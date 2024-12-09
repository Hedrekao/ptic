from collections import defaultdict
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple

import numpy as np
import torch
import torch.nn as nn
import wandb
from tqdm.auto import tqdm

from ml.models.hierarchy_node_model import HierarchyNodeModel
from ml.utils.constants import MODELS_REGISTRY_PATH
from ml.utils.data_loader import PrefetchLoader, create_images_dataloader
from ml.utils.hierarchy import Hierarchy
from ml.utils.logger import create_file_logger


@dataclass
class TrainConfig:
    # train parameters
    epochs: int
    batch_size: int

    # lr parameters
    max_lr: float
    div_factor: float
    final_div_factor: float
    pct_start: float

    # regularization parameters
    grad_clip_value: float
    weight_decay: float
    early_stopping_patience: int
    label_smoothing: float

    optimizer: str

    @property
    def initial_lr(self) -> float:
        return self.max_lr / self.div_factor

    @property
    def min_lr(self) -> float:
        return self.max_lr / self.final_div_factor


def __get_data_loaders(hierarchy: Hierarchy, node_id: str, train_config: TrainConfig, device: torch.device) -> Tuple[PrefetchLoader, PrefetchLoader, int]:
    children = hierarchy.get_children(node_id)
    categories_dict = {child: hierarchy.get_leaf_nodes(
        child) for child in children}

    train_loader = create_images_dataloader(
        categories_dict, split='train', batch_size=train_config.batch_size, device=device)
    val_loader = create_images_dataloader(
        categories_dict, split='val', batch_size=train_config.batch_size, device=device)

    return train_loader, val_loader, len(children)


def __create_optimizer(model: nn.Module, train_config: TrainConfig) -> torch.optim.Optimizer:
    if train_config.optimizer == 'adamw':
        return torch.optim.AdamW(
            model.parameters(),
            lr=train_config.initial_lr,
            weight_decay=train_config.weight_decay
        )
    elif train_config.optimizer == 'adam':
        return torch.optim.Adam(
            model.parameters(),
            lr=train_config.initial_lr
        )
    else:
        raise ValueError(f'Invalid optimizer: {train_config.optimizer}')


class MetricSmoother:
    def __init__(self, window_size: int = 3):
        self.window_size = window_size
        self.values = []

    def update(self, value: float) -> float:
        self.values.append(value)
        if len(self.values) > self.window_size:
            self.values.pop(0)
        return self.get_smoothed()

    def get_smoothed(self) -> float:
        return sum(self.values) / len(self.values)


def get_mixup_alpha(train_acc, val_acc, epoch, total_epochs, grad_norm):
    """Dynamically adjust mixup alpha based on overfitting gap"""
    gap = train_acc - val_acc
    # Adjust alpha based on gradient norm
    if grad_norm < 0.01:  # Very small gradients
        base_alpha = 0.4  # Less mixing to allow bigger steps
    elif grad_norm > 2.0:  # Large gradients
        base_alpha = 0.6  # More mixing for stability
    elif grad_norm > 1.5:
        base_alpha = 0.7
    elif grad_norm > 1.0:
        base_alpha = 0.8
    else:
        base_alpha = 0.6

    # Adjust for accuracy gap
    if gap > 0.15:
        base_alpha *= 1.2

    # Early training adjustment
    if epoch < total_epochs * 0.1:
        return min(1.0, base_alpha * 1.1)
    return base_alpha


def mixup_data(x, y, alpha):
    """Performs mixup on the input and target"""
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1

    batch_size = x.size()[0]
    index = torch.randperm(batch_size)

    mixed_x = lam * x + (1 - lam) * x[index]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam


def get_gradient_norm(model):
    total_norm = 0
    for p in model.parameters():
        if p.grad is not None:
            param_norm = p.grad.data.norm(2)
            total_norm += param_norm.item() ** 2
    return total_norm ** 0.5


def __train_epoch(
    model: nn.Module,
    loader: PrefetchLoader,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.OneCycleLR,
    logger: logging.Logger,
    grad_clip_value: float = 0.5,
    label_smoothing: float = 0.1,
    prev_train_acc: float = 0.0,
    prev_val_acc: float = 0.0,
    epoch: int = 0,
    total_epochs: int = 100,
    avg_grad_norm: float = 0.0
) -> Tuple[float, float, float, float]:

    model.train()
    total_loss = 0
    correct = 0
    total_samples = 0

    alpha = get_mixup_alpha(prev_train_acc, prev_val_acc,
                            epoch, total_epochs, avg_grad_norm)
    logger.info(f"Mixup alpha: {alpha}")

    progress_bar = tqdm(loader, desc='Training')
    grad_norms = []

    criterion = nn.CrossEntropyLoss(label_smoothing=label_smoothing)

    for X_batch, y_batch in progress_bar:
        optimizer.zero_grad()

        mixed_X, y_a, y_b, lam = mixup_data(X_batch, y_batch, alpha)

        y_pred = model(mixed_X)

        loss = lam * criterion(y_pred, y_a) + (1 - lam) * \
            criterion(y_pred, y_b)

        loss.backward()

        grad_norm = get_gradient_norm(model)
        grad_norms.append(grad_norm)

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(
            model.parameters(), grad_clip_value, norm_type=2)

        optimizer.step()
        scheduler.step()

        # Update metrics
        model.eval()
        with torch.no_grad():
            original_outputs = model(X_batch)
            pred = original_outputs.argmax(dim=1)
            correct += (pred == y_batch).sum().item()
        model.train()

        total_samples += y_batch.size(0)
        total_loss += loss.item()

        # Update progress bar
        progress_bar.set_postfix(
            loss=f"{loss.item():.4f}",
            acc=f"{100.0 * correct / total_samples:.2f}%"
        )

    epoch_loss = total_loss / len(loader)
    epoch_acc = correct / total_samples

    avg_grad_norm = np.mean(grad_norms)

    return epoch_loss, epoch_acc, alpha, avg_grad_norm


@torch.no_grad()
def __validate(model: nn.Module, loader: PrefetchLoader) -> Tuple[float, float, float, dict]:
    model.eval()
    total_loss = 0
    correct = 0
    total_samples = 0

    correct_per_class = defaultdict(int)
    total_per_class = defaultdict(int)

    criterion = nn.CrossEntropyLoss()
    progress_bar = tqdm(
        loader, desc='Validation')
    for X_batch, y_batch in progress_bar:
        y_pred = model(X_batch)
        loss = criterion(y_pred, y_batch)

        total_loss += loss.item()
        total_samples += y_batch.size(0)

        # Per-class metrics
        preds = y_pred.argmax(dim=1)
        for pred, label in zip(preds, y_batch):
            label_idx = label.item()
            total_per_class[label_idx] += 1
            if pred == label:
                correct_per_class[label_idx] += 1

        correct += (y_pred.argmax(dim=1) == y_batch).sum().item()

        progress_bar.set_postfix(
            loss=f"{loss.item():.4f}",
            acc=f"{100.0 * correct / total_samples:.2f}%"
        )

    epoch_loss = total_loss / len(loader)
    epoch_acc = correct / total_samples

    class_accuracies = {
        f"val/class_{k}_accuracy": correct_per_class[k] / total_per_class[k] for k in total_per_class.keys()}

    balanced_accuracy = np.mean(list(class_accuracies.values()))

    return epoch_loss, epoch_acc, balanced_accuracy, class_accuracies


def train_singular_model(hierarchy: Hierarchy, node_id: str, train_config: TrainConfig, device_type: str, project_name: str) -> None:

    # init wandb run
    run_name = f"node_{node_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    wandb.init(
        project=f"bachelor-resnet-{project_name}",
        name=run_name,
        config={
            "architecture": "HierarchyNodeModel",
            "epochs": train_config.epochs,
            "batch_size": train_config.batch_size,
            "optimizer": train_config.optimizer,
            "weight_decay": train_config.weight_decay,
            "grad_clip_value": train_config.grad_clip_value,
            "label_smoothing": train_config.label_smoothing,
            "early_stopping_patience": train_config.early_stopping_patience,
            "pct_start": train_config.pct_start,
            "div_factor": train_config.div_factor,
            "final_div_factor": train_config.final_div_factor,
            "max_lr": train_config.max_lr,
            "node_id": node_id,
            "num_classes": None  # Will be set after loading data
        }
    )

    device = torch.device(device_type)

    # Setup data
    train_loader, val_loader, num_classes = __get_data_loaders(
        hierarchy, node_id, train_config, device)

    # Update wandb config
    wandb.config.update({"num_classes": num_classes}, allow_val_change=True)

    # Setup logging
    logger = create_file_logger(f'train_{node_id}.log')
    logger.info(f'Training model for node {node_id}')

    # Create model
    model = HierarchyNodeModel(num_classes=num_classes)
    model.to(device)

    wandb.watch(model, log="all", log_freq=10)

    # Setup training
    optimizer = __create_optimizer(model, train_config)

    # Setup schedulers
    num_steps = len(train_loader) * train_config.epochs
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer,
        max_lr=train_config.max_lr,
        total_steps=num_steps,
        pct_start=train_config.pct_start,
        anneal_strategy='cos',
        div_factor=train_config.div_factor,
        final_div_factor=train_config.final_div_factor,
        three_phase=True
    )
    # Setup validation loss smoother
    val_smoother = MetricSmoother(window_size=5)

    # Training loop
    best_val_loss = float('inf')
    patience = 0

    train_acc = 0.0
    val_acc = 0.0
    avg_grad_norm = 0.0

    for epoch in range(train_config.epochs):
        print(f'\nEpoch {epoch + 1}/{train_config.epochs}')

        # Training phase
        train_loss, train_acc, mixup_alpha, avg_grad_norm = __train_epoch(
            model=model,
            loader=train_loader,
            optimizer=optimizer,
            scheduler=scheduler,
            logger=logger,
            grad_clip_value=train_config.grad_clip_value,
            label_smoothing=train_config.label_smoothing,
            prev_train_acc=train_acc,
            prev_val_acc=val_acc,
            epoch=epoch,
            total_epochs=train_config.epochs,
            avg_grad_norm=avg_grad_norm
        )

        # Validation phase
        val_loss, val_acc, val_balanced_acc, val_class_acc = __validate(
            model, val_loader)
        smoothed_val_loss = val_smoother.update(val_loss)

        # Log metrics to wandb
        wandb.log({
            "epoch": epoch + 1,
            "train/loss": train_loss,
            "train/accuracy": train_acc,
            "val/loss": val_loss,
            "val/accuracy": val_acc,
            "val/balanced_accuracy": val_balanced_acc,
            **val_class_acc,
            "val/smoothed_loss": smoothed_val_loss,
            "metrics/acc_gap": train_acc - val_acc,
            "learning_rate": optimizer.param_groups[0]["lr"],
            "mixup_alpha": mixup_alpha,
            "avg_grad_norm": avg_grad_norm
        })

        # Logging
        logger.info(
            f'Epoch {epoch + 1}: '
            f'Train Loss: {train_loss:.4f}, '
            f'Train Acc: {train_acc:.4f}, '
            f'Val Loss: {val_loss:.4f}, '
            f'Val Acc: {val_acc:.4f}, '
            f"Smoothed Val Loss: {smoothed_val_loss:.4f}, "
            f'Gap: {(train_acc - val_acc):.4f}, '
            f'LR: {optimizer.param_groups[0]["lr"]:.6f}'
        )

        # Model checkpointing
        if smoothed_val_loss < best_val_loss:
            best_val_loss = smoothed_val_loss
            patience = 0
            torch.save(model.state_dict(), os.path.join(
                MODELS_REGISTRY_PATH, f'{node_id}.pth'))
            logger.info(f'Saved new best model with val_loss: {val_loss:.4f}')

            wandb.save(f'{node_id}.pth')
            wandb.run.summary["best_val_loss"] = best_val_loss
            wandb.run.summary["best_val_acc"] = val_acc
        else:
            patience += 1
            if patience >= train_config.early_stopping_patience:
                logger.info('Early stopping triggered')
                wandb.run.summary["early_stopping_epoch"] = epoch + 1
                break

    logger.info('Training completed')
    wandb.finish()

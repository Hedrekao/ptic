from dataclasses import dataclass
from typing import Tuple

import torch
import torch.nn as nn
import wandb
from torch.utils.data import DataLoader
from torch.cuda.amp import GradScaler, autocast
from tqdm.auto import tqdm

from ml.models.HierarchyNodeModel import HierarchyNodeModel
from ml.utils.data_loader import create_images_dataloader
from ml.utils.hierarchy import Hierarchy


# TODO: might config should be split into subparts like optimizer config, model config, scheduler config, use gradient clipping or not
# maybe all the configs should go to config.py
@dataclass
class TrainConfig:
    epochs: int
    batch_size: int
    learning_rate: float
    optimizer: str
    weight_decay: float


def __get_data_loaders(hierarchy: Hierarchy, node_id: str, train_config: TrainConfig) -> Tuple[DataLoader, DataLoader, int]:
    children = hierarchy.get_children(node_id)

    categories_dict = {child: hierarchy.get_leaf_nodes(
        child) for child in children}

    train_loader = create_images_dataloader(
        categories_dict, split='train', batch_size=train_config.batch_size)

    val_loader = create_images_dataloader(
        categories_dict, split='val', batch_size=train_config.batch_size)

    return train_loader, val_loader, len(children)


def __create_optimizer(model: nn.Module, train_config: TrainConfig) -> torch.optim.Optimizer:
    # TODO: might be more optimizers, more hyperparameters
    optimizer = None
    if train_config.optimizer == 'adam':
        optimizer = torch.optim.Adam(
            model.parameters(), lr=train_config.learning_rate)
    elif train_config.optimizer == 'adamw':
        optimizer = torch.optim.AdamW(
            model.parameters(), lr=train_config.learning_rate, weight_decay=train_config.weight_decay)
    elif train_config.optimizer == 'rmsprop':
        optimizer = torch.optim.RMSprop(
            model.parameters(), lr=train_config.learning_rate)
    else:
        raise ValueError(f'Invalid optimizer: {train_config.optimizer}')

    return optimizer


def __train_epoch(model: nn.Module,
                  train_loader: DataLoader,
                  loss_fn: nn.Module,
                  optimizer: torch.optim.Optimizer,
                  scaler: GradScaler,
                  device: str) -> Tuple[float, float]:
    model.train()
    total_loss = 0
    acc = 0
    progress_bar = tqdm(train_loader, desc='Training')

    for X_batch, y_batch in progress_bar:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)

        # TODO: comment multiprecision training to explain what it does
        with autocast(device):
            y_pred = model(X_batch)
            loss = loss_fn(y_pred, y_batch)

        total_loss += loss.item()
        acc += (y_pred.argmax(dim=1) == y_batch).sum().item()

        scaler.scale(loss).backward()

        # gradient clipping for stability
        # TODO: might be an overkill, might be removed
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

        scaler.step(optimizer)
        scaler.update()

        # TODO: might also in future put lr
        progress_bar.set_postfix(loss=loss.item())

    acc /= len(train_loader)
    total_loss /= len(train_loader)

    return total_loss, acc


@torch.no_grad()
def __validate(model: nn.Module, val_loader: DataLoader, loss_fn: nn.Module, device: str) -> Tuple[float, float]:
    model.eval()
    val_acc = 0
    val_loss = 0

    progress_bar = tqdm(val_loader, desc='Validation')
    for X_batch, y_batch in progress_bar:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)

        y_pred = model(X_batch)
        loss = loss_fn(y_pred, y_batch)

        val_loss += loss.item()
        val_acc += (y_pred.argmax(dim=1) == y_batch).sum().item()

        # TODO: might also in future put lr
        progress_bar.set_postfix(loss=loss.item())

    val_acc /= len(val_loader)
    val_loss /= len(val_loader)

    return val_loss, val_acc


def train_singular_model(hierarchy: Hierarchy, node_id: str, train_config: TrainConfig, device: str) -> None:

    train_loader, val_loader, num_classes = __get_data_loaders(
        hierarchy, node_id, train_config)

    model = HierarchyNodeModel(num_classes=num_classes)
    model.to(device)

    # TODO: might be custom hierarchical loss function
    loss_fn = nn.CrossEntropyLoss()

    optimizer = __create_optimizer(model, train_config)

    scaler = GradScaler(device)

    # TODO: we might add a learning rate scheduler like OneCycleLR to have warmup and cooldown periods

    wandb.init(
        project="bachelor-resnet-icaam",
        # track hyperparameters and run metadata
        # TODO: might be more hyperparameters
        config={
            "learning_rate": train_config.learning_rate,
            "epochs": train_config.epochs,
            "batch_size": train_config.batch_size,
            "optimizer": train_config.optimizer,
            "weight_decay": train_config.weight_decay
        }
    )

    best_val_loss = float('inf')
    patience = 0

    for epoch in range(train_config.epochs):
        print(f'Epoch {epoch}/{train_config.epochs}')

        train_loss, acc = __train_epoch(
            model, train_loader, loss_fn, optimizer, scaler, device)

        wandb.log({"train_loss": train_loss,
                  "train_accuracy": acc, "epoch": epoch})

        print(f'Epoch {epoch}, train_loss: {train_loss}, train_accuracy {acc}')

        val_loss, val_acc = __validate(model, val_loader, loss_fn, device)

        # TODO: maybe we can log more metrics like lr, precision, recall, f1-score
        # TODO: maybe we can log all metrics at once
        wandb.log({"val_loss": val_loss, "val_accuracy": val_acc, "epoch": epoch})

        print(
            f'Epoch {epoch}, val_loss: {val_loss}, val_accuracy {val_acc}')

        # TODO: all the early stopping params should be in a config
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience = 0
            torch.save(model.state_dict(), f'model_{node_id}.pth')
            print(f'Best model saved as model_{node_id}.pth')
            wandb.save(f'model_{node_id}.pth')
        else:
            patience += 1
            if patience >= 5:
                print('Early stopping')
                break

    wandb.finish()

    # path for saving the model should be part of constants probably, we should not save to root
    torch.save(model.state_dict(), f'model_{node_id}.pth')
    print(f'Model saved as model_{node_id}.pth')

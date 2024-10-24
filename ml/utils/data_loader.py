import os
import random
from glob import glob
from queue import Queue
from threading import Thread
from typing import Dict, List, Tuple

import torch
from torch.utils.data import DataLoader, Dataset
from torchvision.tv_tensors._image import Image
from torchvision.transforms import v2

from .constants import PROCESSED_IMAGES_PATH

torch.serialization.add_safe_globals([Image])


class ImageDataset(Dataset):
    def __init__(self, root_dir: str, categories: Dict[str, List[str]], split: str = 'train',
                 train_ratio: float = 0.70, val_ratio: float = 0.15):

        self.root_dir = os.path.normpath(root_dir)
        self.categories = categories
        self.split = split

        # Create category to index mapping
        self.cat_mapping = {cat: idx for idx,
                            cat in enumerate(categories.keys())}

        self.train_augmentations = v2.Compose([
            v2.RandomApply(
                [v2.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1)], p=0.3),
            v2.RandomApply(
                [v2.GaussianBlur(kernel_size=(3, 3), sigma=(0.1, 2.0))], p=0.3),
            v2.RandomApply(
                [v2.RandomAdjustSharpness(sharpness_factor=2)], p=0.3),
            v2.RandomApply([v2.RandomErasing(scale=(0.02, 0.15))], p=0.3)
        ])

        self.rebalancing_augmentations = [
            'flip_h',         # Horizontal flip
            'flip_v',         # Vertical flip
            'rot90',          # 90 degree rotation
            'rot180',         # 180 degree rotation
            'rot270',         # 270 degree rotation
            'flip_h_rot90',   # Combine flip and rotation
            'flip_v_rot90',   # Another combination
            'identity'        # No change
        ]

        # Collect all file paths and their categories
        self.samples = []

        n_samples = {}
        for cat, leaves in categories.items():
            n_samples[cat] = 0
            for leaf in leaves:
                cat_dir = os.path.join(self.root_dir, leaf)
                tensor_files = glob(os.path.join(cat_dir, '*.pt'))

                # Generate deterministic train/val/test split
                n_files = len(tensor_files)
                indices = list(range(n_files))

                # Seed random number generator for reproducibility
                random.Random(42).shuffle(indices)

                n_train = int(n_files * train_ratio)
                n_val = int(n_files * val_ratio)

                if split == 'train':
                    selected_indices = indices[:n_train]
                elif split == 'val':
                    selected_indices = indices[n_train:n_train + n_val]
                else:  # test
                    selected_indices = indices[n_train + n_val:]

                n_samples[cat] += len(selected_indices)
                for idx in selected_indices:
                    self.samples.append({
                        'path': tensor_files[idx],
                        'category': cat,
                        'label': self.cat_mapping[cat]
                    })

        # print sample distribution
        # percentage of samples in each category

        total_samples = sum(n_samples.values())

        for cat, n in n_samples.items():
            print(f"{cat}: {n} samples ({n/total_samples:.2%})")

        # Only balance classes for training data
        if split != 'train':
            return

        # Balance classes by creating transformations of underrepresented classes
        max_cat = max(n_samples, key=n_samples.get)
        max_cat_samples = max(n_samples.values())

        # create tmp path for storing transformed tensors
        tmp_dir = os.path.join(self.root_dir, 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)

        # Balance classes by creating transformations
        for cat in self.categories.keys():
            if cat == max_cat:
                print(
                    f"Skipping balanced class {cat}, already has {max_cat_samples} samples")
                continue

            cat_samples = [
                sample for sample in self.samples if sample['category'] == cat]
            n_samples_cat = n_samples[cat]
            while n_samples_cat < max_cat_samples:
                # Select a random sample from the class
                sample = random.choice(cat_samples)
                # Create a random transformation
                tensor = torch.load(sample['path'], weights_only=True)

                transformation_type = random.choice(
                    self.rebalancing_augmentations)
                if transformation_type == 'flip_h':
                    transformed_tensor = torch.flip(
                        tensor, [2])  # Horizontal flip
                elif transformation_type == 'flip_v':
                    transformed_tensor = torch.flip(
                        tensor, [1])  # Vertical flip
                elif transformation_type == 'rot90':
                    transformed_tensor = torch.rot90(tensor, k=1, dims=(1, 2))
                elif transformation_type == 'rot180':
                    transformed_tensor = torch.rot90(tensor, k=2, dims=(1, 2))
                elif transformation_type == 'rot270':
                    transformed_tensor = torch.rot90(tensor, k=3, dims=(1, 2))
                elif transformation_type == 'flip_h_rot90':
                    transformed_tensor = torch.rot90(
                        torch.flip(tensor, [2]), k=1, dims=(1, 2))
                elif transformation_type == 'flip_v_rot90':
                    transformed_tensor = torch.rot90(
                        torch.flip(tensor, [1]), k=1, dims=(1, 2))
                else:  # identity
                    transformed_tensor = tensor

                # Save the transformed tensor to a temporary path
                tmp_path = os.path.join(
                    tmp_dir, f'{n_samples_cat}_{cat}.pt')

                assert transformed_tensor.shape == tensor.shape, \
                    f"Transformed tensor shape {transformed_tensor.shape} does not match original tensor shape {tensor.shape}"

                torch.save(transformed_tensor, tmp_path)

                self.samples.append({
                    'path': tmp_path,
                    'category': cat,
                    'label': self.cat_mapping[cat]
                })

                n_samples_cat += 1

            print(f"Balanced class {cat} to {n_samples_cat} samples")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        sample = self.samples[idx]
        # Load preprocessed tensor
        tensor = torch.load(sample['path'], weights_only=True)

        if self.split == 'train':
            old_shape = tensor.shape
            tensor = self.train_augmentations(tensor)

            assert tensor.shape == old_shape, \
                f"Augmented tensor shape {tensor.shape} does not match original tensor shape {old_shape}"

        return tensor, torch.tensor(sample['label'], dtype=torch.long)


class PrefetchLoader:
    def __init__(self, loader: DataLoader, buffer_size: int = 2, device: torch.device = None, root_dir: str = None):
        self.loader = loader
        self.buffer_size = buffer_size
        self.device = device or torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu')
        self.buffer = Queue(maxsize=buffer_size)
        self.stop_event = None
        self.prefetch_thread = None
        self.root_dir = root_dir
        self._active = False

    def prefetch_worker(self):
        try:
            for batch in self.loader:
                if self.stop_event.is_set():
                    break

                # Move batch to device in the background thread
                if isinstance(batch, (tuple, list)):
                    batch = tuple(t.to(self.device, non_blocking=True)
                                  if isinstance(t, torch.Tensor) else t
                                  for t in batch)
                elif isinstance(batch, dict):
                    batch = {k: v.to(self.device, non_blocking=True)
                             if isinstance(v, torch.Tensor) else v
                             for k, v in batch.items()}
                elif isinstance(batch, torch.Tensor):
                    batch = batch.to(self.device, non_blocking=True)

                self.buffer.put(batch)
        except Exception as e:
            print(f"Prefetch worker error: {e}")
            self.stop_event.set()
        finally:
            self.buffer.put(None)  # Signal end of data
            self._active = False

    def __iter__(self):
        # Clean up previous iteration if necessary
        if self._active:
            self.stop_event.set()
            if self.prefetch_thread is not None:
                self.prefetch_thread.join()
            while not self.buffer.empty():
                self.buffer.get()

        # Start new iteration
        self._active = True
        self.stop_event = torch.multiprocessing.Event()
        self.prefetch_thread = Thread(
            target=self.prefetch_worker,
            daemon=True
        )
        self.prefetch_thread.start()

        while True:
            if self.stop_event.is_set():
                raise RuntimeError("Prefetch worker encountered an error")

            batch = self.buffer.get()
            if batch is None:
                break
            yield batch

    def __len__(self):
        return len(self.loader)

    def __del__(self):
        if self._active:
            self.stop_event.set()
            if self.prefetch_thread is not None:
                self.prefetch_thread.join()

    def remove_tmp_folder(self):
        tmp_dir = os.path.join(self.root_dir, 'tmp')
        for file in os.listdir(tmp_dir):
            os.remove(os.path.join(tmp_dir, file))

        os.rmdir(tmp_dir)


def create_images_dataloader(
    categories: Dict[str, List[str]],
    batch_size: int = 32,
    split: str = 'train',
    num_workers: int = 4,
    n_prefetch_batches: int = 3,
    device: torch.device = None
) -> PrefetchLoader:
    """
    Creates a dataloader with prefetching for the specified categories.

    Args:
        root_dir: Path to processed data directory
        categories: List of category names to include
        batch_size: Batch size
        split: One of 'train', 'val', 'test'
        num_workers: Number of worker processes
        prefetch_factor: Number of batches to prefetch
    """

    dataset = ImageDataset(PROCESSED_IMAGES_PATH, categories, split)

    # Create base DataLoader
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(split == 'train'),
        num_workers=num_workers,
        drop_last=True,
    )

    # Wrap with prefetching
    return PrefetchLoader(loader, buffer_size=n_prefetch_batches, device=device, root_dir=PROCESSED_IMAGES_PATH)

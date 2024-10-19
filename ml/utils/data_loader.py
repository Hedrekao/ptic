import torch
import os
import random
from .constants import PROCESSED_IMAGES_PATH
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple
from queue import Queue
from threading import Thread
from glob import glob
from torchvision.tv_tensors._image import Image

torch.serialization.add_safe_globals([Image])


class ImageDataset(Dataset):
    def __init__(self, root_dir: str, categories: List[str], split: str = 'train',
                 train_ratio: float = 0.70, val_ratio: float = 0.15):

        self.root_dir = os.path.normpath(root_dir)
        self.categories = categories
        self.split = split

        # Create category to index mapping
        self.cat_mapping = {cat: idx for idx, cat in enumerate(categories)}

        # Collect all file paths and their categories
        self.samples = []
        for cat in categories:
            cat_dir = os.path.join(self.root_dir, cat)
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

            for idx in selected_indices:
                self.samples.append({
                    'path': tensor_files[idx],
                    'category': cat,
                    'label': self.cat_mapping[cat]
                })

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        sample = self.samples[idx]
        # Load preprocessed tensor
        tensor = torch.load(sample['path'], weights_only=True)
        return tensor, torch.tensor(sample['label'], dtype=torch.long)


class PrefetchLoader:
    def __init__(self, loader: DataLoader, buffer_size: int = 2):
        self.loader = loader
        self.buffer_size = buffer_size
        self.buffer = Queue(maxsize=buffer_size)
        self.stop_event = None
        self.prefetch_thread = None

    def prefetch_worker(self):
        try:
            for batch in self.loader:
                if self.stop_event.is_set():
                    break
                self.buffer.put(batch)
            self.buffer.put(None)  # Signal end of data
        except Exception as e:
            print(f"Prefetch worker error: {e}")
            self.stop_event.set()
            self.buffer.put(None)

    def __iter__(self):
        self.stop_event = torch.multiprocessing.Event()
        self.prefetch_thread = Thread(
            target=self.prefetch_worker,
            daemon=True
        )
        self.prefetch_thread.start()

        while True:
            batch = self.buffer.get()
            if batch is None:
                break
            yield batch

    def __len__(self):
        return len(self.loader)


def create_images_dataloader(
    categories: List[str],
    batch_size: int = 32,
    split: str = 'train',
    num_workers: int = 4,
    n_prefetch_batches: int = 2
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
    return PrefetchLoader(loader, buffer_size=n_prefetch_batches)

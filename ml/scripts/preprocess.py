import json
import shutil
import os
from typing import Optional

import click
import pandas as pd
import torch
import torchvision.transforms.v2 as v2
from PIL import Image

from ml.utils.constants import DATA_DIR, PROCESSED_IMAGES_PATH, RAW_IMAGES_PATH
from ml.utils.image_statistics import get_images_statistics, print_statistics


def RGBA2RGB(img: torch.Tensor) -> torch.Tensor:
    if img.shape[0] == 4:
        rgb = img[:3]
        alpha = img[3]
        bg = torch.ones_like(rgb) * (1 - alpha)
        return rgb * alpha + bg

    return img


def LA2RGB(img: torch.Tensor) -> torch.Tensor:
    if img.shape[0] == 2:  # LA format
        luminance, alpha = img[0], img[1]
        # Convert to RGB by repeating the luminance channel
        rgb = luminance.unsqueeze(0).repeat(3, 1, 1)
        bg = torch.ones_like(rgb) * (1 - alpha)
        return rgb * alpha + bg
    return img


def create_transform_pipeline(min_size: tuple, dataset_mean: list, dataset_std: list):

    return v2.Compose([
        v2.ToImage(),
        v2.Resize(min_size),
        v2.Lambda(LA2RGB),
        v2.RGB(),
        v2.Lambda(RGBA2RGB),
        v2.ToDtype(torch.float32, scale=True),
        v2.Normalize(
            mean=dataset_mean,
            std=dataset_std
        )
    ])


@click.command()
@click.option("--min-size", "-m", "min_size_threshold", type=int)
@click.option("--n-product", "-np", "n_products_threshold", type=int, required=False, default=5)
@click.option("--hierarchy", "-h", "hierarchy_path", type=str, required=False)
def preprocess_images(min_size_threshold: int, n_products_threshold: int = 5,  hierarchy_path: Optional[str] = None):

    statistics = get_images_statistics(min_size_threshold)
    print_statistics(statistics)

    __preprocess_images(
        statistics["min_size"], statistics["corrupted_files"], statistics["files_below_min_size"], statistics["dataset_mean"], statistics["dataset_std"])

    __remove_unusable_categories(n_products_threshold)

    if hierarchy_path is not None:
        __preprocess_hierarchy(hierarchy_path)


def __preprocess_images(min_size: tuple, corrupted_files: set, file_below_min_size: set, dataset_mean: list, dataset_std: list):

    transform = create_transform_pipeline(min_size, dataset_mean, dataset_std)

    for class_name in os.listdir(RAW_IMAGES_PATH):
        base_save_path = os.path.join(PROCESSED_IMAGES_PATH, class_name)
        os.makedirs(base_save_path, exist_ok=True)
        for img_name in os.listdir(os.path.join(RAW_IMAGES_PATH, class_name)):

            raw_path = os.path.join(RAW_IMAGES_PATH, class_name, img_name)

            if raw_path in corrupted_files or raw_path in file_below_min_size:
                continue

            img_name = img_name.split(".")[0] + ".pt"
            save_path = os.path.join(base_save_path, img_name)

            try:
                tensor = transform(Image.open(raw_path))
            except OSError:
                print(f"Error processing {raw_path}")
                continue

            assert tensor.shape == (
                3, min_size[0], min_size[1]), f"All images should have the same shape. Got {tensor.shape}"

            torch.save(tensor, save_path)

        print(f"Finished processing {class_name}")

    with open(os.path.join(DATA_DIR, 'config.json'), 'w') as f:
        json.dump({
            "min_size": [min_size[0], min_size[1]],
            "mean": dataset_mean,
            "std": dataset_std}, f)


# removing categories with less than n images
# the minimal number of images is dependent on the dataset split
# in case we have 70, 15, 15 split we should have at least 7 images per category
# so that at least one image from category will be present in each split
def __remove_unusable_categories(n_images_threshold: int = 5):
    count = 0
    categories = os.listdir(PROCESSED_IMAGES_PATH)
    for class_name in categories:
        if len(os.listdir(os.path.join(PROCESSED_IMAGES_PATH, class_name))) < n_images_threshold:
            shutil.rmtree(os.path.join(PROCESSED_IMAGES_PATH, class_name))
            count += 1

    print(f"Removed {count} categories")
    print("Categories left: ", len(categories) - count)


# trimming hierarchical tree file to only contain relevant information for training
# (we only need paths to categories that there are actually images for)
def __preprocess_hierarchy(hierarchy_path: str):
    hierarchy_path = os.path.normpath(hierarchy_path)
    hierarchy_df = pd.read_csv(hierarchy_path)
    categories = os.listdir(PROCESSED_IMAGES_PATH)

    start_categories = hierarchy_df.shape[0]

    # mask for nodes that their ids are not in the categories list and not in parent id column
    mask = ~hierarchy_df["<ID>"].isin(categories) & ~hierarchy_df["<ID>"].isin(
        hierarchy_df["<Parent ID>"].unique())

    while mask.any():
        hierarchy_df = hierarchy_df[~mask]
        mask = ~hierarchy_df["<ID>"].isin(categories) & ~hierarchy_df["<ID>"].isin(
            hierarchy_df["<Parent ID>"].unique())

    end_categories = hierarchy_df.shape[0]
    print(f"Removed {start_categories - end_categories} from hierarchy file")
    print(f"{end_categories} left in hierarchical tree")

    hierarchy_df.to_csv(os.path.join(
        DATA_DIR, 'processed_hierarchy.csv'), index=False)


if __name__ == "__main__":
    preprocess_images()

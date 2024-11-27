import os
import json
import click
import torch
import torchvision.transforms.v2 as v2
from ml.utils.image_statistics import get_images_statistics, print_statistics
from ml.utils.constants import DATA_DIR, RAW_IMAGES_PATH, PROCESSED_IMAGES_PATH
from PIL import Image


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


def create_transform_pipeline(min_size: tuple):

    return v2.Compose([
        v2.ToImage(),
        v2.Resize(min_size),
        v2.Lambda(LA2RGB),
        v2.RGB(),
        v2.Lambda(RGBA2RGB),
        v2.ToDtype(torch.float32, scale=True),
        v2.Normalize(
            mean=[0.4529, 0.4129, 0.3755],
            std=[0.2829, 0.2726, 0.2763]
        )
    ])


@click.command()
@click.option("--min-size", "-m", "min_size_threshold", type=int)
def preprocess_images(min_size_threshold: int):

    statistics = get_images_statistics(min_size_threshold)
    print_statistics(statistics)

    __preprocess_images(
        statistics["min_size"], statistics["corrupted_files"], statistics["files_below_min_size"])


def __preprocess_images(min_size: tuple, corrupted_files: set, file_below_min_size: set):

    transform = create_transform_pipeline(min_size)

    for class_name in os.listdir(RAW_IMAGES_PATH):
        base_save_path = os.path.join(PROCESSED_IMAGES_PATH, class_name)
        os.makedirs(base_save_path, exist_ok=True)
        for img_name in os.listdir(os.path.join(RAW_IMAGES_PATH, class_name)):

            raw_path = os.path.join(RAW_IMAGES_PATH, class_name, img_name)

            if raw_path in corrupted_files or raw_path in file_below_min_size:
                continue

            img_name = img_name.split(".")[0] + ".pt"
            save_path = os.path.join(base_save_path, img_name)

            tensor = transform(Image.open(raw_path))

            assert tensor.shape == (
                3, min_size[0], min_size[1]), f"All images should have the same shape. Got {tensor.shape}"

            torch.save(tensor, save_path)

        print(f"Finished processing {class_name}")

    with open(os.path.join(DATA_DIR, 'config.json'), 'w') as f:
        json.dump({"min_size": [min_size[0], min_size[1]]}, f)


if __name__ == "__main__":
    preprocess_images()

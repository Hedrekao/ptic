import os
import click
import torch
import torchvision.transforms.v2 as v2
from image_statistics import get_images_statistics, print_statistics
from constants import RAW_IMAGES_PATH, PROCESSED_IMAGES_PATH
from PIL import Image


@click.command()
@click.option("--min-size", "-m", "min_size_threshold", type=int)
def preprocess_images(min_size_threshold: int):

    statistics = get_images_statistics(min_size_threshold)
    print_statistics(statistics)

    __preprocess_images(
        statistics["min_size"], statistics["corrupted_files"], statistics["files_below_min_size"])


def __preprocess_images(min_size: tuple, corrupted_files: set, file_below_min_size: set):

    # TODO: do small research about normalization of values in tensor instead of just [0,1]
    transform = v2.Compose([
        v2.ToImage(),
        v2.Resize(min_size),
        v2.ToDtype(torch.float32, scale=True)
    ])

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

            torch.save(tensor, save_path)

        print(f"Finished processing {class_name}")


if __name__ == "__main__":
    preprocess_images()

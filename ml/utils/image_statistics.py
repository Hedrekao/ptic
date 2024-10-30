import os
import numpy as np
from PIL import Image, UnidentifiedImageError
from .constants import RAW_IMAGES_PATH


def get_images_statistics(min_size_threshold: int) -> dict:

    min_size = (np.inf, np.inf)
    corrupted_files = set()
    file_below_min_size = set()
    smallest_file = ""
    total_files = 0

    for class_name in os.listdir(RAW_IMAGES_PATH):
        for img_name in os.listdir(os.path.join(RAW_IMAGES_PATH, class_name)):
            try:
                total_files += 1
                img = Image.open(os.path.join(
                    RAW_IMAGES_PATH, class_name, img_name))
                img_size = img.size

                if img_size[0] >= min_size_threshold and img_size[1] >= min_size_threshold:
                    if img_size[0] < min_size[0] and img_size[1] < min_size[1]:
                        min_size = img_size
                        smallest_file = os.path.join(
                            RAW_IMAGES_PATH, class_name, img_name)
                else:
                    file_below_min_size.add(os.path.join(
                        RAW_IMAGES_PATH, class_name, img_name))

            except UnidentifiedImageError:
                # if we cannot open the file, we skip it and also mark it as corrupted
                corrupted_files.add(os.path.join(
                    RAW_IMAGES_PATH, class_name, img_name))

    return {
        "min_size": min_size,
        "smallest_file": smallest_file,
        "corrupted_files": corrupted_files,
        "files_below_min_size": file_below_min_size,
        "total_files": total_files,
    }


def print_statistics(statistics: dict):
    print("Minimum image size: ", statistics["min_size"])
    print("Total number of files: ", statistics["total_files"])
    print("Number of files below minimum size: ",
          len(statistics["files_below_min_size"]))
    print("Files below minumum size threshold ratio: ",
          len(statistics["files_below_min_size"]) / statistics["total_files"])
    print("Number of corrupted files: ", len(statistics["corrupted_files"]))
    print("Corrupted ratio: ", len(
        statistics["corrupted_files"]) / statistics["total_files"])
    print("Smallest file: ", statistics["smallest_file"])

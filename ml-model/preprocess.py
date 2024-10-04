import os
import numpy as np

from PIL import Image, UnidentifiedImageError

base_path = "raw_images"


def preprocess_images():

    min_size, smallest_file, corrupted_files = __find_min_image_size()

    print("Minimum image size: ", min_size)
    print("Number of corrupted files: ", len(corrupted_files))
    print("Smallest file: ", smallest_file)


def __find_min_image_size():

    min_size = (np.inf, np.inf)
    corrupted_files = []
    smallest_file = ""
    total_min_size = np.inf

    for class_name in os.listdir(base_path):
        for img_name in os.listdir(os.path.join(base_path, class_name)):
            try:
                img = Image.open(os.path.join(base_path, class_name, img_name))
                img_size = img.size
                min_size = (min(min_size[0], img_size[0]),
                            min(min_size[1], img_size[1]))
                if img_size[0] * img_size[1] < total_min_size:
                    total_min_size = img_size[0] * img_size[1]
                    smallest_file = os.path.join(
                        base_path, class_name, img_name)
            except UnidentifiedImageError:
                # if we cannot open the file, we skip it and also mark it as corrupted
                corrupted_files.append(os.path.join(
                    base_path, class_name, img_name))

    return min_size, smallest_file, corrupted_files


if __name__ == "__main__":
    preprocess_images()

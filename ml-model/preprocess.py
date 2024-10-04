import click

from statistics import get_images_statistics, print_statistics


@click.command()
@click.option("--min-size", "-m", "min_size_threshold", type=int)
def preprocess_images(min_size_threshold: int):

    statistics = get_images_statistics(min_size_threshold)
    print_statistics(statistics)


if __name__ == "__main__":
    preprocess_images()

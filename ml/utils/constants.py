import os

DATA_DIR = "./ml/data"
RAW_IMAGES_PATH = "./ml/data/raw_images"
PROCESSED_IMAGES_PATH = "./ml/data/processed_images"
HIERARCHY_FILE_PATH = "./ml/data/hierarchy.csv"

MODELS_REGISTRY_PATH = "/content/drive/MyDrive/bach/models_registry" if os.getenv(
    "TRAINING_ENV", "LOCAL") == "GOOGLE_COLAB" else "./ml/models_registry"

CONFIGS_PATH = "./ml/data/configs"

LOG_DIR = "./ml/logs"

import torch
import json
import os
import numpy as np
from glob import glob
from PIL import Image
from ml.models import HierarchyNodeModel
from ml.utils.constants import MODELS_REGISTRY_PATH
from ml.utils.hierarchy import Hierarchy


class HierachyModel:
    def __init__(self):
        self.models = {}
        self.metadata = {}
        self.hierarchy = Hierarchy()
        self.hierarchy_mask = np.load(
            os.path.join(MODELS_REGISTRY_PATH, "hierarchy_mask.npy"))

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        self.__load_metadata()
        self.__load_models()

    def __load_metadata(self):
        metadata_files = glob(os.path.join(MODELS_REGISTRY_PATH, "*.json"))

        for file in metadata_files:
            file_name = os.path.split(file)[-1].split(".")[0]

            with open(file, "r") as f:
                model_metadata = json.load(f)
                self.metadata[file_name] = model_metadata

    def __load_models(self):

        model_files = glob(os.path.join(MODELS_REGISTRY_PATH, "*.pth"))
        self.models = {}

        for file in model_files:
            file_name = os.path.split(file)[-1].split(".")[0]
            model_metadata = self.metadata[file_name]
            n_classes = model_metadata["n_classes"]

            model = HierarchyNodeModel(
                n_classes).to(self.device)

            model.load_state_dict(torch.load(
                file, map_location=self.device, weights_only=True))

            self.models[file_name] = model

    def predict(self, image: Image):
        pass

import torch
import json
import os
import numpy as np
import torch.nn.functional as F
from glob import glob
from PIL import Image
from ml.models import HierarchyNodeModel
from ml.scripts.preprocess import create_transform_pipeline
from ml.utils.constants import DATA_DIR, MODELS_REGISTRY_PATH
from ml.utils.hierarchy import Hierarchy


class HierarchyModel:
    def __init__(self, hierarchy: Hierarchy):
        self.models = {}
        self.metadata = {}
        self.hierarchy = hierarchy
        self.hierarchy_mask = np.load(
            os.path.join(MODELS_REGISTRY_PATH, "hierarchy_mask.npy"))
        self.config = json.load(
            open(os.path.join(DATA_DIR, "config.json"), "r"))

        self.transform_pipeline = create_transform_pipeline(
            (self.config["min_size"][0], self.config["min_size"][1]),
            self.config["mean"],
            self.config["std"]
        )

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        self.__load_metadata()
        self.__load_models()

    def __load_metadata(self):
        metadata_files = glob(os.path.join(MODELS_REGISTRY_PATH, "*.json"))

        for file in metadata_files:
            file_name = os.path.splitext(os.path.split(file)[-1])[0]

            with open(file, "r") as f:
                model_metadata = json.load(f)
                self.metadata[file_name] = model_metadata

    def __load_models(self):

        model_files = glob(os.path.join(MODELS_REGISTRY_PATH, "*.pth"))
        self.models = {}

        for file in model_files:
            file_name = os.path.splitext(os.path.split(file)[-1])[0]
            model_metadata = self.metadata[file_name]
            n_classes = model_metadata["n_classes"]

            model = HierarchyNodeModel(
                n_classes).to(self.device)

            model.load_state_dict(torch.load(
                file, map_location=self.device, weights_only=True))

            self.models[file_name] = model

    def transform_image(self, image: Image):
        return self.transform_pipeline(image)

    def predict(self, tensor: torch.Tensor):

        tensor = tensor.to(self.device)

        root_node = self.hierarchy.get_root_id()
        preds = []

        queue = [root_node]

        batch_size = tensor.shape[0]
        while len(queue) > 0:

            node = queue.pop(0)
            model_metadata = self.metadata[node]

            is_single_label = model_metadata["is_single_label"]

            children = self.hierarchy.get_non_leaf_children(node)

            if is_single_label:
                output = np.ones((batch_size, 1))
            else:
                model = self.models[node]
                model.eval()

                with torch.no_grad():
                    output = model(tensor)
                    output = F.softmax(output, dim=-1).cpu().numpy()

            preds.append(output)

            queue.extend(children)

        all_probs = np.concatenate(preds, axis=1)

        log_probs = np.log(all_probs + 1e-10)

        leaf_probs = np.exp(log_probs @ self.hierarchy_mask.T)

        # normalize leaf probabilities
        leaf_probs /= leaf_probs.sum(axis=1, keepdims=True)

        return leaf_probs

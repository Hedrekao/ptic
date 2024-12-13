import json
import os
import sys
from glob import glob
from typing import Optional

import numpy as np
import torch

from ml.scripts.train_single import TrainConfig, train_singular_model
from ml.utils.constants import CONFIGS_PATH, MODELS_REGISTRY_PATH
from ml.utils.hierarchy import Hierarchy


class ModelMetadata:
    def __init__(self, model_name: str, n_classes: int, children: list) -> None:
        self.model_name = model_name
        self.n_classes = n_classes
        self.is_single_label = False
        self.children = children

    def save(self):
        path = os.path.join(MODELS_REGISTRY_PATH, f"{self.model_name}.json")

        result = {
            "n_classes": self.n_classes,
            "is_single_label": self.is_single_label,
            "children": self.children,
        }

        with open(path, "w") as f:
            json.dump(result, f)


def train_hierarchy(project_name: str, hierarchy_file_path: Optional[str] = None):
    device_type = "cpu"

    if torch.cuda.is_available():
        device_type = "cuda"
    elif torch.backends.mps.is_available():
        device_type = "mps"

    # prepare dir for saving models
    os.makedirs(MODELS_REGISTRY_PATH, exist_ok=True)

    # decide whether we should start training from scratch or resume training
    model_files = [os.path.splitext(os.path.split(path)[-1])[0] for path in glob(
        os.path.join(MODELS_REGISTRY_PATH, "*.pth"))]

    hierarchy = Hierarchy(hierarchy_file_path)
    available_configs = os.listdir(CONFIGS_PATH)
    queue = []
    root_id = hierarchy.get_root_id()
    queue.append(root_id)

    if len(model_files) == 0:
        print("Starting training from scratch")
    else:
        not_trained_node = None
        while len(queue) > 0:
            node = queue.pop(0)
            if node not in model_files:
                not_trained_node = node
                break
            children = hierarchy.get_children(node)
            queue.extend(children)

        if not_trained_node is None:
            print("All nodes are already trained")
            return
        else:
            start_node = hierarchy.get_parent(
                not_trained_node) if not_trained_node != root_id else not_trained_node
            queue = [start_node]
            print("Resuming training from node: ", queue[0])

    # bfs traversal for training internal hierarchy nodes
    while len(queue) > 0:
        node_id = queue.pop(0)
        children = hierarchy.get_children(node_id)

        queue.extend(children)

        if len(children) == 0 or node_id in model_files:
            continue

        print(f"Training node {node_id}")

        metadata = ModelMetadata(node_id, len(children), children)

        if len(children) == 1:
            metadata.is_single_label = True
        else:
            config_name = node_id if f"{node_id}.json" in available_configs else "default"
            config_json = json.load(
                open(os.path.join(CONFIGS_PATH, f"{config_name}.json")))
            train_config = TrainConfig(**config_json)
            train_singular_model(hierarchy, node_id,
                                 train_config, device_type, project_name)

        metadata.save()
        print(f"Finished training node {node_id}")

    print("Creating hierarchy mask matrix")
    hierarchy_mask = hierarchy.create_matrix_mask()

    np.save(os.path.join(MODELS_REGISTRY_PATH,
            "hierarchy_mask.npy"), hierarchy_mask)

    print("Finished training hierarchy")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(
            "Usage: python train_hierarchy.py <project_name> [hierarchy_file_path]")
        exit(1)

    project_name = sys.argv[1]
    hierarchy_file_path = None
    if len(sys.argv) == 3:
        hierarchy_file_path = sys.argv[2]

    train_hierarchy(project_name, hierarchy_file_path)

import os
import torch
import json
import numpy as np

from glob import glob
from ml.scripts.train_single import TrainConfig, train_singular_model
from ml.utils.constants import MODELS_REGISTRY_PATH
from ml.utils.hierarchy import Hierarchy


class ModelMetadata:
    def __init__(self, model_name: str, n_classes: int) -> None:
        self.model_name = model_name
        self.n_classes = n_classes
        self.is_single_label = False

    def save(self):
        path = os.path.join(MODELS_REGISTRY_PATH, f"{self.model_name}.json")

        result = {
            "n_classes": self.n_classes,
            "is_single_label": self.is_single_label
        }

        with open(path, "w") as f:
            json.dump(result, f)


def train_hierarchy():
    device_type = "cpu"

    if torch.cuda.is_available():
        device_type = "cuda"
    elif torch.backends.mps.is_available():
        device_type = "mps"

    train_config = TrainConfig(
        epochs=150,
        batch_size=16,
        max_lr=1.2e-3,
        div_factor=15.0,
        final_div_factor=100.0,
        pct_start=0.4,
        weight_decay=0.1,
        grad_clip_value=0.4,
        label_smoothing=0.1,
        early_stopping_patience=30,
        optimizer="adamw",
    )

    # prepare dir for saving models
    os.makedirs(MODELS_REGISTRY_PATH, exist_ok=True)

    # decide whether we should start training from scratch or resume training
    model_files = [os.path.split(path)[1].split('.')[0] for path in glob(
        os.path.join(MODELS_REGISTRY_PATH, "*.pth"))]

    hierarchy = Hierarchy()
    queue = []

    if len(model_files) == 0:
        print("Starting training from scratch")
        root_id = hierarchy.get_root_id()
        queue.append(root_id)
    else:
        model_files.sort()
        last_trained_node = model_files[-1]
        parent = hierarchy.get_parent(last_trained_node)
        if parent is None:
            queue.append(last_trained_node)
        else:
            queue.append(parent)

        print("Resuming training from node ", queue[0])

    # bfs traversal for training internal hierarchy nodes
    while len(queue) > 0:
        node_id = queue.pop(0)
        children = hierarchy.get_children(node_id)

        queue.extend(children)

        if len(children) == 0 or node_id in model_files:
            continue

        print(f"Training node {node_id}")

        metadata = ModelMetadata(node_id, len(children))

        if len(children) == 1:
            metadata.is_single_label = True
        else:
            train_singular_model(hierarchy, node_id, train_config, device_type)

        metadata.save()
        print(f"Finished training node {node_id}")

    print("Creating hierarchy mask matrix")
    hierarchy_mask = hierarchy.create_matrix_mask()

    np.save(os.path.join(MODELS_REGISTRY_PATH,
            "hierarchy_mask.npy"), hierarchy_mask)

    print("Finished training hierarchy")


train_hierarchy()
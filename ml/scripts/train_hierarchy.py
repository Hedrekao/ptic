import os
import torch
import json
import numpy as np

from glob import glob
from ml.scripts.train_single import TrainConfig, train_singular_model
from ml.utils.constants import MODELS_REGISTRY_PATH
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
            train_singular_model(hierarchy, node_id, train_config, device_type)

        metadata.save()
        print(f"Finished training node {node_id}")

    print("Creating hierarchy mask matrix")
    hierarchy_mask = hierarchy.create_matrix_mask()

    np.save(os.path.join(MODELS_REGISTRY_PATH,
            "hierarchy_mask.npy"), hierarchy_mask)

    print("Finished training hierarchy")


train_hierarchy()

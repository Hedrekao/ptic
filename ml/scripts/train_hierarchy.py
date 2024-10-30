import torch

from ml.scripts.train_single import TrainConfig, train_singular_model
from ml.utils.hierarchy import Hierarchy


def train_hierarchy():
    hierarchy = Hierarchy()
    root_id = hierarchy.get_root_id()
    queue = [root_id]

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

    while len(queue) > 0:
        node_id = queue.pop(0)
        children = hierarchy.get_children(node_id)

        queue.extend(children)

        print(f"Training node {node_id}")
        train_singular_model(hierarchy, node_id, train_config, device_type)
        print(f"Finished training node {node_id}")

    print("Finished training hierarchy")

import torch
from ml.models import HierarchyModel
from ml.utils.data_loader import create_images_dataloader
from ml.utils.hierarchy import Hierarchy
from tqdm.auto import tqdm


def evaluate_model():
    hierarchy = Hierarchy()

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    model = HierarchyModel(hierarchy=hierarchy)

    categories = {
        cat: [cat] for cat in hierarchy.get_leaf_nodes(hierarchy.get_root_id())
    }

    dataloader = create_images_dataloader(
        categories,
        batch_size=16,
        split="test",
        device=device
    )

    top1_acc = 0
    top3_acc = 0
    top5_acc = 0

    n_samples = len(dataloader) * 16

    progress_bar = tqdm(dataloader, desc="Evaluating model")

    for batch in progress_bar:
        tensors, labels = batch
        probs = model.predict(tensors)

        _, top5_indices = torch.topk(torch.tensor(probs), 5, dim=1)

        top1_acc += (top5_indices[:, 0] == labels).sum().item()
        top3_acc += (top5_indices[:, :3] ==
                     labels.unsqueeze(1)).any(dim=1).sum().item()

        top5_acc += (top5_indices == labels.unsqueeze(1)
                     ).any(dim=1).sum().item()

    top1_acc /= n_samples

    top3_acc /= n_samples

    top5_acc /= n_samples

    return {
        "top1_acc": f"{top1_acc:.2f}",
        "top3_acc": f"{top3_acc:.2f}",
        "top5_acc": f"{top5_acc:.2f}"
    }

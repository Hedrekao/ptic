import torch
from ml.models import HierarchyModel
from ml.utils.data_loader import create_images_dataloader
from ml.utils.hierarchy import Hierarchy
from tqdm.auto import tqdm


@torch.no_grad()
def evaluate_model():
    hierarchy = Hierarchy()

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    model = HierarchyModel(hierarchy=hierarchy)

    categories = {}

    # create a dict with leaf categories in an bfs order that was used during training and creating hierarchy mask
    queue = [hierarchy.get_root_id()]

    while queue:
        node_id = queue.pop(0)

        if hierarchy.is_leaf(node_id):
            categories[node_id] = [node_id]
        else:
            queue.extend(hierarchy.get_children(node_id))

    dataloader = create_images_dataloader(
        categories,
        batch_size=16,
        split="test",
        device=device
    )

    top1_acc = 0
    top3_acc = 0
    top5_acc = 0

    category_accuracy = {cat: {"top1": 0, "top3": 0,
                               "top5": 0, "count": 0} for cat in categories}

    n_samples = len(dataloader) * 16

    progress_bar = tqdm(dataloader, desc="Evaluating model")

    for batch in progress_bar:
        tensors, labels = batch

        leaf_probs = model.predict(tensors)

        _, top5_indices = torch.topk(torch.tensor(leaf_probs), 5, dim=1)

        top1_acc += (top5_indices[:, 0] == labels).sum().item()
        top3_acc += (top5_indices[:, :3] ==
                     labels.unsqueeze(1)).any(dim=1).sum().item()
        top5_acc += (top5_indices == labels.unsqueeze(1)
                     ).any(dim=1).sum().item()

        for i, cat in enumerate(categories):
            # Create a mask for samples belonging to this category
            category_mask = (labels == i)

            # Count the number of samples in this category for averaging later
            sum_of_labels = category_mask.sum().item()

            if sum_of_labels == 0:
                continue

            category_accuracy[cat]["count"] += sum_of_labels

            # Category-specific accuracy calculations
            cat_labels = labels[category_mask]
            cat_top5 = top5_indices[category_mask]

            category_accuracy[cat]["top1"] += (cat_top5[:, 0]
                                               == cat_labels).sum().item()
            category_accuracy[cat]["top3"] += (cat_top5[:, :3] ==
                                               cat_labels.unsqueeze(1)).any(dim=1).sum().item()
            category_accuracy[cat]["top5"] += (cat_top5 ==
                                               cat_labels.unsqueeze(1)).any(dim=1).sum().item()

    top1_acc /= n_samples

    top3_acc /= n_samples

    top5_acc /= n_samples

    category_acc = {
        cat: {
            "top1": round((category_accuracy[cat]["top1"] / category_accuracy[cat]["count"]), 2)
            if category_accuracy[cat]["count"] > 0 else 0,
            "top3": round((category_accuracy[cat]["top3"] / category_accuracy[cat]["count"]), 2)
            if category_accuracy[cat]["count"] > 0 else 0,
            "top5": round((category_accuracy[cat]["top5"] / category_accuracy[cat]["count"]), 2)
            if category_accuracy[cat]["count"] > 0 else 0
        }
        for cat in categories
    }

    return {
        "top1": f"{top1_acc:.2f}",
        "top3": f"{top3_acc:.2f}",
        "top5": f"{top5_acc:.2f}",
        "category_acc": category_acc,
    }


if __name__ == "__main__":
    print(evaluate_model())

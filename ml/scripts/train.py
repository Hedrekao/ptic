from ml.utils.data_loader import create_images_dataloader
from ml.utils.hierarchy import Hierarchy


def train_singular_model(hierarchy: Hierarchy, node_id: str):

    children = hierarchy.get_children(node_id)

    categories_dict = {child: hierarchy.get_leaf_nodes(
        child) for child in children}

    data_loader = create_images_dataloader(categories_dict, split='train')

    # TODO: Placeholder for actual model
    # model = Model()

    # TODO: training loop
    # for epoch in range(epochs):

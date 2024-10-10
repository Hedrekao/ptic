import pandas as pd


class Hierarchy():
    def __init__(self, path: str):
        self.hierarchy: pd.DataFrame = pd.read_csv(path)

    def get_children(self, parent_id: str):

        children = self.hierarchy[self.hierarchy["parent_id"] == parent_id]

        return children["id"].tolist()

    def get_leaf_nodes(self, root_id: str):
        """
        Recursively get all leaf nodes ids under a given root node
        """

        children = self.get_children(root_id)

        if not children:
            return [root_id]

        leaf_nodes = []

        for child in children:
            leaf_nodes.extend(self.get_leaf_nodes(child))

        return leaf_nodes

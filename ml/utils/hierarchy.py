import pandas as pd
from typing import List, Optional
from .constants import HIERARCHY_FILE_PATH


class Hierarchy():
    def __init__(self, path: Optional[str]):
        if path is None:
            path = HIERARCHY_FILE_PATH
        self.hierarchy: pd.DataFrame = pd.read_csv(path)

    def get_root_id(self):
        root_node = self.hierarchy[self.hierarchy["parent_id"].isnull()]

        return root_node["id"].values[0]

    def get_children(self, parent_id: str):

        children = self.hierarchy[self.hierarchy["parent_id"] == parent_id]

        return children["id"].tolist()

    def get_leaf_nodes(self, root_id: str) -> List[str]:
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

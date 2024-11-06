import pandas as pd
import numpy as np
import graphviz
from typing import List, Optional
from .constants import DATA_DIR, HIERARCHY_FILE_PATH


class Hierarchy():
    def __init__(self, path: Optional[str] = None):
        if path is None:
            path = HIERARCHY_FILE_PATH
        self.hierarchy: pd.DataFrame = pd.read_csv(path)

    def get_root_id(self):
        root_node = self.hierarchy[self.hierarchy["parent_id"].isnull()]

        return root_node["id"].values[0]

    def get_parent(self, child_id: str):
        parent = self.hierarchy.loc[self.hierarchy["id"]
                                    == child_id, 'parent_id'].values

        if len(parent) == 0 or pd.isna(parent[0]):
            return None

        return parent[0]

    def get_children(self, parent_id: str):

        children = self.hierarchy.loc[self.hierarchy["parent_id"] == parent_id,
                                      'id'].values
        children.sort()

        return children.tolist()

    def is_leaf(self, node_id: str):
        return len(self.get_children(node_id)) == 0

    def get_non_leaf_children(self, parent_id: str):
        children = self.get_children(parent_id)

        return [child for child in children if not self.is_leaf(child)]

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

        leaf_nodes.sort()

        return leaf_nodes

    def draw_tree(self):

        dot = graphviz.Digraph(comment='Hierarchy')

        # Configure graph attributes for better visualization
        dot.attr(rankdir='TB')  # Top to Bottom layout
        dot.attr('node', shape='box')
        dot.attr('node', style='rounded')
        dot.attr('graph', fontsize='12')
        dot.attr('edge', color='#666666')

        # Add nodes with formatted labels
        for _, row in self.hierarchy.iterrows():
            # Format label to show both ID and name
            id = row['id']
            children = self.get_children(id)

            # color leaf nodes differently
            if len(children) > 0:
                fillcolor = '#E6F3FF'
            else:
                fillcolor = '#E6FFE6'

            dot.node(id, id, fillcolor=fillcolor,
                     style='filled,rounded')

        # Add edges
        for _, row in self.hierarchy.iterrows():
            if not pd.isna(row['parent_id']):
                dot.edge(row['parent_id'], row['id'])

        dot.render("hierarchy_tree", DATA_DIR, format='png', cleanup=True)

    def create_matrix_mask(self):

        edges = []  # List of (parent_id, child_id) tuples
        leaf_nodes = []
        edge_to_col_idx = {}  # Map (parent, child) -> column index

        root_id = self.get_root_id()

        queue = [root_id]

        while len(queue) > 0:
            current_node_id = queue.pop(0)

            children = self.get_children(current_node_id)

            if len(children) == 0:
                leaf_nodes.append(current_node_id)

            for child_id in children:
                edges.append((current_node_id, child_id))
                edge_to_col_idx[(current_node_id, child_id)] = len(edges) - 1
                queue.append(child_id)

        # Create the mask matrix
        n_leaves = len(leaf_nodes)
        n_edges = len(edge_to_col_idx)
        mask_matrix = np.zeros((n_leaves, n_edges), dtype=np.float32)

        for row_idx, leaf_id in enumerate(leaf_nodes):
            current_node_id = leaf_id
            while True:

                parent_id = self.get_parent(current_node_id)

                if parent_id is None:  # Reached root
                    break

                # Mark the edge in the mask
                edge = (parent_id, current_node_id)
                col_idx = edge_to_col_idx[edge]
                mask_matrix[row_idx, col_idx] = 1.0
                current_node_id = parent_id

        return mask_matrix

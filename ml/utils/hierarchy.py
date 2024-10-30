import pandas as pd
from typing import List, Optional
from .constants import HIERARCHY_FILE_PATH


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

        if len(parent) == 0:
            return None

        return parent[0]

    def get_children(self, parent_id: str):

        children = self.hierarchy.loc[self.hierarchy["parent_id"] == parent_id,
                                      'id'].values
        children.sort()

        return children.tolist()

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

    def draw_hierarchy(self):

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

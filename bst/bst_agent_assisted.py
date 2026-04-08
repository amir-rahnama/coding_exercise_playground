"""BST with parent pointers — iterative insert, compact nodes, top-down print."""

from __future__ import annotations


class Node:
    __slots__ = ("value", "parent", "left_child", "right_child")

    def __init__(self, value: float, parent: Node | None = None) -> None:
        self.value = value
        self.parent = parent
        self.left_child: Node | None = None
        self.right_child: Node | None = None


class BinarySearchTree:
    def __init__(self) -> None:
        self.root: Node | None = None

    def insert(self, values: list[float]) -> None:
        """Insert every element in *values* (order preserved). Empty list is a no-op."""
        for v in values:
            self.insert_one(v)

    def insert_one(self, value: float) -> None:
        """Insert a single value. Smaller → left; greater or equal → right (duplicates on the right)."""
        new = Node(value)
        if self.root is None:
            self.root = new
            return

        node = self.root
        while node is not None:
            go_left = value < node.value
            nxt = node.left_child if go_left else node.right_child
            if nxt is None:
                new.parent = node
                if go_left:
                    node.left_child = new
                else:
                    node.right_child = new
                return
            node = nxt

    def print_tree(self, node: Node | None = None) -> None:
        """Print a top-down ASCII tree (stdout)."""
        if node is None:
            node = self.root
        if node is None:
            print("(empty tree)")
            return
        print(node.value)
        kids = [c for c in (node.left_child, node.right_child) if c is not None]
        for i, child in enumerate(kids):
            _print_branch(child, "", i == len(kids) - 1)


def _print_branch(node: Node, prefix: str, is_last: bool) -> None:
    connector = "└── " if is_last else "├── "
    print(f"{prefix}{connector}{node.value}")
    extension = prefix + ("    " if is_last else "│   ")
    kids = [c for c in (node.left_child, node.right_child) if c is not None]
    for i, child in enumerate(kids):
        _print_branch(child, extension, i == len(kids) - 1)


if __name__ == "__main__":
    sample = [10, 5, 15, 3, 7, 12, 18]
    tree = BinarySearchTree()
    tree.insert(sample)
    print(f"Inserting values: {sample}\n")
    tree.print_tree()

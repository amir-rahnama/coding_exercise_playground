"""BST built from a list with iterative insert (O(1) extra space while descending)."""


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val: int) -> None:
        self.val = val
        self.left: Node | None = None
        self.right: Node | None = None


class BinarySearchTree:
    """Binary search tree: smaller values left, greater-or-equal right."""

    def __init__(self, values: list[int] | None = None) -> None:
        self.root: Node | None = None
        if values:
            for v in values:
                self.insert(v)

    def insert(self, val: int) -> None:
        new = Node(val)
        if self.root is None:
            self.root = new
            return

        node = self.root
        while node is not None:
            go_left = val < node.val
            next_node = node.left if go_left else node.right
            if next_node is None:
                if go_left:
                    node.left = new
                else:
                    node.right = new
                return
            node = next_node

    def show(self) -> None:
        _print_ascii_tree(self.root)


def _children_in_order(node: Node) -> list[Node]:
    """Left then right, skipping missing children (keeps drawing order stable)."""
    return [c for c in (node.left, node.right) if c is not None]


def _print_ascii_tree(root: Node | None) -> None:
    if root is None:
        print("(empty tree)")
        return

    print(root.val)
    kids = _children_in_order(root)
    for i, child in enumerate(kids):
        _print_branch(child, "", i == len(kids) - 1)


def _print_branch(node: Node, prefix: str, is_last: bool) -> None:
    connector = "└── " if is_last else "├── "
    print(f"{prefix}{connector}{node.val}")
    extension = prefix + ("    " if is_last else "│   ")
    kids = _children_in_order(node)
    for i, child in enumerate(kids):
        _print_branch(child, extension, i == len(kids) - 1)


if __name__ == "__main__":
    sample = [10, 5, 15, 3, 7, 12, 18]
    tree = BinarySearchTree(sample)
    print(f"BST from {sample}:\n")
    tree.show()

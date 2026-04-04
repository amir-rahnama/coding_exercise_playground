"""Binary search tree built from a list, with a simple terminal visualization."""


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val: int) -> None:
        self.val = val
        self.left: Node | None = None
        self.right: Node | None = None


class BinarySearchTree:
    def __init__(self, values: list[int] | None = None) -> None:
        self.root: Node | None = None
        if values:
            for x in values:
                self.insert(x)

    def insert(self, val: int) -> None:
        self.root = self._insert_recursive(self.root, val)

    @staticmethod
    def _insert_recursive(node: Node | None, val: int) -> Node:
        if node is None:
            return Node(val)
        if val < node.val:
            node.left = BinarySearchTree._insert_recursive(node.left, val)
        else:
            node.right = BinarySearchTree._insert_recursive(node.right, val)
        return node

    def show(self) -> None:
        """Print an ASCII tree to stdout (your terminal / prompt)."""
        if self.root is None:
            print("(empty tree)")
            return
        print(self.root.val)
        if self.root.left and self.root.right:
            self._print_subtree(self.root.left, "", False)
            self._print_subtree(self.root.right, "", True)
        elif self.root.left:
            self._print_subtree(self.root.left, "", True)
        elif self.root.right:
            self._print_subtree(self.root.right, "", True)

    @staticmethod
    def _print_subtree(node: Node, prefix: str, is_last: bool) -> None:
        branch = "└── " if is_last else "├── "
        print(f"{prefix}{branch}{node.val}")
        child_prefix = prefix + ("    " if is_last else "│   ")
        left, right = node.left, node.right
        if left and right:
            BinarySearchTree._print_subtree(left, child_prefix, False)
            BinarySearchTree._print_subtree(right, child_prefix, True)
        elif left:
            BinarySearchTree._print_subtree(left, child_prefix, True)
        elif right:
            BinarySearchTree._print_subtree(right, child_prefix, True)


def bts_tree(values: list[int]) -> BinarySearchTree:
    """Build a BST from *values*, print it, and return the tree instance."""
    tree = BinarySearchTree(values)
    tree.show()
    return tree


if __name__ == "__main__":
    bts_tree([10, 5, 15, 3, 7, 12, 18])

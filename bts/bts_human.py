from typing import List, Optional

class Node: 
    def __init__(self, value: float, 
        parent: Optional["Node"] = None, 
        left_child: Optional["Node"] = None, 
        right_child: Optional["Node"] = None) -> None:
        self.value = value
        self.parent = parent
        self.left_child = left_child
        self.right_child = right_child

class BinarySearchTree: 
    def __init__(self) -> None:
        self.root : Optional[Node] = None
    
    def insert(self, values: list[float]) -> None:
        if self.root is None:
            self.root = Node(values[0], None, None, None)
        for value in values[1:]:
                self.insert_recursive(self.root, value)

    def insert_recursive(self, node: Node, value: float) -> None:
        if value < node.value: 
            if node.left_child is None:
                node.left_child = Node(value, node, None, None)
                return
            else:
                self.insert_recursive(node.left_child, value)
        elif value > node.value:
            if node.right_child is None:
                node.right_child = Node(value, node, None, None)
                return
            else:
                self.insert_recursive(node.right_child, value)
    def print_tree(self, node: Optional[Node] = None, prefix: str = "", is_left: bool = True):
        if node is None:
            node = self.root
        if node is None:
            return

        # print right subtree first
        if node.right_child is not None:
            self.print_tree(node.right_child, prefix + ("│   " if is_left else "    "), False)

        # print current node
        print(prefix + ("└── " if is_left else "┌── ") + str(node.value))

        # print left subtree
        if node.left_child is not None:
            self.print_tree(node.left_child, prefix + ("    " if is_left else "│   "), True)
        
if __name__ == "__main__":
    example = BinarySearchTree()
    example.insert([10, 5, 15, 3, 7, 12, 18])
    print("Inserting values: [10, 5, 15, 3, 7, 12, 18]")
    example.print_tree()

    
        
from anytree import AnyNode
from parser import Parser
from typing import cast

class Transformation:
    pre     : AnyNode # a^2 + b^2
    post    : AnyNode # c^2
    id      : int

    def __init__(self, equality : str):
        equalitylist = equality.split("=")
        assert len(equalitylist) == 2

        self.pre, self.post = cast(list[AnyNode], Parser().parse_from_txt(equalitylist))
       


    def apply(self, tree:AnyNode) -> tuple[AnyNode, bool]:
        """Will apply the given transformation to the tree

        Args:
            tree (AnyNode): must be a valid formula tree

        Raises:
            NotImplementedError: must be implemented by all child classes

        Returns:
            tuple[AnyNode, bool]: will return the tree and if the change worked
        """
        # apply changes
        if not self.checkRequirements(tree): return tree, False
        raise NotImplementedError()
    
    def checkRequirements(self, tree:AnyNode):
        return (
            tree.is_root
            # ...
        )

class Axiom(Transformation):
    name : str

class Deduction(Transformation):
    history: list[int]
from anytree import AnyNode, PreOrderIter
from parser import Parser
from typing import cast
from elements import Constant, Variable, Function, Expression, Placeholder

class Transformation:
    pre             : AnyNode # a^2 + b^2
    post            : AnyNode # c^2
    id              : int
    placeholders    : dict[str, AnyNode]
    safe            : bool

    def __init__(self, equality : str):
        equalitylist = equality.split("=")
        assert len(equalitylist) == 2

        self.pre, self.post = cast(list[AnyNode], Parser().parse_from_txt(equalitylist))

        # replace all variables in post with Placeholders
        for element in PreOrderIter(self.post):
            if isinstance(element, Variable):
                element = Placeholder(str(element)) # Replaces all variables with Placeholders of the same Id

    def apply(self, tree:AnyNode) -> tuple[bool, AnyNode]:
        """Will check if the transformation is applicable. If yes, Will apply the given transformation to the root of tree.

        Args:
            tree (AnyNode): must be a valid formula tree

        Raises:
            NotImplementedError: must be implemented by all child classes

        Returns:
            tuple[AnyNode, bool]: will return the tree and if the change worked
        """
        out, placeholders = self._compare_trees(tree, self.pre, {})
        post = self.post # make copy so we don't modify attribute
        if out: # If it worked
            for node in PreOrderIter(post):
                if isinstance(node.element, Placeholder):
                    if str(node.element) not in placeholders:
                        raise KeyError("didn't work") # should NEVER occur. TODO remove after testing

                    node = placeholders[str(node.element)]
            return True, post
        return  False, tree
    

    def _trees_equal(self, a: AnyNode, b: AnyNode) -> bool:                      
        """Check if two trees are exactly equal (elements and structure)."""     
        if a.element != b.element:                                               
            return False                                                         
        if len(a.children) != len(b.children):                                   
            return False                                                         
        return all(self._trees_equal(ac, bc) for ac, bc in zip(a.children, b.children))                                                                           
                                                                             
    def _compare_trees(self, tree: AnyNode, sample: AnyNode, placeholders: dict[str, AnyNode]) -> tuple[bool, dict[str,AnyNode]]: 
        for tree_child, sample_child in zip(tree.children, sample.children):
            # Placeholders must be leaf nodes.                              
            if isinstance(sample_child.element, Placeholder):               
                ph_key = str(sample_child.element)                          
                if ph_key not in placeholders:                              
                    placeholders[ph_key] = tree_child                       
                else:                                                       
                    # placeholder already filled — tree must exactly match the stored subtree                                                           
                    if not self._trees_equal(tree_child, placeholders[ph_key]):
                        return False, placeholders                          
                continue    

            # Not a placeholder in sample tree
            out, placeholders = self._compare_trees(tree_child, sample_child, placeholders)
            if not out:
                return False, placeholders
        
        return True, placeholders





class Axiom(Transformation):

    name : str

class Deduction(Transformation):
    history: list[int]
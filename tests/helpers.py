from anytree import AnyNode


def leaf(element):
    """Create a childless AnyNode."""
    return AnyNode(name=str(element), element=element)


def node(element, children):
    """Create an AnyNode with children."""
    return AnyNode(name=str(element), element=element, children=children)

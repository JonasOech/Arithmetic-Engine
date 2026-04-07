import pytest
from anytree import AnyNode
from parser import Parser
from transformation import Transformation
from elements import Constant, Variable, Expression, Placeholder
from tests.helpers import leaf, node


@pytest.fixture
def t():
    return Transformation("a + b = c")


class TestCompareTreesLeaves:

    def test_identical_leaves(self, t):
        tree = leaf(Variable("x1"))
        sample = leaf(Variable("x1"))
        result, ph = t._compare_trees(tree, sample, {})
        assert result is True
        assert ph == {}

    def test_different_leaves(self, t):
        tree = leaf(Variable("x1"))
        sample = leaf(Variable("x2"))
        result, ph = t._compare_trees(tree, sample, {})
        assert result is True


class TestCompareTreesStructure:

    def test_matching_binary_expression(self, t, parser):
        tree = parser.parse_from_txt("x1 + x2")
        sample = parser.parse_from_txt("x1 + x2")
        result, ph = t._compare_trees(tree, sample, {})
        assert result is True
        assert ph == {}

    def test_matching_nested_expression(self, t, parser):
        tree = parser.parse_from_txt("( x1 + x2 ) * x3")
        sample = parser.parse_from_txt("( x1 + x2 ) * x3")
        result, ph = t._compare_trees(tree, sample, {})
        assert result is True

    def test_deeply_nested_match(self, t, parser):
        tree = parser.parse_from_txt("( x1 + x2 ) * ( x3 + x4 )")
        sample = parser.parse_from_txt("( x1 + x2 ) * ( x3 + x4 )")
        result, ph = t._compare_trees(tree, sample, {})
        assert result is True


class TestCompareTreesPlaceholder:

    def test_single_placeholder(self, t):
        """A placeholder matches any subtree."""
        tree = node(Expression("+"), [leaf(Variable("x1")), leaf(Variable("x2"))])
        sample = node(Expression("+"), [leaf(Placeholder("a")), leaf(Variable("x2"))])
        result, ph = t._compare_trees(tree, sample, {})
        assert result is True
        assert "a" in ph

    def test_placeholder_stores_tree_child(self, t):
        x1 = leaf(Variable("x1"))
        tree = node(Expression("+"), [x1, leaf(Variable("x2"))])
        sample = node(Expression("+"), [leaf(Placeholder("a")), leaf(Variable("x2"))])
        result, ph = t._compare_trees(tree, sample, {})
        assert ph["a"] is x1

    def test_all_children_checked_after_placeholder(self, t):
        """A placeholder in the first child should not prevent checking the second child."""
        inner_tree = node(Expression("+"), [leaf(Variable("x1")), leaf(Variable("x2"))])
        inner_sample = node(Expression("+"), [leaf(Placeholder("a")), leaf(Variable("x2"))])
        # Wrap so both children are checked at the outer level too
        tree = node(Expression("*"), [inner_tree, leaf(Variable("x3"))])
        sample = node(Expression("*"), [inner_sample, leaf(Variable("x3"))])
        result, ph = t._compare_trees(tree, sample, {})
        assert result is True
        assert "a" in ph

    def test_two_different_placeholders(self, t):
        tree = node(Expression("+"), [leaf(Variable("x1")), leaf(Variable("x2"))])
        sample = node(Expression("+"), [leaf(Placeholder("a")), leaf(Placeholder("b"))])
        result, ph = t._compare_trees(tree, sample, {})
        assert result is True
        assert "a" in ph
        assert "b" in ph

    def test_same_placeholder_twice_matching(self, t):
        """Same placeholder used twice — both subtrees must match."""
        tree = node(Expression("+"), [leaf(Variable("x1")), leaf(Variable("x1"))])
        sample = node(Expression("+"), [leaf(Placeholder("a")), leaf(Placeholder("a"))])
        result, ph = t._compare_trees(tree, sample, {})
        assert result is True

    def test_same_placeholder_twice_mismatching(self, t):
        """Same placeholder used twice with different subtrees — should fail."""
        tree = node(Expression("+"), [leaf(Variable("x1")), leaf(Variable("x2"))])
        sample = node(Expression("+"), [leaf(Placeholder("a")), leaf(Placeholder("a"))])
        result, ph = t._compare_trees(tree, sample, {})
        assert result is False

    def test_placeholder_matches_complex_subtree(self, t):
        subtree = node(Expression("*"), [leaf(Variable("x1")), leaf(Variable("x2"))])
        tree = node(Expression("+"), [subtree, leaf(Constant(1))])
        sample = node(Expression("+"), [leaf(Placeholder("a")), leaf(Constant(1))])
        result, ph = t._compare_trees(tree, sample, {})
        assert result is True
        assert ph["a"] is subtree

    def test_seen_placeholder_mismatching_subtree(self, t):
        """Pre-populated placeholder with a different structure — should fail."""
        tree = node(Expression("+"), [leaf(Variable("x1")), leaf(Variable("x2"))])
        sample = node(Expression("+"), [leaf(Placeholder("a")), leaf(Variable("x2"))])
        stored = node(Expression("*"), [leaf(Constant(1)), leaf(Constant(2))])
        result, ph = t._compare_trees(tree, sample, {"a": stored})
        assert result is False


class TestCompareTreesWithParser:

    def test_simple_addition(self, t, parser):
        tree = parser.parse_from_txt("x1 + x2")
        sample = parser.parse_from_txt("x1 + x2")
        result, _ = t._compare_trees(tree, sample, {})
        assert result is True

    def test_exponentiation(self, t, parser):
        tree = parser.parse_from_txt("x1 ^ x2")
        sample = parser.parse_from_txt("x1 ^ x2")
        result, _ = t._compare_trees(tree, sample, {})
        assert result is True

    def test_function_application(self, t, parser):
        tree = parser.parse_from_txt("sin ( x1 )")
        sample = parser.parse_from_txt("sin ( x1 )")
        result, _ = t._compare_trees(tree, sample, {})
        assert result is True

    def test_complex_expression(self, t, parser):
        tree = parser.parse_from_txt("x1 ^ 2 + x2 ^ 2")
        sample = parser.parse_from_txt("x1 ^ 2 + x2 ^ 2")
        result, _ = t._compare_trees(tree, sample, {})
        assert result is True

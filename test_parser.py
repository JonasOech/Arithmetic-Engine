import pytest
from anytree import AnyNode, RenderTree, PreOrderIter, PostOrderIter, LevelOrderIter
from anytree.search import findall, find_by_attr
from parser import Parser
from elements import Constant, Variable, Expression, Function


@pytest.fixture
def p():
    return Parser()


def names(node: AnyNode) -> str:
    """Return a flat string of node names via pre-order traversal."""
    result = node.name  # type: ignore
    for child in node.children:
        result += " " + names(child)
    return result


def child_names(node: AnyNode) -> list[str]:
    return [c.name for c in node.children]


# ── _classify_element ────────────────────────────────────────────────

class TestClassifyElement:
    def test_variable_x1(self, p):
        assert isinstance(p._classify_element("x1"), Variable)

    def test_variable_x99(self, p):
        assert isinstance(p._classify_element("x99"), Variable)

    def test_variable_x0(self, p):
        assert isinstance(p._classify_element("x0"), Variable)
    
    def test_variable_a(self, p):
        assert isinstance(p._classify_element("a"), Variable)

    def test_variable_z(self, p):
        assert isinstance(p._classify_element("z"), Variable)

    def test_constant_integer(self, p):
        assert isinstance(p._classify_element("42"), Constant)

    def test_constant_zero(self, p):
        assert isinstance(p._classify_element("0"), Constant)

    def test_constant_large(self, p):
        assert isinstance(p._classify_element("999999"), Constant)

    def test_expression_plus(self, p):
        assert isinstance(p._classify_element("+"), Expression)

    def test_expression_minus(self, p):
        assert isinstance(p._classify_element("-"), Expression)

    def test_expression_mul(self, p):
        assert isinstance(p._classify_element("*"), Expression)

    def test_expression_div(self, p):
        assert isinstance(p._classify_element("/"), Expression)

    def test_expression_exp(self, p):
        assert isinstance(p._classify_element("^"), Expression)

    def test_expression_lparen(self, p):
        assert isinstance(p._classify_element("("), Expression)

    def test_expression_rparen(self, p):
        assert isinstance(p._classify_element(")"), Expression)

    def test_function_sin(self, p):
        assert isinstance(p._classify_element("sin"), Function)

    def test_function_cos(self, p):
        assert isinstance(p._classify_element("cos"), Function)

    def test_function_log(self, p):
        assert isinstance(p._classify_element("log"), Function)


# ── Simple binary operations ─────────────────────────────────────────

class TestSimpleBinary:
    def test_addition(self, p):
        tree = p.parse_from_txt("x1 + x2")
        assert tree.name == "+"
        assert child_names(tree) == ["x1", "x2"]

    def test_subtraction(self, p):
        tree = p.parse_from_txt("x1 - x2")
        assert tree.name == "-"
        assert child_names(tree) == ["x1", "x2"]

    def test_multiplication(self, p):
        tree = p.parse_from_txt("x1 * x2")
        assert tree.name == "*"
        assert child_names(tree) == ["x1", "x2"]

    def test_division(self, p):
        tree = p.parse_from_txt("x1 / x2")
        assert tree.name == "/"
        assert child_names(tree) == ["x1", "x2"]

    def test_exponentiation(self, p):
        tree = p.parse_from_txt("x1 ^ x2")
        assert tree.name == "^"
        assert child_names(tree) == ["x1", "x2"]

    def test_add_constants(self, p):
        tree = p.parse_from_txt("3 + 5")
        assert tree.name == "+"
        assert child_names(tree) == ["3", "5"]

    def test_mul_constants(self, p):
        tree = p.parse_from_txt("7 * 2")
        assert tree.name == "*"
        assert child_names(tree) == ["7", "2"]

    def test_mixed_var_const_add(self, p):
        tree = p.parse_from_txt("x1 + 5")
        assert tree.name == "+"
        assert child_names(tree) == ["x1", "5"]

    def test_mixed_const_var_mul(self, p):
        tree = p.parse_from_txt("3 * x2")
        assert tree.name == "*"
        assert child_names(tree) == ["3", "x2"]

    def test_sub_constants(self, p):
        tree = p.parse_from_txt("10 - 4")
        assert tree.name == "-"
        assert child_names(tree) == ["10", "4"]


# ── Operator precedence ──────────────────────────────────────────────

class TestPrecedence:
    def test_mul_before_add(self, p):
        tree = p.parse_from_txt("x1 + x2 * x3")
        assert tree.name == "+"
        assert tree.children[1].name == "*"

    def test_mul_before_sub(self, p):
        tree = p.parse_from_txt("x1 - x2 * x3")
        assert tree.name == "-"
        assert tree.children[1].name == "*"

    def test_div_before_add(self, p):
        tree = p.parse_from_txt("x1 + x2 / x3")
        assert tree.name == "+"
        assert tree.children[1].name == "/"

    def test_exp_before_mul(self, p):
        tree = p.parse_from_txt("x1 * x2 ^ x3")
        assert tree.name == "*"
        assert tree.children[1].name == "^"

    def test_exp_before_add(self, p):
        tree = p.parse_from_txt("x1 + x2 ^ x3")
        assert tree.name == "+"
        assert tree.children[1].name == "^"

    def test_add_left_assoc(self, p):
        tree = p.parse_from_txt("x1 + x2 + x3")
        assert tree.name == "+"
        assert tree.children[0].name == "+"
        assert child_names(tree.children[0]) == ["x1", "x2"]
        assert tree.children[1].name == "x3"

    def test_sub_left_assoc(self, p):
        tree = p.parse_from_txt("x1 - x2 - x3")
        assert tree.name == "-"
        assert tree.children[0].name == "-"

    def test_mul_left_assoc(self, p):
        tree = p.parse_from_txt("x1 * x2 * x3")
        assert tree.name == "*"
        assert tree.children[0].name == "*"

    def test_exp_right_assoc(self, p):
        # x1 ^ x2 ^ x3 should be x1 ^ (x2 ^ x3)
        tree = p.parse_from_txt("x1 ^ x2 ^ x3")
        assert tree.name == "^"
        assert tree.children[0].name == "x1"
        assert tree.children[1].name == "^"

    def test_full_precedence_chain(self, p):
        # x1 + x2 * x3 ^ x4
        tree = p.parse_from_txt("x1 + x2 * x3 ^ x4")
        assert tree.name == "+"
        assert tree.children[1].name == "*"
        assert tree.children[1].children[1].name == "^"


# ── Parentheses ──────────────────────────────────────────────────────

class TestParentheses:
    def test_parens_override_precedence(self, p):
        tree = p.parse_from_txt("( x1 + x2 ) * x3")
        assert tree.name == "*"
        assert tree.children[0].name == "+"

    def test_parens_right_side(self, p):
        tree = p.parse_from_txt("x1 * ( x2 + x3 )")
        assert tree.name == "*"
        assert tree.children[1].name == "+"

    def test_nested_parens(self, p):
        tree = p.parse_from_txt("( ( x1 + x2 ) )")
        assert tree.name == "+"
        assert child_names(tree) == ["x1", "x2"]

    def test_parens_around_single_var(self, p):
        tree = p.parse_from_txt("( x1 )")
        assert tree.name == "x1"

    def test_parens_around_single_const(self, p):
        tree = p.parse_from_txt("( 5 )")
        assert tree.name == "5"

    def test_parens_with_exp(self, p):
        tree = p.parse_from_txt("( x1 + x2 ) ^ x3")
        assert tree.name == "^"
        assert tree.children[0].name == "+"

    def test_double_parens_mul(self, p):
        tree = p.parse_from_txt("( x1 + x2 ) * ( x3 + x4 )")
        assert tree.name == "*"
        assert tree.children[0].name == "+"
        assert tree.children[1].name == "+"

    def test_parens_sub(self, p):
        tree = p.parse_from_txt("x1 - ( x2 + x3 )")
        assert tree.name == "-"
        assert tree.children[1].name == "+"

    def test_parens_nested_deep(self, p):
        tree = p.parse_from_txt("( ( ( x1 ) ) )")
        assert tree.name == "x1"

    def test_parens_mul_add(self, p):
        tree = p.parse_from_txt("( x1 * x2 ) + x3")
        assert tree.name == "+"
        assert tree.children[0].name == "*"


# ── Functions ────────────────────────────────────────────────────────

class TestFunctions:
    def test_sin(self, p):
        tree = p.parse_from_txt("sin ( x1 )")
        assert tree.name == "sin"
        assert child_names(tree) == ["x1"]

    def test_cos(self, p):
        tree = p.parse_from_txt("cos ( x1 )")
        assert tree.name == "cos"
        assert child_names(tree) == ["x1"]

    def test_log(self, p):
        tree = p.parse_from_txt("log ( x1 )")
        assert tree.name == "log"
        assert child_names(tree) == ["x1"]

    def test_function_of_constant(self, p):
        tree = p.parse_from_txt("sin ( 5 )")
        assert tree.name == "sin"
        assert child_names(tree) == ["5"]

    def test_function_plus_var(self, p):
        tree = p.parse_from_txt("sin ( x1 ) + x2")
        assert tree.name == "+"
        assert tree.children[0].name == "sin"
        assert tree.children[1].name == "x2"

    def test_function_times_var(self, p):
        tree = p.parse_from_txt("cos ( x1 ) * x2")
        assert tree.name == "*"
        assert tree.children[0].name == "cos"

    def test_var_times_function(self, p):
        tree = p.parse_from_txt("x1 * sin ( x2 )")
        assert tree.name == "*"
        assert tree.children[1].name == "sin"

    def test_function_of_expr(self, p):
        tree = p.parse_from_txt("sin ( x1 + x2 )")
        assert tree.name == "sin"
        assert tree.children[0].name == "+"

    def test_function_exp(self, p):
        tree = p.parse_from_txt("exp ( x1 )")
        assert tree.name == "exp"
        assert child_names(tree) == ["x1"]

    def test_function_tan(self, p):
        tree = p.parse_from_txt("tan ( x1 )")
        assert tree.name == "tan"
        assert child_names(tree) == ["x1"]


# ── Implicit multiplication ─────────────────────────────────────────

class TestImplicitMultiplication:
    def test_two_vars(self, p):
        tree = p.parse_from_txt("x1 x2")
        assert tree.name == "*"
        assert child_names(tree) == ["x1", "x2"]

    def test_three_vars(self, p):
        tree = p.parse_from_txt("x1 x2 x3")
        assert tree.name == "*"
        # left-associative: (x1*x2)*x3
        assert tree.children[0].name == "*"
        assert tree.children[1].name == "x3"

    def test_const_var(self, p):
        tree = p.parse_from_txt("3 x1")
        assert tree.name == "*"
        assert child_names(tree) == ["3", "x1"]

    def test_implicit_mul_with_add(self, p):
        tree = p.parse_from_txt("x1 x2 + x3")
        assert tree.name == "+"
        assert tree.children[0].name == "*"

    def test_implicit_mul_two_consts(self, p):
        tree = p.parse_from_txt("2 3")
        assert tree.name == "*"
        assert child_names(tree) == ["2", "3"]


# ── Single elements ──────────────────────────────────────────────────

class TestSingleElement:
    def test_single_variable(self, p):
        tree = p.parse_from_txt("x1")
        assert tree.name == "x1"
        assert tree.children == tuple()

    def test_single_constant(self, p):
        tree = p.parse_from_txt("42")
        assert tree.name == "42"
        assert tree.children == tuple()

    def test_single_zero(self, p):
        tree = p.parse_from_txt("0")
        assert tree.name == "0"


# ── Complex expressions ─────────────────────────────────────────────

class TestComplex:
    def test_three_adds(self, p):
        tree = p.parse_from_txt("x1 + x2 + x3 + x4")
        # left-associative: ((x1+x2)+x3)+x4
        assert tree.name == "+"
        assert tree.children[1].name == "x4"

    def test_mixed_add_mul(self, p):
        tree = p.parse_from_txt("x1 * x2 + x3 * x4")
        assert tree.name == "+"
        assert tree.children[0].name == "*"
        assert tree.children[1].name == "*"

    def test_nested_function_in_expr(self, p):
        tree = p.parse_from_txt("x1 + sin ( x2 ) * x3")
        assert tree.name == "+"
        assert tree.children[1].name == "*"
        assert tree.children[1].children[0].name == "sin"

    def test_exp_in_parens(self, p):
        tree = p.parse_from_txt("( x1 ^ x2 ) + x3")
        assert tree.name == "+"
        assert tree.children[0].name == "^"

    def test_chained_mul_div(self, p):
        tree = p.parse_from_txt("x1 * x2 / x3")
        assert tree.name == "/"
        assert tree.children[0].name == "*"

    def test_div_then_mul(self, p):
        tree = p.parse_from_txt("x1 / x2 * x3")
        assert tree.name == "*"
        assert tree.children[0].name == "/"

    def test_complex_parens_and_ops(self, p):
        tree = p.parse_from_txt("( x1 + x2 ) * ( x3 - x4 )")
        assert tree.name == "*"
        assert tree.children[0].name == "+"
        assert tree.children[1].name == "-"

    def test_function_in_parens(self, p):
        tree = p.parse_from_txt("( sin ( x1 ) )")
        assert tree.name == "sin"

    def test_add_sub_chain(self, p):
        tree = p.parse_from_txt("x1 + x2 - x3")
        assert tree.name == "-"
        assert tree.children[0].name == "+"

    def test_sub_add_chain(self, p):
        tree = p.parse_from_txt("x1 - x2 + x3")
        assert tree.name == "+"
        assert tree.children[0].name == "-"

    def test_mul_exp_add(self, p):
        tree = p.parse_from_txt("x1 * x2 ^ x3 + x4")
        assert tree.name == "+"
        assert tree.children[0].name == "*"
        assert tree.children[0].children[1].name == "^"

    def test_function_squared(self, p):
        tree = p.parse_from_txt("sin ( x1 ) ^ 2")
        assert tree.name == "^"
        assert tree.children[0].name == "sin"
        assert tree.children[1].name == "2"

    def test_two_functions_added(self, p):
        tree = p.parse_from_txt("sin ( x1 ) + cos ( x2 )")
        assert tree.name == "+"
        assert tree.children[0].name == "sin"
        assert tree.children[1].name == "cos"

    def test_two_functions_multiplied(self, p):
        tree = p.parse_from_txt("sin ( x1 ) * cos ( x2 )")
        assert tree.name == "*"
        assert tree.children[0].name == "sin"
        assert tree.children[1].name == "cos"

    def test_deep_nesting(self, p):
        tree = p.parse_from_txt("( ( x1 + x2 ) * x3 )")
        assert tree.name == "*"
        assert tree.children[0].name == "+"

    def test_all_ops(self, p):
        tree = p.parse_from_txt("x1 + x2 - x3 * x4 / x5")
        # * and / bind tighter, left-assoc among +/-
        assert tree.name == "-"
        assert tree.children[0].name == "+"

    def test_const_arithmetic(self, p):
        tree = p.parse_from_txt("1 + 2 * 3")
        assert tree.name == "+"
        assert tree.children[1].name == "*"

    def test_exp_chain_three(self, p):
        # right-associative: x1 ^ (x2 ^ x3)
        tree = p.parse_from_txt("x1 ^ x2 ^ x3")
        assert tree.name == "^"
        assert tree.children[0].name == "x1"
        assert tree.children[1].name == "^"
        assert child_names(tree.children[1]) == ["x2", "x3"]

    def test_function_of_product(self, p):
        tree = p.parse_from_txt("log ( x1 * x2 )")
        assert tree.name == "log"
        assert tree.children[0].name == "*"

    def test_parens_override_right(self, p):
        tree = p.parse_from_txt("x1 * ( x2 + x3 ) + x4")
        assert tree.name == "+"
        assert tree.children[0].name == "*"
        assert tree.children[0].children[1].name == "+"

    def test_default_formula(self, p):
        tree = p.parse_from_txt()
        assert tree.name == "*"
        assert tree.children[1].name == "+"

    def test_function_minus_function(self, p):
        tree = p.parse_from_txt("sin ( x1 ) - cos ( x2 )")
        assert tree.name == "-"
        assert tree.children[0].name == "sin"
        assert tree.children[1].name == "cos"

    def test_function_of_subtraction(self, p):
        tree = p.parse_from_txt("sin ( x1 - x2 )")
        assert tree.name == "sin"
        assert tree.children[0].name == "-"

    def test_parens_around_exp(self, p):
        tree = p.parse_from_txt("( x1 ^ x2 ) * ( x3 ^ x4 )")
        assert tree.name == "*"
        assert tree.children[0].name == "^"
        assert tree.children[1].name == "^"

    def test_function_of_division(self, p):
        tree = p.parse_from_txt("log ( x1 / x2 )")
        assert tree.name == "log"
        assert tree.children[0].name == "/"

    def test_four_term_product(self, p):
        tree = p.parse_from_txt("x1 * x2 * x3 * x4")
        assert tree.name == "*"
        assert tree.children[1].name == "x4"

    def test_exp_of_sum(self, p):
        tree = p.parse_from_txt("x1 ^ ( x2 + x3 )")
        assert tree.name == "^"
        assert tree.children[1].name == "+"

    def test_div_constants(self, p):
        tree = p.parse_from_txt("10 / 2")
        assert tree.name == "/"
        assert child_names(tree) == ["10", "2"]

    def test_exp_constants(self, p):
        tree = p.parse_from_txt("2 ^ 3")
        assert tree.name == "^"
        assert child_names(tree) == ["2", "3"]

    def test_add_then_exp(self, p):
        tree = p.parse_from_txt("x1 + x2 ^ x3 + x4")
        # ((x1) + (x2^x3)) + x4
        assert tree.name == "+"
        assert tree.children[1].name == "x4"
        assert tree.children[0].name == "+"

    def test_mul_in_nested_parens(self, p):
        tree = p.parse_from_txt("( ( x1 * x2 ) + x3 )")
        assert tree.name == "+"
        assert tree.children[0].name == "*"

    def test_const_exp_var(self, p):
        tree = p.parse_from_txt("2 ^ x1")
        assert tree.name == "^"
        assert child_names(tree) == ["2", "x1"]

    def test_function_of_exp(self, p):
        tree = p.parse_from_txt("sin ( x1 ^ x2 )")
        assert tree.name == "sin"
        assert tree.children[0].name == "^"

    def test_sum_of_products(self, p):
        tree = p.parse_from_txt("x1 * x2 + x3 * x4 + x5 * x6")
        assert tree.name == "+"
        assert tree.children[1].name == "*"

    def test_triple_div(self, p):
        tree = p.parse_from_txt("x1 / x2 / x3")
        assert tree.name == "/"
        assert tree.children[0].name == "/"

    def test_function_added_to_const(self, p):
        tree = p.parse_from_txt("sin ( x1 ) + 5")
        assert tree.name == "+"
        assert tree.children[0].name == "sin"
        assert tree.children[1].name == "5"


# ── Tree iteration & structure ──────────────────────────────────────

class TestTreeIteration:
    """Tests using anytree iterators, search, and node properties."""

    # ── Node counts ─────────────────────────────────────────────────

    def test_single_var_node_count(self, p):
        tree = p.parse_from_txt("x1")
        assert len(list(PreOrderIter(tree))) == 1

    def test_binary_op_node_count(self, p):
        tree = p.parse_from_txt("x1 + x2")
        assert len(list(PreOrderIter(tree))) == 3

    def test_chained_add_node_count(self, p):
        # x1 + x2 + x3  ->  ((x1+x2)+x3)  = 5 nodes
        tree = p.parse_from_txt("x1 + x2 + x3")
        assert len(list(PreOrderIter(tree))) == 5

    def test_function_node_count(self, p):
        # sin(x1) = 2 nodes
        tree = p.parse_from_txt("sin ( x1 )")
        assert len(list(PreOrderIter(tree))) == 2

    def test_function_of_expr_node_count(self, p):
        # sin(x1+x2) = sin -> + -> x1,x2  = 4 nodes
        tree = p.parse_from_txt("sin ( x1 + x2 )")
        assert len(list(PreOrderIter(tree))) == 4

    def test_complex_expr_node_count(self, p):
        # x1 * x2 + x3 * x4  ->  +(*(x1,x2), *(x3,x4))  = 7 nodes
        tree = p.parse_from_txt("x1 * x2 + x3 * x4")
        assert len(list(PreOrderIter(tree))) == 7

    def test_full_precedence_node_count(self, p):
        # x1 + x2 * x3 ^ x4  ->  +(x1, *(x2, ^(x3,x4)))  = 7 nodes
        tree = p.parse_from_txt("x1 + x2 * x3 ^ x4")
        assert len(list(PreOrderIter(tree))) == 7

    # ── Tree height & depth ─────────────────────────────────────────

    def test_single_var_height(self, p):
        tree = p.parse_from_txt("x1")
        assert tree.height == 0

    def test_binary_op_height(self, p):
        tree = p.parse_from_txt("x1 + x2")
        assert tree.height == 1

    def test_chained_add_height(self, p):
        # ((x1+x2)+x3) -> height 2
        tree = p.parse_from_txt("x1 + x2 + x3")
        assert tree.height == 2

    def test_precedence_chain_height(self, p):
        # x1 + x2 * x3 ^ x4  ->  +(x1, *(x2, ^(x3,x4)))  -> height 3
        tree = p.parse_from_txt("x1 + x2 * x3 ^ x4")
        assert tree.height == 3

    def test_leaf_depth(self, p):
        tree = p.parse_from_txt("x1 + x2 * x3")
        # x3 is at depth 2: + -> * -> x3
        x3 = find_by_attr(tree, "x3")
        assert x3.depth == 2

    def test_root_depth_is_zero(self, p):
        tree = p.parse_from_txt("x1 + x2")
        assert tree.depth == 0

    # ── Leaves ──────────────────────────────────────────────────────

    def test_binary_leaves(self, p):
        tree = p.parse_from_txt("x1 + x2")
        leaf_names = [n.name for n in tree.leaves]
        assert leaf_names == ["x1", "x2"]

    def test_complex_leaves(self, p):
        tree = p.parse_from_txt("x1 * x2 + x3 * x4")
        leaf_names = [n.name for n in tree.leaves]
        assert leaf_names == ["x1", "x2", "x3", "x4"]

    def test_function_leaves(self, p):
        tree = p.parse_from_txt("sin ( x1 ) + cos ( x2 )")
        leaf_names = [n.name for n in tree.leaves]
        assert leaf_names == ["x1", "x2"]

    def test_leaf_count_matches_operands(self, p):
        tree = p.parse_from_txt("x1 + x2 * x3 ^ x4")
        assert len(tree.leaves) == 4

    # ── Pre-order traversal ─────────────────────────────────────────

    def test_preorder_binary(self, p):
        tree = p.parse_from_txt("x1 + x2")
        order = [n.name for n in PreOrderIter(tree)]
        assert order == ["+", "x1", "x2"]

    def test_preorder_precedence(self, p):
        # x1 + x2 * x3  ->  +(x1, *(x2,x3))
        tree = p.parse_from_txt("x1 + x2 * x3")
        order = [n.name for n in PreOrderIter(tree)]
        assert order == ["+", "x1", "*", "x2", "x3"]

    def test_preorder_left_assoc(self, p):
        # x1 + x2 + x3  ->  +(+(x1,x2), x3)
        tree = p.parse_from_txt("x1 + x2 + x3")
        order = [n.name for n in PreOrderIter(tree)]
        assert order == ["+", "+", "x1", "x2", "x3"]

    def test_preorder_function(self, p):
        tree = p.parse_from_txt("sin ( x1 + x2 )")
        order = [n.name for n in PreOrderIter(tree)]
        assert order == ["sin", "+", "x1", "x2"]

    # ── Post-order traversal ────────────────────────────────────────

    def test_postorder_binary(self, p):
        tree = p.parse_from_txt("x1 + x2")
        order = [n.name for n in PostOrderIter(tree)]
        assert order == ["x1", "x2", "+"]

    def test_postorder_precedence(self, p):
        tree = p.parse_from_txt("x1 + x2 * x3")
        order = [n.name for n in PostOrderIter(tree)]
        assert order == ["x1", "x2", "x3", "*", "+"]

    def test_postorder_matches_rpn(self, p):
        # Post-order of an expression tree is reverse-Polish notation
        # x1 * x2 + x3  ->  +(*(x1,x2), x3)  ->  RPN: x1 x2 * x3 +
        tree = p.parse_from_txt("x1 * x2 + x3")
        order = [n.name for n in PostOrderIter(tree)]
        assert order == ["x1", "x2", "*", "x3", "+"]

    # ── Level-order traversal ───────────────────────────────────────

    def test_levelorder_binary(self, p):
        tree = p.parse_from_txt("x1 + x2")
        order = [n.name for n in LevelOrderIter(tree)]
        assert order == ["+", "x1", "x2"]

    def test_levelorder_precedence(self, p):
        # +(x1, *(x2,x3))  ->  level0: +, level1: x1 *, level2: x2 x3
        tree = p.parse_from_txt("x1 + x2 * x3")
        order = [n.name for n in LevelOrderIter(tree)]
        assert order == ["+", "x1", "*", "x2", "x3"]

    def test_levelorder_balanced(self, p):
        # (x1+x2)*(x3+x4) -> level0: *, level1: + +, level2: x1 x2 x3 x4
        tree = p.parse_from_txt("( x1 + x2 ) * ( x3 + x4 )")
        order = [n.name for n in LevelOrderIter(tree)]
        assert order == ["*", "+", "+", "x1", "x2", "x3", "x4"]

    # ── find_by_attr & findall ──────────────────────────────────────

    def test_find_by_attr_variable(self, p):
        tree = p.parse_from_txt("x1 + x2 * x3")
        node = find_by_attr(tree, "x2")
        assert node is not None
        assert node.parent.name == "*"

    def test_find_by_attr_operator(self, p):
        tree = p.parse_from_txt("x1 + x2 * x3")
        node = find_by_attr(tree, "*")
        assert node is not None
        assert node.parent.name == "+"

    def test_findall_leaves(self, p):
        tree = p.parse_from_txt("x1 * x2 + x3")
        leaves = findall(tree, filter_=lambda n: n.is_leaf)
        assert [n.name for n in leaves] == ["x1", "x2", "x3"]

    def test_findall_operators(self, p):
        tree = p.parse_from_txt("x1 + x2 * x3")
        ops = findall(tree, filter_=lambda n: not n.is_leaf)
        assert [n.name for n in ops] == ["+", "*"]

    def test_findall_variables_in_complex(self, p):
        tree = p.parse_from_txt("sin ( x1 ) + x2 * x3")
        leaves = findall(tree, filter_=lambda n: n.is_leaf)
        assert [n.name for n in leaves] == ["x1", "x2", "x3"]

    # ── Descendants & ancestors ─────────────────────────────────────

    def test_descendants_count(self, p):
        tree = p.parse_from_txt("x1 + x2 * x3")
        # root (+) has 4 descendants: x1, *, x2, x3
        assert len(tree.descendants) == 4

    def test_ancestors_of_deep_node(self, p):
        # x1 + x2 * x3 ^ x4  ->  +(x1, *(x2, ^(x3,x4)))
        tree = p.parse_from_txt("x1 + x2 * x3 ^ x4")
        x4 = find_by_attr(tree, "x4")
        ancestor_names = [n.name for n in x4.ancestors]
        assert ancestor_names == ["+", "*", "^"]

    # ── Siblings ────────────────────────────────────────────────────

    def test_siblings_binary(self, p):
        tree = p.parse_from_txt("x1 + x2")
        x1 = find_by_attr(tree, "x1")
        assert [s.name for s in x1.siblings] == ["x2"]

    def test_siblings_balanced(self, p):
        tree = p.parse_from_txt("( x1 + x2 ) * ( x3 + x4 )")
        left_plus = tree.children[0]
        assert [s.name for s in left_plus.siblings] == ["+"]

    # ── is_root / is_leaf ───────────────────────────────────────────

    def test_root_is_root(self, p):
        tree = p.parse_from_txt("x1 + x2")
        assert tree.is_root

    def test_leaves_are_leaves(self, p):
        tree = p.parse_from_txt("x1 + x2 * x3")
        for leaf in tree.leaves:
            assert leaf.is_leaf

    def test_operator_not_leaf(self, p):
        tree = p.parse_from_txt("x1 + x2 * x3")
        mul = find_by_attr(tree, "*")
        assert not mul.is_leaf
        assert not mul.is_root

import pytest
from anytree import AnyNode, RenderTree
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

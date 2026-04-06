from treelib import Tree
from elements import Constant, Variable, Expression
from re import search as ReSearch

class Parser:
    def parse_from_txt(self, formula:str= "x1 * ( x2 + x3 )") -> Tree:
        """_summary_
        Accepts input of formulas in text form.
        Variables: x1, x2, x3, ...
        Seperator must be space
        
        Returns:
            _type_: Tree Object
        
        """            
        output = Tree()
        stack = [] # All elements will be pushed to the stack. The tree will be built in the stack

        form = formula.split(' ') # Make list of all expressions (Later replace with tokenizer)
        form = [for x in form: classify_element(x))] # List now of element objects

        output = _apply_expressions(form, 4)


    def _apply_expressions(self, formula:list[Constant|Variable|Expression], prio:int) -> Tree:
        """
        Recursively applies expressions of a select prio and downwards
        """

        if not max(x) for x in [element in formula if type(element) == Expression] == prio:
            return _apply_expressions(formula, prio-1)

        for element in formula:
            if type(element) == Expression and element.priority == prio:

    
    def classify_element(self, element:str="x1") -> Constant|Variable|Expression:
        if ReSearch("\d+", element):
            return Constant(int(element))
        elif ReSearch("x\d", element):
            return Variable(element)
        elif ReSearch("\*|\+|\-|\/|\(", element):
            return Expression(element)
        
        else:
            raise TypeError("Input can not be classified")

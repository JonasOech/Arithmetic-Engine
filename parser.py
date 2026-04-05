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
        stack = []

        list = formula.split(' ') # Make array
        
        
    
    def classify_element(self, element:str="x1") -> Constant|Variable|Expression:
        if ReSearch("\d+", element):
            return Constant(int(element))
        elif ReSearch("x\d", element):
            return Variable(element)
        elif ReSearch("\*|\+|\-|\/", element):
            return Expression(element)
        
        else:
            raise TypeError("Input can not be classified")
from anytree import AnyNode
from elements import Constant, Variable, Expression, Function
from re import search as ReSearch
from typing import cast

class Parser:
    def parse_from_txt(self, formula:str| list[str] = "x1 * ( x2 + x3 )") -> AnyNode|list[AnyNode]:
        """_summary_
        Accepts input of formulas in text form.
        Variables: x1, x2, x3, ...
        Seperator must be space
        
        Returns:
            _type_: Tree Object
        
        """            
        if type(formula) == list:
            return [cast(AnyNode, self.parse_from_txt(i)) for i in formula]

        form = cast(str, formula).strip().split(' ') # Make list of all expressions (Later replace with tokenizer TODO)

        form = [self._classify_element(x) for x in form] # List now of element objects
        
        # replace every const and var with a AnyNode
        for i in range(len(form)): 
            if type(form[i]) in [Constant, Variable]:
                form[i] = AnyNode(name = str(form[i]), element = form[i])
        form = cast(list[AnyNode|Expression|Function], form)

        # If everything succeded, it's a list with just a tree
        output = self._apply_expressions(form)[0]
        return output 

    def _apply_expressions(self, formula:list[AnyNode|Expression|Function]) -> list[AnyNode]:
        """
        applies expressions recursively
        """
        # Apply functions , but just "F ( S )"
        for i in range(len(formula)):
            # Perform type safety
            if not (
                i + 3 < len(formula) and # avoid index errors
                type(formula[i]) == Function and
                type(formula[i+1]) == Expression and 
                type(formula[i+2]) == AnyNode and
                type(formula[i+3]) == Expression
            ):
                continue
            # check if parenthesis match
            if not (
                str(formula[i+1]) == "(" and
                str(formula[i+3]) == ")"
            ):
                continue

            # We have a function!
            formula[i] = AnyNode(name = str(formula[i]), children=[formula[i+2]], element = formula[i])
            del formula[i+1:i+4]

            return self._apply_expressions(formula)

        # Apply Parentheses, but just "( S )"
        for i in range(len(formula)):
            # Perform type safety
            if not (
                i + 2 < len(formula) and # avoid index errors
                type(formula[i+0]) == Expression and 
                type(formula[i+1]) == AnyNode and
                type(formula[i+2]) == Expression
            ):
                continue
            # check if parenthesis match
            if not (
                str(formula[i+0]) == "(" and
                str(formula[i+2]) == ")"
            ):
                continue

            # We have Parenthesis

            formula[i] = formula[i+1]
            del formula[i+1:i+3]

            return self._apply_expressions(formula)


        # Apply Exponentiation "S ^ S"
        formula, r = self._apply_binary_operator(formula, "^", ltr=False)
        if r: 
            return self._apply_expressions(formula)

        # Apply Multiplication "S S"
        for i in range(len(formula)):
            if not ( 
                    i+1 < len(formula) and
                    # S S
                    type(formula[i]) == AnyNode and 
                    type(formula[i+1]) == AnyNode
            ):
                continue

            formula[i] = AnyNode(name = "*", element = Expression("*"), children=[
                formula[i],
                formula[i+1]
            ])
            del formula[i+1]
            return self._apply_expressions(formula)


        # Apply Multiplication "S * S" and Division "S/s"
        formula, r = self._apply_binary_operator(formula, ["*", "/"])
        if r: 
            return self._apply_expressions(formula)

        # Apply Addition "S + S"
        formula, r = self._apply_binary_operator(formula, ["+", "-"])
        if r: 
            return self._apply_expressions(formula)


            
        # If we arrive here, none of the above operations were made. Check if we are done.
        if len(formula) == 1 and isinstance(formula[0], AnyNode):
            return cast(list[AnyNode], formula)
        raise Exception("Didn't work")


        
    def _apply_binary_operator(self, formula:list[AnyNode|Expression|Function], op:str|list[str] = "+", ltr:bool = True) -> tuple[list[AnyNode|Expression|Function], bool]:
        """ Will search the tree for binary operations like S * S, S + S, ...

        Args:
            formula (_type_): the formula
            op (str, optional): the operator: "+", "/", ...
            ltr (bool, optional): Left to right. Will search right to left if false

        Returns:
            list: the new function
            bool: true if a change was performed
        """
        
        indices = range(len(formula)) if ltr else range(len(formula) - 1, -1, -1)
        for i in indices:
            if not(
                i+2 < len(formula) and
                type(formula[i]) == AnyNode and
                type(formula[i+1]) == Expression and
                type(formula[i+2]) == AnyNode and
                ( # op could be both list or str
                    str(formula[i+1]) == op or
                    str(formula[i+1]) in op
                )
            ):
                continue


            formula[i+1] = AnyNode(name = str(formula[i+1]), element = formula[i+1], children=[
                formula[i],
                formula[i+2]
            ])
            del formula[i+2]
            del formula[i]

            return formula, True

        return formula, False

         

    
    def _classify_element(self, element:str="x1") -> Constant|Variable|Expression|Function|AnyNode:
        if ReSearch(r"^x\d*$|^[a-z]$", element):
            return Variable(element)
        elif ReSearch(r"^\d+$", element):
            return Constant(int(element))
        elif ReSearch(r"^[\*\+\-\/\(\)\^]$", element):
            return Expression(element)
        else:
            return Function(element)

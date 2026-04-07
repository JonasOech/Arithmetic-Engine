class Element:
    tag : str 

    def __init__(self):
        raise NotImplementedError("Cant use the Element object by its own.")

    def __str__(self):
        raise NotImplementedError

class Constant(Element):
    value: int|float|complex|bool
    
    def __init__(self, value: int|float|complex|bool):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return isinstance(other, Constant) and self.value == other.value

class Variable(Element):
    id : str

    def __init__(self, id: str):
        self.id = id

    def __str__(self):
        return str(self.id)

    def __eq__(self, other):
        return isinstance(other, Variable) and self.id == other.id


class Expression(Element):
    type : str
    Numelements : int

    def __init__(self, type: str):
        self.type = type

    def __str__(self):
        return str(self.type)

    def __eq__(self, other):
        return isinstance(other, Expression) and self.type == other.type

class Function(Element):
    type : str
    NumElements: int

    def __init__(self, type:str):
        self.type = type
    
    def __str__(self):
        return str(self.type)

    def __eq__(self, other):
        return isinstance(other, Function) and self.type == other.type
    
class Placeholder(Element):
    id : str

    def __init__(self, id:str):
        self.id = id

    def __str__(self):
        return str(self.id)
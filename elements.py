from math import inf


class Element:
    tag : str 

    def __str__(self):
        raise NotImplementedError

class Constant(Element):
    value: int|float|complex|bool
    
    def __init__(self, value: int|float|complex|bool):
        self.value = value

    def __str__(self):
        return str(self.value)

class Variable(Element):
    id : str

    def __init__(self, id: str):
        self.id = id

    def __str__(self):
        return str(self.id)


class Expression(Element):
    type : str
    Numelements : int
    priority : int # determines order of operation. Higher order means executed first

    def __init__(self, type: str):
        self.type = type

        match type:
            case "+"|"-": 
                self.priority = 0
                self.Numelements = 2
            case "*"|"/":
                self.priority = 1
                self.Numelements = 2
            case "^": 
                self.priority = 2
                self.Numelements = 2
            case "("|")":
                self.priority = 3
    
    def __str__(self):
        return str(self.type)

class Function(Element):
    type : str
    NumElements: int

    def __init__(self, type:str):
        self.type = type
    
    def __str__(self):
        return str(self.type)
    
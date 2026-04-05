from math import inf


class Element:
    tag : str 

class Constant(Element):
    value: int|float|complex|bool
    
    def __init__(self, value: int|float|complex|bool):
        self.value = value

class Variable(Element):
    id : str

    def __init__(self, id: str):
        self.id = id

class Expression(Element):
    type : str
    Numelements : int
    order : int # determines order of operation. Higher order means executed first

    def __init__(self, type: str):
        self.type = type

        match type:
            case "+"|"-": 
                self.order = 0
                self.Numelements = 2
            case "*"|"/":
                self.order = 1
                self.Numelements = 2
            case "^": 
                self.order = 2
                self.Numelements = 2
            case "("|")":
                self.order = 3
                self.Numelements = int("inf")


    

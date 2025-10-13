import random

class Dice:
    def __init__(self):
        self.__values__ = [0, 0]
    
    def roll(self):
        self.__values__ = [random.randint (1, 6), random.randint (1, 6)]
        return self.__values__
    
    @property
    def values(self):
        return tuple(self.__values__)
    
    def is_double(self):
        return self.__values__[0], self.__values__[1]
    
    def __str__(self):
        v1, v2 = self.__values__
        s = f"{v1} - {v2}"
        if self.is_double():
            s += "doble"
            return s



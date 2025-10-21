import random #Lo importamos para poder utilizar funciones con las cuales generemos números aleatorios 


class Dice:
    def __init__(self):
        """
        Inicializa los dados en estado 'sin tirar'.
        Los valores iniciales se representan como [0, 0].
        """
        self.__values__ = [0, 0]
    
    def roll(self):
        """
        Realiza una tirada de dos dados, generando valores aleatorios entre 1 y 6.
        Devuelve la lista con los valores obtenidos.
        """
        self.__values__ = [random.randint (1, 6), random.randint (1, 6)]
        return self.__values__
    
    @property#Nos va permitir acceder a los metodos como si fueran atributos, por mas que devuelvan valores internos 
    def values(self):
        """
        Devuelve los valores actuales de los dados como una tupla.
        Ejemplo: (3, 5)
        """
        return tuple(self.__values__)
    
    def is_double(self):
        """
        Retorna True si ambos dados muestran el mismo valor y no son cero.
        De lo contrario, devuelve False.
        """
        v1, v2 = self.__values__
        return v1 == v2 and v1 != 0
    
    def reset(self):
        """
        Reinicia los valores de los dados a su estado inicial (sin tirar).
        """
        self.__values__ = [0, 0]
    
    def __str__(self):
        """
        Devuelve una representación en texto de los dados.
        """
        v1, v2 = self.__values__
        if v1 == 0 and  v2 == 0:
            return "Falta tirar"
        s = f"{v1} - {v2}"
        if self.is_double():
            s += " (doble)"#Le suma a s el texto "(doble)"
        return s

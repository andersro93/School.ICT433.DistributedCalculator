from .Operation import Operation


class Division(Operation):

    SYMBOL = "/"

    def __init__(self):
        super().__init__()

    def calculate(self, arg1, arg2):
        return arg1 / arg2

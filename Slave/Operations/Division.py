from .Operation import Operation


class Division(Operation):

    SYMBOL = "/"

    def __init__(self):
        super().__init__()

    def calculate(self, arg1, arg2):
        return float(arg1) / float(arg2)

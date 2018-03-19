

class Operation(object):

    SYMBOL = None

    def calculate(self, arg1, arg2):
        raise NotImplemented("The operation class needs to implement this function!")

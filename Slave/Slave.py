from random import Random
from xmlrpc.server import SimpleXMLRPCServer

from .Operations import *
import xmlrpc.client


class Slave(object):

    MASTER_HOST = None
    """ The host address of the master server """

    MASTER_PORT = None
    """ The port on the master server """

    SERVER = None
    """ The server to the slave """

    OPERATOR = None
    """ Which operation this slave is going to do """

    OWN_HOSTNAME = None
    """ Which hostname the slave is going to listen on """

    OWN_PORT = None
    """ Which port the slave is going to listen on """

    SLAVE_PORT_RANGE = (20000, 22000)
    """ The port range the slave might use """

    SUPPORTED_OPERATIONS = [
        Addition,
        Subtraction,
        Multiplication,
        Division,
        Power
    ]

    def __init__(self, master_host, master_port, operation=None):
        self.MASTER_HOST = master_host
        self.MASTER_PORT = master_port

        # Could have been something more elegant
        self.OWN_HOSTNAME = "localhost"

        # Set own port to a random port in given interval
        self.OWN_PORT = Random().randint(self.SLAVE_PORT_RANGE[0], self.SLAVE_PORT_RANGE[1])

        if not operation:
            self.OPERATOR = Random().choice(self.SUPPORTED_OPERATIONS)()
        else:
            for supported_operation in self.SUPPORTED_OPERATIONS:
                if operation == supported_operation.SYMBOL:
                    self.OPERATOR = supported_operation()
                    break

    def run(self):
        self.register_to_master()

    def register_to_master(self):
        with xmlrpc.client.ServerProxy(f'http://{self.MASTER_HOST}:{self.MASTER_PORT}/') as master:
            print(self.MASTER_HOST)
            print(f"Registering at: http://{self.MASTER_HOST}:{self.MASTER_PORT}/")

            if master.register("localhost", self.OWN_PORT, self.OPERATOR.SYMBOL):
                self.start_own_server()

    def calculate(self, arg1, arg2):
        """
        Calculates the given arguments with the operator that the slave uses
        :param arg1: number
        :param arg2: number
        :return: number, str
        """
        print(f"New request: {arg1} {self.OPERATOR.SYMBOL} {arg2}")

        result = self.OPERATOR.calculate(arg1, arg2)

        print(f"Result: {result}\n")

        return result

    def start_own_server(self):
        # Create the server
        self.SERVER = SimpleXMLRPCServer((self.OWN_HOSTNAME, self.OWN_PORT))

        # Register the routes
        self.SERVER.register_introspection_functions()
        self.SERVER.register_function(self.calculate, "calculate")
        self.SERVER.register_function(self.heartbeat, "heartbeat")

        # Print started
        print(f"Slave started with operation: {self.OPERATOR.SYMBOL}, at: {self.OWN_HOSTNAME}:{self.OWN_PORT}")

        # Run the server
        self.SERVER.serve_forever()

    @staticmethod
    def heartbeat():
        """
        Simple heartbeat method to check if the slave is up
        :return: bool
        """
        return True

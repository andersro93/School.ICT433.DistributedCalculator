from random import Random
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy

from .Task import Task


class Master(object):

    SERVER = None
    """ The server object that serves as the master server """

    HOSTNAME = None
    """ Which host to bind to """

    PORT = None
    """ Which port to bind the master server to """

    SLAVES = dict()
    """ All the slaves that are registered on the master server """

    SUPPORTED_OPERATORS = ["**", "*", "/", "+", "-"]
    """ The supported operators by the server """

    RANDOM = None
    """ Random object used to perform random operations """

    def __init__(self, hostname, port):
        self.HOSTNAME = hostname
        self.PORT = port
        self.RANDOM = Random()

        # Create a dictionary of all operators
        for operator in self.SUPPORTED_OPERATORS:
            self.SLAVES[operator] = list()

    def register_slave(self, hostname, port, operator):
        """
        Registers the slave
        :param hostname: str
        :param port: int
        :param operator: str
        :return: bool
        """

        # Create slave tuple
        slave = (hostname, port)

        # Check if operator is valid
        if operator not in self.SUPPORTED_OPERATORS:
            print(f"Invalid operator from slave: '{operator}'")
            return False

        self.SLAVES[operator].append(slave)
        print(f"Slave registered: {operator}, {slave}")

        return True

    def calculate(self, command: str):

        # Remove spaces from expression
        command_without_spaces = command.strip(" ")

        # Determine all tasks
        task = self.create_task(command_without_spaces)

        # Calculate task
        result = self.calculate_task(task)

        return result

    def create_task(self, command):
        if "(" in command or ")" in command:
            start_index = command.find("(")
            end_index = command.rfind(")")

            self.create_task(command[start_index:end_index])

        operation = False

        for supported_operation in self.SUPPORTED_OPERATORS:
            if supported_operation in command:
                operation = supported_operation
                break

        splitted_command = command.split(operation)

        task = Task()
        task.Operation = operation
        task.ARG1 = splitted_command[0]
        task.ARG2 = splitted_command[2]

        return task

    def calculate_task(self, task: Task):
        if task.ARG1 is Task:
            task.ARG1 = self.calculate_task(task.ARG1)

        if task.ARG2 is Task:
            task.ARG2 = self.calculate_task(task.ARG2)

        return self.send_task_to_slave(task.ARG1, task.Operation, task.ARG2)

    def send_task_to_slave(self, arg1=None, operator=None, arg2=None):
        """
        Forwards the given input to one of the slaves connected to the server
        :param arg1:
        :param operator:
        :param arg2:
        :return: double, str
        """
        print(f"New request: {arg1} {operator} {arg2}")

        if operator not in self.SUPPORTED_OPERATORS:
            return f"Invalid operation: '{operator}'"

        if len(self.SLAVES) is 0:
            return f"No slaves is online to perform the operation: '{operator}'"

        for slave in self.SLAVES[operator]:

            with ServerProxy(f"http://{slave[0]}:{slave[1]}/") as client:
                result = client.calculate(arg1, arg2)
                print(f"Result from Slave: {result}")
                return result

        return "No slaves available to handle your request, sorry..."

    def run(self):
        """
        Runs the server instance
        """

        # Create the server
        self.SERVER = SimpleXMLRPCServer((self.HOSTNAME, self.PORT))

        # Register the routes
        self.SERVER.register_introspection_functions()
        self.SERVER.register_function(self.heartbeat, "heartbeat")
        self.SERVER.register_function(self.register_slave, "register")
        self.SERVER.register_function(self.calculate, "calculate")

        # Run the server
        self.SERVER.serve_forever()

    @staticmethod
    def heartbeat():
        """
        Simple heartbeat method to check if the master is online
        :return: bool
        """
        return True

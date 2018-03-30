from random import Random
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
import re
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

    def __init__(self, hostname: str, port: str):
        self.HOSTNAME = hostname
        self.PORT = port
        self.RANDOM = Random()

        # Create a dictionary of all operators
        for operator in self.SUPPORTED_OPERATORS:
            self.SLAVES[operator] = list()

    def register_slave(self, hostname: str, port: str, operator: str) -> bool:
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

    def calculate(self, command: str) -> str:
        """
        Handles an incoming command
        :param command:
        :return: str
        """

        print(f"New calculation: {command}")

        # Remove spaces from expression
        command = command.strip(" ")

        # Solve all parenthesis
        command = self.__solve_parenthesis(command)

        # Solve simple command
        command = self.__solve_simple_commands(command)

        return command

    def __solve_simple_commands(self, command: str):
        """
        Solves the commands
        :param command:
        :return: str
        """
        command = command

        for operator in self.SUPPORTED_OPERATORS:
            while True:
                regex_pattern = '((\d*\.?\d*)([\\' + operator + '])(\d*\.?\d*))'

                matches = re.findall(regex_pattern, command)

                if len(matches) is 0:
                    break

                for sub_command in matches:
                    sub_task = self.create_task(sub_command[1], sub_command[2], sub_command[3])

                    try:
                        result = self.__send_task_to_slave(sub_task)
                    except Exception as e:
                        return str(e)

                    command = command.replace(sub_command[0], str(result))

        return command

    def __solve_parenthesis(self, command: str) -> str:
        """
        Solves the command regarding parenthesis and returns the remaining command
        :param command:
        :return: str
        """

        command = command

        while True:
            matches = re.findall(r"(\((\d*\.?\d*)(.)(\d*\.?\d*)\))", command)

            if len(matches) is 0:
                return command

            for sub_command in matches:
                sub_task = self.create_task(sub_command[1], sub_command[2], sub_command[3])

                try:
                    result = self.__send_task_to_slave(sub_task)
                except Exception as e:
                    return str(e)

                command = command.replace(sub_command[0], str(result))

    def __send_task_to_slave(self, task: Task) -> str:
        """
        Forwards the given input to one of the slaves connected to the server
        :param task: Task
        :return: double, str
        """

        if task.Operation not in self.SUPPORTED_OPERATORS:
            raise Exception(f"Invalid operation: '{task.Operation}'")

        if len(self.SLAVES) is 0:
            raise Exception(f"No slaves is online to perform the operation: '{task.Operation}'")

        for slave in self.SLAVES[task.Operation]:

            with ServerProxy(f"http://{slave[0]}:{slave[1]}/") as client:
                result = client.calculate(task.ARG1, task.ARG2)
                print(f"Result from Slave: {result}")
                return result

        raise Exception("No slaves available to handle your request, sorry...")

    def run(self):
        """
        Runs the server instance
        """

        # Create the server
        self.SERVER = SimpleXMLRPCServer((self.HOSTNAME, int(self.PORT)))

        # Register the routes
        self.SERVER.register_introspection_functions()
        self.SERVER.register_function(self.heartbeat, "heartbeat")
        self.SERVER.register_function(self.register_slave, "register")
        self.SERVER.register_function(self.calculate, "calculate")

        # Run the server
        self.SERVER.serve_forever()

    @staticmethod
    def create_task(arg1: str, operator: str, arg2: str) -> Task:
        """
        Factory method for creating tasks and assigning values
        :param arg1:
        :param operator:
        :param arg2:
        :return: Task
        """
        task = Task()
        task.Operation = operator
        task.ARG1 = arg1
        task.ARG2 = arg2

        return task

    @staticmethod
    def heartbeat() -> bool:
        """
        Simple heartbeat method to check if the master is online
        :return: bool
        """
        return True

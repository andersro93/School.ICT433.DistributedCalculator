from xmlrpc.client import ServerProxy


class Client(object):

    MASTER_HOST = None
    """ The master hostname """

    MASTER_PORT = None
    """ The master port """

    CLIENT = None
    """ The client object """

    SUPPORTED_OPERATORS = [
        "+",
        "-",
        "*",
        "/",
        "**"
    ]
    """ The supported operators """

    def __init__(self, master_host, master_port):
        self.MASTER_HOST = master_host
        self.MASTER_PORT = master_port

        self.CLIENT = ServerProxy(f"http://{self.MASTER_HOST}:{self.MASTER_PORT}/")

    def run(self):

        print("============================================================")
        print("Simple distributed calculator")
        print("Enter exit, when you are done")
        print("============================================================")

        while True:
            command = input("> ")

            if command == "exit":
                break

            result = self.CLIENT.calculate(command)

            print(f"[MASTER] {result}")

        print("Exiting application...")

#!/bin/python

import sys

from Master import Master
from Slave import Slave
from Client import Client

MASTER_HOST = 'localhost'
MASTER_PORT = 4444

PROGRAM = None

if "Master" in sys.argv:
    PROGRAM = Master(MASTER_HOST, MASTER_PORT)
elif "Slave" in sys.argv:
    PROGRAM = Slave(MASTER_HOST, MASTER_PORT, "+")
elif "Client" in sys.argv:
    PROGRAM = Client(MASTER_HOST, MASTER_PORT)

PROGRAM.run()

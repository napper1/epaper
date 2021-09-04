import os
import socket


if socket.gethostname() == os.getenv("PRODUCTION_HOSTNAME"):
    DEBUG = False
else:
    DEBUG = True

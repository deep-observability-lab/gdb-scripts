import os
def init(workspace, coredump='/var/sysroot/', default_port=1234 ,environment = ''):
    global WORKSPACE
    global DEFAULT_PORT
    global NUM_PORTS
    global AVAILABLE_PORTS
    global COREDUMP
    global ENV
    WORKSPACE = os.path.abspath(workspace)
    ENV = environment
    DEFAULT_PORT = int(default_port)
    NUM_PORTS = 3
    AVAILABLE_PORTS = [i + DEFAULT_PORT for i in range(NUM_PORTS)]
    COREDUMP = coredump

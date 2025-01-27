import os


def init(
        workspace,
        coredump='/var/sysroot/',
        default_port=1234,
        environment='',
        src_env=''):
    global WORKSPACE
    global DEFAULT_PORT
    global NUM_PORTS
    global AVAILABLE_PORTS
    global COREDUMP
    global ENV
    global SRC_ENV
    WORKSPACE = os.path.abspath(workspace)
    ENV = environment
    SRC_ENV = src_env
    DEFAULT_PORT = int(default_port)
    NUM_PORTS = 3
    AVAILABLE_PORTS = [i + DEFAULT_PORT for i in range(NUM_PORTS)]
    COREDUMP = coredump


def init(workspace, default_port=1234):
    global WORKSPACE
    global DEFAULT_PORT
    global NUM_PORTS
    global AVAILABLE_PORTS

    WORKSPACE = workspace
    DEFAULT_PORT = int(default_port)
    NUM_PORTS = 3
    AVAILABLE_PORTS = [i+DEFAULT_PORT for i in range(NUM_PORTS)]

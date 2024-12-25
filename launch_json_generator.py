import os
import json
import subprocess


def generate_debug_config(mode, output_path, **kwargs):
    """
    Generates a `launch.json` configuration for debugging in VSCode.

    Args:
        mode (str): Mode of debugging ("live" or "coredump").
        output_path (str): Path to save the generated `launch.json`. The parent directory is created if it doesn't exist.
        kwargs: Additional parameters specific to the mode:
            - For "live":
                - ip (str): Remote IP address.
                - port (str): GDB server port.
                - binary_path (str): Full path to the local binary.
                - workspace (str): Workspace folder path.
                - gdb_script (str): Path to the GDB commands file.
            - For "coredump":
                - core_path (str): Path to the core dump file.
                - binary_path (str): Full path to the local binary.
                - workspace (str): Workspace folder path.
                - gdb_script (str): Path to the GDB commands file.
    """
    try:
        # Ensure the parent directory of output_path exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Static schema version
        version = "0.2.0"

        if mode == "live":
            config = {
                "name": "Remote Debugging with GDB",
                "type": "cppdbg",
                "request": "attach",
                "program": kwargs["binary_path"],
               
                # "stopAtEntry": False,
                # "cwd": kwargs["workspace"],
                "processId" : int(kwargs['process_id']),
                "useExtendedRemote": True,
                "MIMode": "gdb",
                "miDebuggerPath": "/usr/bin/gdb-multiarch",
                "miDebuggerServerAddress": f"{kwargs['ip']}:{kwargs['port']}",
                "setupCommands": [
                    {
                      "description": "Enable pretty-printing for gdb",
                      "text": "-enable-pretty-printing",
                       "ignoreFailures": False
                    },
                    {
                        "description": "set gdb architecture to destination architecture.",
                        "text": f"set architecture {kwargs['arch']}",
                         "ignoreFailures": False
                    },
                    {
                        "description": "Enable extended remote mode",
                        "text": f"target extended-remote {kwargs['ip']}:{kwargs['port']}",
                         "ignoreFailures": False
                    },       
                    {
                        "description": "Enable Non-Stop Mode",
                        "text": "set non-stop on",
                         "ignoreFailures": False
                    },
                    {
                        "description": "Enable Target Async",
                        "text": "set target-async on",
                         "ignoreFailures": False
                    },
                    {
                        "description": "List threads",
                        "text": "info threads",
                         "ignoreFailures": False
                    },
                    {
                        "description": "Ignore SIGALRM signal",
                        "text": "handle SIGALRM nostop noprint",
                         "ignoreFailures": False
                    },
                    {
                        "description": "Ignore SIGSTOP signal",
                        "text": "handle SIGSTOP nostop noprint",
                         "ignoreFailures": False
                    }, 
                    {
                        "description": "load gdb commands",
                        "text": f"source {kwargs['gdb_script']}",
                         "ignoreFailures": False
                    }
                ],
                "logging": {
                    "engineLogging": False,
                    "trace": False,
                    "traceResponse": False
                }
            }
        elif mode == "coredump":
            config = {
                "name": "Debug Core Dump",
                "type": "cppdbg",
                "request": "launch",
                "program": kwargs["binary_path"],
                "coreDumpPath": kwargs["core_path"],
                "stopAtEntry": True,
                "cwd": kwargs["workspace"],
                "MIMode": "gdb",
                "miDebuggerPath": "/usr/bin/gdb-multiarch",
                "setupCommands": [
                    {
                        "description": "Load GDB script",
                        "text": f"source {kwargs['gdb_script']}",
                        "ignoreFailures": False
                    },
                    {
                      "description": "Enable pretty-printing for gdb",
                      "text": "-enable-pretty-printing",
                      "ignoreFailures": False
                    }
                ],
                "logging": {
                    "engineLogging": False,
                    "trace": False,
                    "traceResponse": False
                },
                "externalConsole": False
            }
        else:
            raise ValueError("Invalid mode. Use 'live' or 'coredump'.")

        # Create launch.json content
        launch_json = {
            "version": version,
            "configurations": [config]
        }

        # Write to file
        with open(output_path, "w") as f:
            json.dump(launch_json, f, indent=4)
        print(f"launch.json written to {output_path}")
        print("open vscode in the path <workspace>/<release>/\n .vscode/launch.json is generated.")
        print("gdbserver is listening on remote...")


    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except PermissionError as e:
        print(f"Error: Permission denied - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

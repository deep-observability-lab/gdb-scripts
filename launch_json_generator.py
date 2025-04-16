import os
import json
import subprocess
import config as cnf


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
                "program": "${{workspaceFolder}}/{}".format(kwargs["binary_path"]),

                # "stopAtEntry": False,
                # "cwd": kwargs["workspace"],
                "processId": int(kwargs['process_id']),
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
                        "text": "source ${{workspaceFolder}}/{}".format(kwargs['gdb_script']),
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
            config = {"name": "Debug Core Dump",
                      "type": "cppdbg",
                      "request": "launch",
                      "program": "${{workspaceFolder}}/{}".format(kwargs["binary_path"]),
                      "coreDumpPath": "${{workspaceFolder}}/{}".format(kwargs["core_path"]),
                      "stopAtEntry": True,
                      "cwd": "${{workspaceFolder}}".format(),
                      "MIMode": "gdb",
                      "miDebuggerPath": "/usr/bin/gdb-multiarch",
                      "setupCommands": [{"description": "Load GDB script",
                                         "text": "source ${{workspaceFolder}}/{}".format(kwargs['gdb_script']),
                                         "ignoreFailures": False},
                                        {"description": "Enable pretty-printing for gdb",
                                         "text": "-enable-pretty-printing",
                                         "ignoreFailures": False}],
                      "logging": {"engineLogging": False,
                                  "trace": False,
                                  "traceResponse": False},
                      "externalConsole": False}
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

        tmp_output = output_path
        if cnf.ENV != '' : 
            tmp_output = cnf.ENV + '/.vscode/launch.json'
        print("\033[33mlaunch.json written to {} \033[0m".format( tmp_output))
        vscode_path = tmp_output.split( "/.vscode")[0]
        print("\033[33mopen vscode in the path {}.vscode/launch.json is generated.\033[0m".format( vscode_path))

        if kwargs['live']:
            print("gdbserver is listening on remote...")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except PermissionError as e:
        print(f"Error: Permission denied - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

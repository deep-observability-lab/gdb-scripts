# tool-chain
=======
# gdb-scripts
a set of gdb scripts for heap and stack and other troubleshooting purposes.
this repository contains : 
# Remote Debugging Automation Tool

This tool simplifies remote debugging by automating essential steps required to debug a process on a remote machine. It connects to a remote `gdbserver`, attaches to a specified process, and facilitates debugging through a local `gdb` instance. Configuration settings allow you to customize the process according to your system.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Example Command](#example-command)
- [Argument Descriptions](#argument-descriptions)
- [Workflow](#workflow)


## Features
- Automates setup and connection for remote debugging.
- Downloads source code to a local path.
- Installs necessary dependencies for remote debugging.
- Configures `gdb` paths to recognize downloaded source code.
- Allows auto-loading of shared libraries from the remote machine.

## Requirements
- Python 3.x
- `gdb-multiarch`
- `gnome-terminal`
- Required Python packages (installed automatically)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/remote-debugging-tool.git
   cd remote-debugging-tool
   ```
2. Install required Python packages:
   ```bash
   sudo pip3 install -r requirements.txt
   ```

## Usage
To initiate remote debugging, run:
```
bashsudo python3 gdb_remote.py [-h] -i IP -u USERNAME -pid PROCESS_ID [-a ARCHITECTURE]
                     -ui USER_INTERFACE [-w WORKSPCAE] [-p PORT] 
```

## Example Command
```bash
sudo python3 gdb_remote.py -i 192.168.183.132 -u zahra -pid 3789 -w ../workspace -p 3434 -a powerpc:common -ui vscode
```

## Argument Descriptions
- **-h** / **--help**: Show help message and exit.
- **-i** / **--ip**: IP address of the remote target (e.g., `-i 192.168.5.5`).
- **-u** / **--username**: Username for authentication on the remote target (e.g., `-u root`).
- **-pid** / **--process_id**: Process ID of the target process (e.g., `-pid 1234`).
- **-a** / **--architecture**: Architecture for the cross-compiled binary. Defaults to `auto` if not specified (e.g., `-a x86_64`).
- **-w** / **--workspace**: Directory where you should put all the shared binaries/app binaries and source codes.
- **-p** / **--port**: Port to set the `DEFAULT_PORT`. If not specified, GDB uses port 1234 (e.g., `-p 1234`).
- **-ui** / **--user_interface**: Specifies the user interface for debugging. Options: "vscode" for Visual Studio Code or "gdb" for GDB CLI.
  
## Workflow

1. **Run Initial Setup**: The script takes the following command as input:
   ```bash
   sudo python3 gdb_remote.py -i 192.168.183.132 -u zahra -pid 3789 -w ../workspace -p 3434 -a powerpc:common
   ```
2. **Prepare Workspace**: In the path you provide script as --workspace, put all the sharedbinaries, source codes , and excutable binary of the process you are going to debug. 

4. **Install Dependencies**: dependancies would be installed automatically. such as:
   - `gdb-multiarch`
   - `gnome-terminal`
   - Relevant Python packages
5. **Start `gdbserver` on Remote Machine**: After setup, the script initiates `gdbserver` on the remote machine at the port specified in `input args`.

6. **Launch `gdb` Locally**: On the local machine, `gdb` is launched to begin debugging. A custom script is executed within `gdb` to set the correct paths for the source code.
7. **Generate `launch.json` for `VScode`**: if you chose vscode for ui_mode, you just need to open VScode at workspace.
8. **Debugging Process**: After configuring, the user can start debugging the specified process.

9. **Exit and Cleanup**: After debugging, the user can run the command:
   ```bash
   exit_gdb
   ```
   This command stops the `gdbserver` on the remote machine and detaches from the process. The local `gdb` instance will also exit.

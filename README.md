# tool-chain
=======

## gdb-scripts
A set of gdb scripts for heap, stack, and other troubleshooting purposes.
This repository contains:
- Remote Debugging Automation Tool

This tool simplifies remote debugging by automating essential steps required to debug a process on a remote machine. It connects to a remote `gdbserver`, attaches to a specified process, and facilitates debugging through a local `gdb` instance. Configuration settings allow you to customize the process according to your system.

---

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Example Command](#example-command)
- [Argument Descriptions](#argument-descriptions)
- [Workflow](#workflow)
- [Coredump Debugging](#coredump-debugging)
- [User Interface (`-ui` flag)](#user-interface-ui-flag)
- [Running in Dockerized Mode](#running-in-dockerized-mode)

---

## Features
- Automates setup and connection for remote debugging.
- Installs necessary dependencies for remote debugging.
- Configures `gdb` paths to recognize downloaded source code.
- Allows auto-loading of shared libraries from the remote machine.
- Enables core-dump debugging by setting GDB pointers correctly.

## Requirements
- Python 3.x
- `gdb-multiarch`
- `tmux`
- Required Python packages (installed automatically)

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/deep-observability-lab/gdb-scripts.git
   cd gdb-scripts
   ```
2. Install required Python packages:
   ```bash
   sudo pip3 install -r requirements.txt
   ```

---

## Usage
To initiate remote debugging, run:
```bash
sudo python3 gdb_remote.py [-h] [-i IP] [-u USERNAME] [-pid PROCESS_ID] [-a ARCHITECTURE]
                           [-ui USER_INTERFACE] [-w WORKSPACE] [-p PORT] [-s ]
```

---

## Example Command
```bash
sudo python3 gdb_remote.py -i 192.168.183.132 -u zahra -pid 3789 -w ../workspace -p 3434 -a powerpc:common -ui vscode
```

---

## Argument Descriptions
- **-h** / **--help**: Show help message and exit.
- **-i** / **--ip**: IP address of the remote target (e.g., `-i 192.168.5.5`).
- **-u** / **--username**: Username for authentication on the remote target (e.g., `-u root`).
- **-pid** / **--process_id**: Process ID of the target process (e.g., `-pid 1234`).
- **-a** / **--architecture**: Architecture for the cross-compiled binary. Defaults to `auto` if not specified (e.g., `-a x86_64`).
- **-w** / **--workspace**: Directory where you should put all the shared binaries/app binaries and source codes.
- **-p** / **--port**: Port to set the `DEFAULT_PORT`. If not specified, GDB uses port 1234 (e.g., `-p 1234`).
- **-ui** / **--user_interface**: Specifies the user interface for debugging. Options: "vscode" for Visual Studio Code or "gdb" for GDB CLI.
- **-s** / **--source**: Directory where you should put all the source codes (separated from binaries and libs).

---

## Workflow

1. **Run Initial Setup**: The script takes the following command as input:
   ```bash
   sudo python3 gdb_remote.py -i 192.168.183.132 -u zahra -pid 3789 -w ../workspace -p 3434 -a powerpc:common
   ```
2. **Prepare Workspace**: In the path you provide script as `--workspace`, put all the shared binaries, source codes, and executable binary of the process you are going to debug.

4. **Install Dependencies**: Dependencies will be installed automatically, such as:
   - `gdb-multiarch`
   - `tmux`
   - Relevant Python packages

5. **Start `gdbserver` on Remote Machine**: After setup, the script initiates `gdbserver` on the remote machine at the port specified in the input args.

6. **Launch `gdb` Locally**: On the local machine, `gdb` is launched to begin debugging. A custom script is executed within `gdb` to set the correct paths for the source code.

7. **Generate `launch.json` for VSCode**: If you chose `vscode` for UI mode, you just need to open VSCode at the workspace.

8. **Debugging Process**: After configuring, the user can start debugging the specified process.

9. **Exit and Cleanup**: After debugging, the user can run the command:
   ```bash
   exit_gdb
   ```
   This command stops the `gdbserver` on the remote machine and detaches from the process. The local `gdb` instance will also exit.

---

## Coredump Debugging

To perform debugging with a coredump, you can run the following command:

```bash
./entrypoint.sh gdb_coredump -w $workspace -a powerpc:common -c core_dump -p program.debug -s <source_code_path> -ui vscode
```

### Argument Descriptions for Coredump Debugging:
- **-w** / **--workspace**: Directory where you should put all the shared binaries, app binaries, and source codes. This should also contain the coredump file.
- **-a** / **--architecture**: Architecture for the cross-compiled binary. Defaults to `auto` if not specified (e.g., `-a powerpc:common`).
- **-c** / **--coredump**: Name of the coredump file located in the workspace.
- **-p** / **--port**: Port to set the `DEFAULT_PORT` for the debugger (e.g., `-p 1234`).
- **-s** / **--source**: Directory where the source codes are located (preferably in the same directory as the binaries and coredump).
- **-ui** / **--user_interface**: Specifies the user interface for debugging. Options: "vscode" for Visual Studio Code or "gdb" for GDB CLI.

### Notes:
- The `launch.json` for debugging will be automatically generated and placed inside the `.vscode` folder within your workspace.
- It is recommended to have your source code located within the same workspace directory as the binaries and coredump for better organization.

---

## User Interface (`-ui` flag)

The `-ui` flag specifies the user interface for debugging, which can either be `gdb` (command-line interface) or `vscode` (Visual Studio Code).

### `-ui gdb`:
- If you specify `-ui gdb`, the tool will automatically open a `gdb-multiarch` instance in a `tmux` session on your local machine. This provides an interactive environment where you can run all your debugging commands directly within the terminal.
  
### `-ui vscode`:
- If you specify `-ui vscode`, the tool will generate a `launch.json` configuration file and place it in the `.vscode` folder inside your workspace. This configuration file will allow you to debug your remote process directly from Visual Studio Code.

Both options are supported for both **remote debugging** and **coredump debugging**. Simply choose the appropriate user interface based on your preferences.

---

## Running in Dockerized Mode

You can run both **remote debugging** and **coredump debugging** in a Dockerized environment. To do so, follow these steps:

### Step 1: Build the Docker Image
Build the Docker image by providing the path to your local repository for `gdb-scripts`:

```bash
docker build --build-arg HOST_PATH=/path/to/repo/gdb-scripts -t gdb-scripts .
```

This will create a Docker image with the necessary dependencies.

### Step 2: Run Docker Container for Coredump Debugging

For **coredump debugging**, run the following Docker command:

```bash
docker run -v /path/to/main-rootfs:/work -v /path/to/src:/src -it gdb-scripts gdb_coredump -c core_dump -p myprogram.debug -w /path/to/main-rootfs -s /path/to/src -ui vscode
```

### Important Notes:
- **`/src`**: The source code directory should be mounted as a volume to `/src` inside the Docker container. This is important to ensure that the debugging environment has access to the correct source code.
- **`/work`**: The main root filesystem (which includes the binaries and the coredump) should be mounted as a volume to `/work`. This path should not be changed as it is crucial for proper execution.
- **`-s`**: Specify the source code path using the `-s` argument, pointing to `/src`.
- **`-w`**: Specify the workspace using the `-w` argument, which should point to `/work`.

### Step 3: Run Docker Container for Remote Debugging

For **remote debugging**, run

 the following Docker command:

```bash
docker run -v /path/to/main-rootfs:/work -v /path/to/src:/src -it gdb-scripts gdb_remote -i 192.168.183.132 -u gdb_user -pid 3789 -w ../workspace -p 3434 -a powerpc:common -s /path/to/src -ui vscode
```

### Important Notes:
- **`/src`**: The source code directory should be mounted as a volume to `/src` inside the Docker container. This ensures that the source code is available for debugging.
- **`/work`**: The main root filesystem should be mounted to `/work` inside the container. This is where the binaries, libraries, and necessary files for debugging reside.
- **`-s`**: Use the `-s` argument to specify the path to the source code (e.g., `/path/to/src`).
- **`-w`**: The workspace should be mounted to `/work` in the container.

This setup allows you to run both **remote debugging** and **coredump debugging** directly from Docker, keeping all your debugging tools and environment isolated within the container.
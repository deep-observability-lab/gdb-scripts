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
- [Configuration](#configuration)
- [Workflow](#workflow)
- [License](#license)

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
```bash
sudo python3 main.py -ip <REMOTE_IP> -u <USERNAME> -pid <PROCESS_ID> -password <PASSWORD> -arch <ARCHITECTURE>
```

## Example Command
```bash
sudo python3 main.py -ip 10.0.2.4 -u remote -pid 1832 -password 1234zremote -arch auto
```

## Argument Descriptions
- **-ip** / **--ip**: IP address of the remote machine (e.g., `-ip 192.168.5.5`).
- **-u** / **--username**: Username for authentication on the remote machine (e.g., `-u root`).
- **-pid** / **--process_id**: Process ID of the target application (e.g., `-pid 1832`).
- **-password** / **--password**: Password for authenticating on the remote machine.
- **-arch** / **--architecture**: Architecture of the cross-compiled binary. Use `auto` for auto-detection.

## Configuration
In the `config.py` file, there are several global variables to customize based on your system setup:
- **PORT**: Specify the port for `gdbserver` to use.
- **SOURCE_CODE_PATH**: The local path where the source code should be downloaded. Ensure that the binary file of the application exists in this path.
- **REMOTE_LIBRARY_PATH**: The remote path to libraries for the target application.

Configure these variables with values specific to your environment before running the tool.

## Workflow

1. **Run Initial Setup**: The script takes the following command as input:
   ```bash
   sudo python3 main.py -ip 10.0.2.4 -u victim -pid 1832 -password 1234zahra -arch auto
   ```
   This command uses the IP address, username, process ID, password, and architecture type to connect to the remote machine.

2. **Update Configuration**: Update global variables in `config.py` to reflect system-specific values for your environment.

3. **Source Code Download**: The script automatically downloads the program’s source code to the specified path on the user’s computer.

4. **Install Dependencies**: Installs necessary dependencies, such as:
   - `gdb-multiarch`
   - `gnome-terminal`
   - Relevant Python packages

5. **Start `gdbserver` on Remote Machine**: After setup, the script initiates `gdbserver` on the remote machine at the port specified in `config.py`.

6. **Launch `gdb` Locally**: On the local machine, `gdb` is launched to begin debugging. A custom script is executed within `gdb` to set the correct paths for the source code.

7. **Debugging Process**: After configuring, the user can start debugging the specified process.

8. **Exit and Cleanup**: After debugging, the user can run the command:
   ```bash
   exit_gdb
   ```
   This command stops the `gdbserver` on the remote machine and detaches from the process. The local `gdb` instance will also exit.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

You can copy and paste this Markdown text directly into your Markdown file. Let me know if you need any further changes!

import os
import subprocess
from ssh_utils import SSHConnection
import config as cnf

class setup_local: 
    def __init__(self, ip, user, pwd): 
        self.ssh_client = SSHConnection(ip=ip, username=user, password=pwd)
        self.ssh_client.connect() 

    def close(self):
        self.ssh_client.close()

    def is_package_installed(self, package_name):
        """Check if a package is installed."""
        result = subprocess.run(
            ["dpkg", "-l", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0

    def install_gnome_terminal(self):
        package_name = "gnome-terminal"
        print("Checking installation status of {}...".format(package_name))
        if not self.is_package_installed(package_name):
            print("gnome-terminal not found. Installing...")
            try:
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y", "gnome-terminal"], check=True)
                print("gnome-terminal installed successfully.")
            except subprocess.CalledProcessError as e:
                print("Failed to install gnome-terminal.")
                print(e)

    def install_gdb_multiarch(self):
        package_name = "gdb-multiarch"
        print("Checking installation status of {}...".format(package_name))
        if not self.is_package_installed(package_name):
            print("{} is not installed. Installing...".format(package_name))
            try:
                subprocess.run(["sudo", "apt", "install", package_name, "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                print("{} installed successfully!\n".format(package_name))
            except subprocess.CalledProcessError as e:
                print("Error: Failed to install {} with return code {}. Please check your package manager.".format(package_name, e.returncode))
                exit(e.returncode)
        else:
            print("{} is already installed.\n".format(package_name))

    def setup_local(self): 
        self.install_gnome_terminal()
        self.install_gdb_multiarch()

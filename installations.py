import os
import subprocess

def install_gdb_multiarch():
    try:
        subprocess.run(["sudo", "apt", "install", "gdb-multiarch"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install gdb-multiarch with return code {e.returncode}")

def check_docker_install():
    try:
        if subprocess.run(["command", "-v", "docker"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
            print("hereee 1")
            subprocess.run(["sudo", "apt-get", "update"])
            subprocess.run(["sudo", "apt-get", "install", "-y", "docker.io", "docker-compose"])
            subprocess.run(["sudo", "usermod", "-aG", "docker", os.environ['USER']])
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install docker with return code {e.returncode}")

def installation() : 
    install_gdb_multiarch()
    check_docker_install()


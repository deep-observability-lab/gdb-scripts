import paramiko

class SSHConnection:
    def __init__(self, ip, username, password=None, private_key=None, port=22):
        self.ip = ip
        self.username = username
        self.password = password
        self.private_key = private_key
        self.port = port
        self.client = None

    def connect(self):
        """Establish SSH connection."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.private_key:
                key = paramiko.RSAKey.from_private_key_file(self.private_key)
                self.client.connect(self.ip, username=self.username, pkey=key, port=self.port)
            else:
                # If using password
                self.client.connect(self.ip, username=self.username, password=self.password, port=self.port)
            print(f"Connected to {self.ip}")
        except Exception as e:
            print(f"Failed to connect to {self.ip}: {e}")
            raise e

    def run_command(self, command):
        """Run a command on the remote machine via SSH."""
        if not self.client:
            raise Exception("No SSH connection established.")
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            if error:
                print(f"Error running command: {error}")
            return output, error
        except Exception as e:
            print(f"Failed to run command '{command}': {e}")
            raise e

    def transfer_file(self, local_path, remote_path):
        """Transfer a file to the remote machine via SFTP."""
        if not self.client:
            raise Exception("No SSH connection established.")
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            print(f"Transferred {local_path} to {remote_path}")
        except Exception as e:
            print(f"Failed to transfer {local_path} to {remote_path}: {e}")
            raise e

    def download_file(self, remote_path, local_path):
        """Download a file from the remote machine via SFTP."""
        if not self.client:
            raise Exception("No SSH connection established.")
        try:
            sftp = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            print(f"Downloaded {remote_path} to {local_path}")
        except Exception as e:
            print(f"Failed to download {remote_path}: {e}")
            raise e

    def close(self):
        """Close the SSH connection."""
        if self.client:
            self.client.close()
            print(f"Disconnected from {self.ip}")

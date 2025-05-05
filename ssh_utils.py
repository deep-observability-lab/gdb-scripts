import paramiko
import sys
import time

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
        retries = 3
        for attempt in range(retries):
            try:
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                if self.private_key:
                    key = paramiko.RSAKey.from_private_key_file(self.private_key)
                    self.client.connect(
                        self.ip,
                        username=self.username,
                        pkey=key,
                        port=self.port,
                        timeout=60,
                        banner_timeout=60,
                        auth_timeout=60)
                else:
                    self.client.connect(
                        self.ip,
                        username=self.username,
                        password=self.password,
                        port=self.port,
                        timeout=60,
                        banner_timeout=60,
                        auth_timeout=60)
                print(f"Connected to {self.ip}")
                return
            except Exception as e:
                print(f"[Attempt {attempt+1}] SSH connection failed: {e}")
                if attempt < retries - 1:
                    time.sleep(5)
                else:
                    sys.exit(1)
            except paramiko.AuthenticationException:
                print(f"Authentication failed for {self.username}@{self.ip}. Please check your credentials.")
                sys.exit(1)  # Exit the script with error code 1

            except paramiko.SSHException as e:
                print(f"SSH error while connecting to {self.ip}: {e}")
                sys.exit(1)

            except Exception as e:
                print(f"Failed to connect to {self.ip}: {e}")
                sys.exit(1)


    def run_command(self, command):
        import time
        """Run a command on the remote machine via SSH."""
        if not self.client:
            raise Exception("No SSH connection established.")
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            time.sleep(1)
            error = stderr.read().decode()
            output = stdout.read().decode()
            if error and "[sudo] password for" not in error:
                print(
                    "Error running command: {} command : {}".format(
                        error, command))
            return output, error

        except Exception as e:
            print("Failed to run command '{}': {}".format(command, e))
            if error:
                print("Error running command :{}".format(error))
            raise e
        finally:
            stdin.close()
            stdout.close()
            stderr.close()

    def transfer_file(self, local_path, remote_path):
        """Transfer a file to the remote machine via SFTP."""
        if not self.client:
            raise Exception("No SSH connection established.")
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            print("Transferred {} to {}".format(local_path, remote_path))
        except Exception as e:
            print(
                "Failed to transfer {} to {}: {}".format(
                    local_path, remote_path, e))
            raise e

    def download_file(self, remote_path, local_path):
        """Download a file from the remote machine via SFTP."""
        if not self.client:
            raise Exception("No SSH connection established.")
        try:
            sftp = self.client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            print("Downloaded {} to {}".format(remote_path, local_path))
        except Exception as e:
            print("Failed to download {}: {}".format(remote_path, e))
            raise e

    def close(self):
        """Close the SSH connection."""
        if self.client:
            self.client.close()
            print("Disconnected from {}".format(self.ip))

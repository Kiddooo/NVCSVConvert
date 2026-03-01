"""
Server Manager Module
=====================

Handles SSH connections, file uploads/downloads, and remote command execution.
"""

import getpass
import hashlib
import json
import os
import socket
from contextlib import contextmanager, nullcontext  # Fixed import
from pathlib import Path
from typing import Any, Dict, Optional, Union

import paramiko
from dotenv import load_dotenv

from constants import console

# Load environment variables from .env file
load_dotenv()
SERVER_HOST = os.getenv("SERVER_HOST")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")
SERVER_USERNAME = os.getenv("SERVER_USERNAME")


def validate_env_variables():
    """
    Validate that all required environment variables are set.

    Raises:
        EnvironmentError: If any required variable is missing
    """
    required_vars = {
        "SERVER_HOST": SERVER_HOST,
        "SSH_KEY_PATH": SSH_KEY_PATH,
        "SERVER_USERNAME": SERVER_USERNAME,
    }

    missing_vars = [var for var, value in required_vars.items() if not value]

    if missing_vars:
        console.print("[red]Missing required environment variables[/red]")
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


class SSHConnectionError(Exception):
    """Custom exception for SSH connection issues"""

    pass


class ServerManager:
    def __init__(self):
        self._ssh_client = None
        validate_env_variables()
        console.print("[green]ServerManager initialized successfully[/green]")

    def calculate_local_hash(self, file_path: Union[str, Path]) -> str:
        """
        Calculate MD5 hash of a local file.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            console.print(f"[red]File not found:[/red] {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @contextmanager
    def get_ssh_connection(self, passphrase: Optional[str] = None, timeout: int = 30):
        """
        Context manager for SSH connection.
        """
        ssh_client = None
        try:
            ssh_client = self.connect_to_server(passphrase, timeout)
            yield ssh_client
        finally:
            if ssh_client:
                ssh_client.close()
                console.print("[blue]SSH connection closed[/blue]")

    def connect_to_server(
        self, passphrase: Optional[str] = None, timeout: int = 30
    ) -> paramiko.SSHClient:
        """
        Establish SSH connection to the server.
        """
        ssh_client = paramiko.SSHClient()

        try:
            ssh_client.load_system_host_keys()
        except FileNotFoundError:
            console.print("[yellow]No known hosts file found[/yellow]")

        try:
            if passphrase is None:
                passphrase = os.getenv("SSH_PASSPHRASE")
                if passphrase is None:
                    passphrase = getpass.getpass("Enter SSH key passphrase: ")

            pkey = paramiko.Ed25519Key.from_private_key_file(
                SSH_KEY_PATH, password=passphrase
            )

            console.print("[blue]Connecting to server...[/blue]")
            ssh_client.connect(
                hostname=SERVER_HOST,
                username=SERVER_USERNAME,
                pkey=pkey,
                timeout=timeout,
                port=2222,
            )
            console.print("[green]Successfully connected to server[/green]")
            return ssh_client

        except paramiko.AuthenticationException as e:
            error_msg = f"Authentication failed: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            ssh_client.close()
            raise SSHConnectionError(error_msg)
        except paramiko.SSHException as e:
            error_msg = f"SSH exception occurred: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            ssh_client.close()
            raise SSHConnectionError(error_msg)
        except socket.error as e:
            error_msg = f"Socket error occurred: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            ssh_client.close()
            raise SSHConnectionError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error occurred: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            ssh_client.close()
            raise SSHConnectionError(error_msg)

    def execute_command(
        self, command: str, ssh_client: Optional[paramiko.SSHClient] = None
    ) -> Dict[str, Any]:
        """
        Execute a command on the remote server.
        """
        result = {"stdout": "", "stderr": "", "return_code": -1}

        try:
            with (
                self.get_ssh_connection()
                if ssh_client is None
                else nullcontext(ssh_client) as client
            ):
                console.print(f"[blue]Executing command:[/blue] {command}")
                stdin, stdout, stderr = client.exec_command(command)
                result["stdout"] = stdout.read().decode().strip()
                result["stderr"] = stderr.read().decode().strip()
                result["return_code"] = stdout.channel.recv_exit_status()

                if result["return_code"] != 0:
                    console.print(f"[red]Command failed:[/red] {command}")
                    console.print(f"[red]Exit code:[/red] {result['return_code']}")
                    console.print(f"[red]stderr:[/red] {result['stderr']}")
                else:
                    console.print("[green]Command executed successfully[/green]")

                return result

        except Exception as e:
            error_msg = f"Error executing command '{command}': {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            raise SSHConnectionError(error_msg)

    def calculate_remote_hash(
        self, remote_path: str, ssh_client: Optional[paramiko.SSHClient] = None
    ) -> str:
        """
        Calculate MD5 hash of a remote file.
        """
        command = f"md5sum {remote_path} | cut -d' ' -f1"
        result = self.execute_command(command, ssh_client)

        if result["return_code"] != 0:
            error_msg = f"Failed to calculate remote hash: {result['stderr']}"
            console.print(f"[red]{error_msg}[/red]")
            raise SSHConnectionError(error_msg)

        return result["stdout"]

    def upload_file_to_server(
        self,
        local_path: Union[str, Path],
        remote_path: str,
        ssh_client: Optional[paramiko.SSHClient] = None,
    ) -> bool:
        """
        Upload a file to the remote server.
        """
        local_path = Path(local_path)
        if not local_path.exists():
            console.print(f"[red]Local file not found:[/red] {local_path}")
            raise FileNotFoundError(f"Local file not found: {local_path}")

        try:
            with (
                self.get_ssh_connection()
                if ssh_client is None
                else nullcontext(ssh_client) as client
            ):
                console.print(
                    f"[blue]Uploading file[/blue] {local_path} [blue]to[/blue] {remote_path}"
                )
                sftp = client.open_sftp()

                # Create remote directory if it doesn't exist
                remote_dir = os.path.dirname(remote_path)
                self.execute_command(f"mkdir -p {remote_dir}", client)

                # Upload file
                sftp.put(str(local_path), remote_path)

                # Verify upload
                local_hash = self.calculate_local_hash(local_path)
                remote_hash = self.calculate_remote_hash(remote_path, client)

                if local_hash != remote_hash:
                    console.print(
                        "[red]File upload verification failed: hash mismatch[/red]"
                    )
                    raise SSHConnectionError(
                        "File upload verification failed: hash mismatch"
                    )

                console.print(
                    f"[green]Successfully uploaded[/green] {local_path} [green]to[/green] {remote_path}"
                )
                return True

        except Exception as e:
            error_msg = f"Error uploading file {local_path}: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            raise SSHConnectionError(error_msg)

    def download_file_from_server(
        self,
        remote_path: str,
        local_path: Union[str, Path],
        ssh_client: Optional[paramiko.SSHClient] = None,
    ) -> bool:
        """
        Download a file from the remote server.
        """
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with (
                self.get_ssh_connection()
                if ssh_client is None
                else nullcontext(ssh_client) as client
            ):
                console.print(
                    f"[blue]Downloading file[/blue] {remote_path} [blue]to[/blue] {local_path}"
                )
                sftp = client.open_sftp()

                # Download file
                sftp.get(remote_path, str(local_path))

                # Verify download
                local_hash = self.calculate_local_hash(local_path)
                remote_hash = self.calculate_remote_hash(remote_path, client)

                if local_hash != remote_hash:
                    local_path.unlink()  # Remove corrupted file
                    console.print(
                        "[red]File download verification failed: hash mismatch[/red]"
                    )
                    raise SSHConnectionError(
                        "File download verification failed: hash mismatch"
                    )

                console.print(
                    f"[green]Successfully downloaded[/green] {remote_path} [green]to[/green] {local_path}"
                )
                return True

        except Exception as e:
            error_msg = f"Error downloading file {remote_path}: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            raise SSHConnectionError(error_msg)

    def update_version_on_server(
        self,
        version_info: Dict[str, Any],
        remote_path: str,
        ssh_client: Optional[paramiko.SSHClient] = None,
    ) -> bool:
        """
        Update version information on the remote server.
        """
        try:
            console.print("[blue]Updating version information on server...[/blue]")
            # Create temporary file with version info
            temp_file = Path("temp_version.json")
            with temp_file.open("w") as f:
                json.dump(version_info, f)

            # Upload to server
            success = self.upload_file_to_server(temp_file, remote_path, ssh_client)

            # Cleanup
            temp_file.unlink()

            if success:
                console.print(
                    f"[green]Successfully updated version info at[/green] {remote_path}"
                )

            return success

        except Exception as e:
            error_msg = f"Error updating version info: {str(e)}"
            console.print(f"[red]{error_msg}[/red]")
            raise SSHConnectionError(error_msg)


class nullcontext:
    """Context manager that does nothing"""

    def __init__(self, enter_result=None):
        self.enter_result = enter_result

    def __enter__(self):
        return self.enter_result

    def __exit__(self, *excinfo):
        pass

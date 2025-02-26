import getpass
import hashlib
import logging
import os
import tempfile

import paramiko
from colorama import Fore
from dotenv import load_dotenv

load_dotenv()
SERVER_HOST = os.getenv("SERVER_HOST")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")
SERVER_USERNAME = os.getenv("SERVER_USERNAME")


def calculate_local_hash(local_path):
    md5 = hashlib.md5()
    with open(local_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()


def connect_to_server(passphrase=None):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if passphrase is None:
            passphrase = os.environ.get("SSH_PASSPHRASE")
            if passphrase is None:
                passphrase = getpass.getpass("Enter SSH key passphrase: ")

        pkey = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH, password=passphrase)

        ssh_client.connect(hostname=SERVER_HOST, username=SERVER_USERNAME, pkey=pkey)
        return ssh_client

    except Exception as e:
        logging.error(f"{Fore.LIGHTRED_EX}Error connecting to server: {str(e)}")
        raise


def execute_command(ssh_client, command):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode("utf-8").strip()
        error = stderr.read().decode("utf-8").strip()

        if error:
            logging.error(
                f"{Fore.LIGHTRED_EX}Error executing command '{command}': {error}"
            )
            raise Exception(error)

        return output
    except Exception:
        logging.exception(
            f"{Fore.LIGHTRED_EX}Exception occurred while executing command '{command}'"
        )
        raise


def calculate_remote_hash(ssh_client, remote_path):
    try:
        command = f"md5sum {remote_path}"
        output = execute_command(ssh_client, command)
        # md5sum output format: <hash> <filename>
        hash_value = output.split()[0]
        return hash_value
    except Exception as e:
        logging.error(f"{Fore.LIGHTRED_EX}Error calculating remote hash: {str(e)}")
        return None


def upload_file_to_server(ssh_client, local_path, remote_path):
    sftp_client = ssh_client.open_sftp()

    try:
        logging.debug(f"{Fore.WHITE}Attempting to upload {local_path} to {remote_path}")

        local_hash = calculate_local_hash(local_path)

        command = f"[ -f {remote_path} ] && echo True || echo False"
        file_exists = execute_command(ssh_client, command).lower() == "true"

        if file_exists:
            remote_hash = calculate_remote_hash(ssh_client, remote_path)

            if remote_hash == local_hash:
                logging.info(
                    f"{Fore.WHITE}No need to upload {local_path}. Hashes match."
                )
                return

        # Create a temporary file for download (if needed) and ensure it's closed properly
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                # Download the remote file temporarily to compare hashes
                download_success = download_file_from_server(
                    ssh_client, remote_path, temp_file.name
                )

                if download_success:
                    remote_hash = calculate_local_hash(temp_file.name)

                    if remote_hash == local_hash:
                        logging.info(
                            f"{Fore.WHITE}No need to upload {local_path}. Hashes match."
                        )
                        return

            except Exception as e:
                logging.error(
                    f"{Fore.LIGHTRED_EX}Error processing temporary file: {str(e)}"
                )

            finally:
                # Ensure the temporary file is closed and deleted
                temp_file.close()
                os.unlink(temp_file.name)

        sftp_client.put(local_path, remote_path)
        logging.info(
            f"{Fore.LIGHTGREEN_EX}Successfully uploaded {local_path} to {remote_path}"
        )
        update_version_on_server(ssh_client)

    except Exception as e:
        logging.error(f"{Fore.LIGHTRED_EX}Error uploading file: {str(e)}")
        raise
    finally:
        sftp_client.close()


def download_file_from_server(ssh_client, remote_path, local_temp_path):
    sftp_client = ssh_client.open_sftp()

    try:
        logging.debug(
            f"{Fore.WHITE}Attempting to download {remote_path} to {local_temp_path}"
        )

        with open(local_temp_path, "wb") as local_file:
            sftp_client.getfo(remote_path, local_file)

        logging.info(
            f"{Fore.LIGHTGREEN_EX}Successfully downloaded {remote_path} to {local_temp_path}"
        )

        return True
    except IOError as e:
        if e.errno == 2:  # File not found error
            logging.warning(
                f"{Fore.LIGHTYELLOW_EX}File {remote_path} does not exist on the server"
            )
        else:
            logging.error(f"Error downloading file: {str(e)}")
        return False
    finally:
        sftp_client.close()


def update_version_on_server(ssh_client):
    try:
        current_version = float(
            execute_command(ssh_client, "cat /var/www/files/shops_version.txt")
        )
        new_version = (
            round(current_version + 0.1, 1)
            if current_version % 1 != 0
            else int(current_version + 1)
        )

        execute_command(
            ssh_client, f"echo {new_version} > /var/www/files/shops_version.txt"
        )
        logging.info(
            f"{Fore.LIGHTGREEN_EX}Updated shops_version.txt to version {new_version}"
        )
    except Exception as e:
        logging.error(f"{Fore.LIGHTRED_EX}Error updating version on server: {str(e)}")
        raise

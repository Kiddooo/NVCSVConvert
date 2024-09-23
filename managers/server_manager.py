import getpass
import hashlib
import logging
import os

import paramiko
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
        logging.error(f"Error connecting to server: {str(e)}")
        raise


def execute_command(ssh_client, command):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode("utf-8").strip()
        error = stderr.read().decode("utf-8").strip()

        if error:
            logging.error(f"Error executing command '{command}': {error}")
            raise Exception(error)

        return output
    except Exception as e:
        logging.exception(f"Exception occurred while executing command '{command}'")
        raise


def upload_file_to_server(ssh_client, local_path, remote_path):
    sftp_client = ssh_client.open_sftp()

    try:
        logging.debug(f"Attempting to upload {local_path} to {remote_path}")

        sftp_client.put(local_path, remote_path)
        logging.info(f"Successfully uploaded {local_path} to {remote_path}")

    except Exception as e:
        logging.error(f"Error uploading file: {str(e)}")
        raise
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
        logging.info(f"Updated shops_version.txt to version {new_version}")
    except Exception as e:
        logging.error(f"Error updating version on server: {str(e)}")
        raise

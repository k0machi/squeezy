#!/usr/bin/env python3
import argparse
import os
import pathlib
import subprocess
import datetime
import hashlib
import codecs
import logging
import sys

REPO_LINK="https://git.komachi.sh/komachi/squidproxy-ez-gui"
BUILD_DIR=pathlib.Path(
        "/tmp/squeezy_" 
        + datetime.datetime.now().strftime("%Y-%m-%d") 
        +  "_" 
        + str(codecs.encode(os.urandom(10), "hex"), encoding="utf-8")
    ).absolute() 
GENERATED_SECRET_KEY = hashlib.sha256(os.urandom(128)).hexdigest()
GENERATED_SALT = hashlib.sha256(os.urandom(128)).hexdigest()
CONTAINER_TAG = "squeezy-prod"

def init_log():
    formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel("INFO")

def check_prereqs():
    try:
        git: subprocess.CompletedProcess = subprocess.run(args=["git", "version"], check=True, capture_output=True)
        docker: subprocess.CompletedProcess = subprocess.run(args=["docker", "ps"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error("This script requires git to be present and docker daemon to be operable by the current user")
        exit(1)
    
    return True
    

def clone_repo():
    logging.info("Downloading Squeezy source...")
    git_clone_proc: subprocess.CompletedProcess = subprocess.run(args=["git", "clone", REPO_LINK, BUILD_DIR], check=True)

def build_image():
    logging.info("Building container image...")
    docker_build: subprocess.CompletedProcess = subprocess.run(args=["docker", "build", "-t", CONTAINER_TAG, BUILD_DIR], check=True)

def start_container(options: argparse.Namespace):
    logging.info("Starting container...")
    container: subprocess.CompletedProcess = subprocess.run(
        args=[
            "docker",
            "run",
            "-e", f"SECRET_KEY={options.secret_key}",
            "-e", f"SECURITY_PASSWORD_SALT={options.password_salt}",
            "-d",
            "-p", f"0.0.0.0:{options.proxy_port}:3128/tcp",
            "-p", f"0.0.0.0:{options.webui_port}:8080/tcp",
            f"{CONTAINER_TAG}:latest"
        ],
        check=True,
        capture_output=True
    )

    return container.stdout

def main():
    init_log()
    check_prereqs()
    parser = argparse.ArgumentParser(epilog="Builds and sets up Squeezy container on the current machine")
    parser.add_argument('-k', '--secret-key', action="store", type=str, required=False, default=GENERATED_SECRET_KEY, help="Flask secret key")
    parser.add_argument('-s', '--password-salt', action="store", type=str, required=False, default=GENERATED_SALT, help="Database password salt")
    parser.add_argument('-p', '--proxy-port', action="store", type=int, required=False, default="3128", help="Squid Proxy Access Port")
    parser.add_argument('-w', '--webui-port', action="store", type=int, required=False, default="8080", help="Squeezy WebUI Port")

    args = parser.parse_args()

    try:
        clone_repo()
        build_image()
        container_id = start_container(args)
        logging.info("Squeezy has been successfully installed! Container ID: %s" % (str(container_id, encoding="utf-8"),))
    except Exception as e:
        logging.critical(f"Something went wrong during the install phase: {e.args}")
        exit(1)

    exit(0)


if __name__ == "__main__":
    main()
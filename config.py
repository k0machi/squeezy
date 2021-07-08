from dotenv import dotenv_values
from flask import Flask
import os

ENVIRONMENT = {
    **dotenv_values(".env.shared"),
    **dotenv_values(".env.local"),
    **os.environ,
}

_app = Flask("Config")
ENVIRONMENT["INSTANCE_PATH"] = _app.instance_path.rstrip("instance")
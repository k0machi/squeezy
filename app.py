from flask import Flask
from dotenv import load_dotenv

app = Flask("World")

@app.route("/")
def hello_world():
    return "<h1>Hello World</h1>"
from flask import Flask, render_template
from dotenv import load_dotenv

app = Flask("World")

@app.route("/")
def hello_world():
    return render_template("index.html", title="Hello")
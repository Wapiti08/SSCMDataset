from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello"

@app.route("/debug")
def debug():
    return open(".env").read()  # simulate credential leak

app.run(host="0.0.0.0", port=5000)

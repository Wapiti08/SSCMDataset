from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello"

@app.route("/debug")
def debug():
    return open(".env").read()  # 模拟凭据泄露

app.run(host="0.0.0.0", port=5000)

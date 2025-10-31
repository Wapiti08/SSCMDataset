'''
 # @ Create Time: 2025-04-10 12:45:39
 # @ Modified time: 2025-04-10 12:45:44
 # @ Description: server side code to receive sent compressed package
 '''

from flask import Flask, request
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    if file:
        # create new filename
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        # build new filepath 
        filepath = UPLOAD_FOLDER.joinpath(filename)
        # save file to filepath
        file.save(filename)

        return f"[+] File saved to {filepath}", 200
    
    return f"[-] No file uploaded", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

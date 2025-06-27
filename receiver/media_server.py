from flask import Flask, send_from_directory
import os

app = Flask(__name__)
MEDIA_DIR = "media"

@app.route('/media/<path:filename>')
def serve_media(filename: str):
    return send_from_directory(MEDIA_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8181)

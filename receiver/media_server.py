from flask import Flask, send_from_directory
from pathlib import Path

app = Flask(__name__)

MEDIA_DIR = Path(__file__).resolve().parent / 'media'

@app.route('/media/<path:filename>')
def serve_media(filename: str):
    return send_from_directory(MEDIA_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)

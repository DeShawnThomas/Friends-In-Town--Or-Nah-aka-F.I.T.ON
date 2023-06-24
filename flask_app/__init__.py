from flask import Flask
import os
app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = "the grind don't stop"

social_media_icons = {
    "facebook": "facebook-logo.png",
    "twitter": "twitter-logo.png",
    "instagram": "instagram-logo.png",
    "linkedin": "linkedin-logo.png",
    "snapchat": "snapchat-logo.png",
    "tiktok": "tiktok-logo.png",
}


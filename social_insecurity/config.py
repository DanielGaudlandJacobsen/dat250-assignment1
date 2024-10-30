"""Provides the configuration for the Social Insecurity application.

This file is used to set the configuration for the application.

Example:
    from flask import Flask
    from social_insecurity.config import Config

    app = Flask(__name__)
    app.config.from_object(Config)

    # Use the configuration
    secret_key = app.config["SECRET_KEY"]
"""

import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24).hex()  # TODO: Use this with wtforms
    SQLITE3_DATABASE_PATH = "sqlite3.db"  # Path relative to the Flask instance folder
    UPLOADS_FOLDER_PATH = os.path.join("uploads")  # Path relative to the Flask instance folder
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}  # TODO: Might use this at some point, probably don't want people to upload any file type
    WTF_CSRF_ENABLED = True  # TODO: I should probably implement this wtforms feature, but it's not a priority
    
    # Konfigurasjon for Flask-WTF CSRF
    WTF_CSRF_SECRET_KEY = os.environ.get("WTF_CSRF_SECRET_KEY") or os.urandom(24).hex()
    # Maksimal filstørrelse som kan lastes opp (for eksempel 16MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 Megabytes


# Ekstra sikkerhet (valgfritt)
# Flask-Talisman kan brukes for å implementere HTTPS og ytterligere sikkerhetsoverskrifter
# EXEMPEL:
# TALISMAN_CONFIG = {
#     'content_security_policy': {
#         'default-src': '\'self\'',
#         'img-src': '*',
#         # Legg til andre policyer etter behov
#     }
# }

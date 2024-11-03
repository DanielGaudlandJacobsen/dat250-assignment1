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
    SECRET_KEY = os.environ.get("SECRET_KEY") or "din_hemmelige_nøkkel"
    SQLITE3_DATABASE_PATH = "sqlite3.db"  # Path relative to the Flask instance folder
    UPLOADS_FOLDER_PATH = "uploads"  # Path relative to the Flask instance folder
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "tiff"}  # Tillatte filtyper for opplasting
    WTF_CSRF_ENABLED = True  # Aktivert CSRF beskyttelse

    # Sikre sesjonskapsler
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"
    SESSION_COOKIE_SECURE = True

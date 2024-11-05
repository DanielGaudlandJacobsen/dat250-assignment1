# social_insecurity/__init__.py

from pathlib import Path
from shutil import rmtree
from typing import cast

from flask import Flask, current_app
from flask_login import LoginManager  # Fjernet kommentar
from flask_bcrypt import Bcrypt  # Fjernet kommentar
from flask_wtf.csrf import CSRFProtect  # Fjernet kommentar
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from social_insecurity.config import Config
from social_insecurity.database import SQLite3
from social_insecurity.models import User  # Sørg for at du har en models.py med User-klassen

# Initialiser utvidelser
sqlite = SQLite3()
login = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["50 per day", "20 per hour"])

@login.user_loader
def load_user(user_id):
    user_row = sqlite.get_user_by_id(int(user_id))
    if user_row:
        return User(id=user_row["id"], username=user_row["username"], password=user_row["password"])
    return None
def create_app(test_config=None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.from_object(test_config)

    # Initialiser utvidelsene
    sqlite.init_app(app, schema="schema.sql")
    login.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Oppsett av Flask-Talisman for sikkerhetshoder
    csp = {
        "default-src": [
            "'self'",
            "https://stackpath.bootstrapcdn.com",
            "https://maxcdn.bootstrapcdn.com",
            "https://cdn.jsdelivr.net",
        ]
    }
    talisman = Talisman(app, content_security_policy=csp, frame_options="DENY")

    with app.app_context():
        create_uploads_folder(app)

    @app.cli.command("reset")
    def reset_command() -> None:
        """Reset the app."""
        instance_path = Path(current_app.instance_path)
        if instance_path.exists():
            rmtree(instance_path)
    
    with app.app_context():
        import social_insecurity.routes  # noqa: E402,F401

    return app


def create_uploads_folder(app: Flask) -> None:
    """Create the instance and upload folders."""
    upload_path = Path(app.instance_path) / cast(str, app.config["UPLOADS_FOLDER_PATH"])
    if not upload_path.exists():
        upload_path.mkdir(parents=True)

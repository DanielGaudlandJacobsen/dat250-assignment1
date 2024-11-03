# social_insecurity/models.py

from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id: int, username: str, password: str):
        self.id = id
        self.username = username
        self.password = password

    def get_id(self) -> str:  # Added return type annotation
        return str(self.id)

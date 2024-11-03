from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

from social_insecurity import create_app

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient
from __future__ import annotations
from collections.abc import Iterator
from typing import TYPE_CHECKING
import pytest
from social_insecurity import create_app, sqlite
from social_insecurity.models import User


@pytest.fixture(scope="session")
def app() -> Iterator[Flask]:
    test_config = {
        "SQLITE3_DATABASE_PATH": "file::memory:?cache=shared",
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    }
    app = create_app(test_config)
    yield app


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


def test_request_index(client: FlaskClient):
    response = client.get("/")
    assert response.status_code == 200
    if TYPE_CHECKING:


    @pytest.fixture(scope="session")
    def app() -> Iterator[Flask]:
        test_config = {
            "SQLITE3_DATABASE_PATH": "file::memory:?cache=shared",
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
        }
        app = create_app(test_config)
        yield app


    @pytest.fixture()
    def client(app: Flask) -> FlaskClient:
        return app.test_client()


    @pytest.fixture()
    def init_db(app: Flask):
        with app.app_context():
            sqlite.query("""
                CREATE TABLE Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    first_name TEXT,
                    last_name TEXT,
                    password TEXT NOT NULL
                );
            """)
            sqlite.query("""
                CREATE TABLE FriendRequests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user_id INTEGER NOT NULL,
                    to_user_id INTEGER NOT NULL,
                    FOREIGN KEY (from_user_id) REFERENCES Users (id),
                    FOREIGN KEY (to_user_id) REFERENCES Users (id)
                );
            """)
            sqlite.query("""
                CREATE TABLE Friends (
                    u_id INTEGER NOT NULL,
                    f_id INTEGER NOT NULL,
                    FOREIGN KEY (u_id) REFERENCES Users (id),
                    FOREIGN KEY (f_id) REFERENCES Users (id)
                );
            """)
            sqlite.query("""
                CREATE TABLE Posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    u_id INTEGER NOT NULL,
                    content TEXT,
                    image TEXT,
                    creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (u_id) REFERENCES Users (id)
                );
            """)
            sqlite.query("""
                CREATE TABLE Comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    p_id INTEGER NOT NULL,
                    u_id INTEGER NOT NULL,
                    comment TEXT,
                    creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (p_id) REFERENCES Posts (id),
                    FOREIGN KEY (u_id) REFERENCES Users (id)
                );
            """)


    def test_request_index(client: FlaskClient):
        response = client.get("/")
        assert response.status_code == 200


    def test_handle_friend_request(client: FlaskClient, init_db):
        with client:
            # Create users
            sqlite.query("INSERT INTO Users (username, password) VALUES (?, ?)", ("user1", "password1"))
            sqlite.query("INSERT INTO Users (username, password) VALUES (?, ?)", ("user2", "password2"))

            # Log in as user1
            user1 = sqlite.get_user_by_username("user1")
            user_obj = User(id=user1["id"], username=user1["username"], password=user1["password"])
            with client.session_transaction() as sess:
                sess["_user_id"] = user_obj.get_id()

            # Send friend request from user1 to user2
            user2 = sqlite.get_user_by_username("user2")
            response = client.post("/handle_friend_request", data={"request_id": 1, "action": "accept"})
            assert response.status_code == 302  # Redirect to friends page

            # Check if friend request was accepted
            friends = sqlite.query("SELECT * FROM Friends WHERE u_id = ? AND f_id = ?", (user1["id"], user2["id"]))
            assert len(friends) == 1


    def test_index(client: FlaskClient, init_db):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Welcome" in response.data


    def test_logout(client: FlaskClient, init_db):
        with client:
            # Create user and log in
            sqlite.query("INSERT INTO Users (username, password) VALUES (?, ?)", ("user1", "password1"))
            user1 = sqlite.get_user_by_username("user1")
            user_obj = User(id=user1["id"], username=user1["username"], password=user1["password"])
            with client.session_transaction() as sess:
                sess["_user_id"] = user_obj.get_id()

            response = client.get("/logout")
            assert response.status_code == 302  # Redirect to index page
            assert b"You have been logged out." in response.data


    def test_stream(client: FlaskClient, init_db):
        with client:
            # Create user and log in
            sqlite.query("INSERT INTO Users (username, password) VALUES (?, ?)", ("user1", "password1"))
            user1 = sqlite.get_user_by_username("user1")
            user_obj = User(id=user1["id"], username=user1["username"], password=user1["password"])
            with client.session_transaction() as sess:
                sess["_user_id"] = user_obj.get_id()

            response = client.get("/stream")
            assert response.status_code == 200
            assert b"Stream" in response.data


    def test_comments(client: FlaskClient, init_db):
        with client:
            # Create users and log in
            sqlite.query("INSERT INTO Users (username, password) VALUES (?, ?)", ("user1", "password1"))
            sqlite.query("INSERT INTO Users (username, password) VALUES (?, ?)", ("user2", "password2"))
            user1 = sqlite.get_user_by_username("user1")
            user2 = sqlite.get_user_by_username("user2")
            user_obj = User(id=user1["id"], username=user1["username"], password=user1["password"])
            with client.session_transaction() as sess:
                sess["_user_id"] = user_obj.get_id()

            # Create post by user2
            sqlite.query("INSERT INTO Posts (u_id, content) VALUES (?, ?)", (user2["id"], "Test post"))

            response = client.get(f"/comments/{user2['username']}/1")
            assert response.status_code == 200
            assert b"Comments" in response.data


    def test_friends(client: FlaskClient, init_db):
        with client:
            # Create users and log in
            sqlite.query("INSERT INTO Users (username, password) VALUES (?, ?)", ("user1", "password1"))
            sqlite.query("INSERT INTO Users (username, password) VALUES (?, ?)", ("user2", "password2"))
            user1 = sqlite.get_user_by_username("user1")
            user2 = sqlite.get_user_by_username("user2")
            user_obj = User(id=user1["id"], username=user1["username"], password=user1["password"])
            with client.session_transaction() as sess:
                sess["_user_id"] = user_obj.get_id()

            response = client.get("/friends")
            assert response.status_code == 200
            assert b"Friends" in response.data


    def test_profile(client: FlaskClient, init_db):
        with client:
            # Create user and log in
            sqlite.query("INSERT INTO Users (username, password) VALUES (?, ?)", ("user1", "password1"))
            user1 = sqlite.get_user_by_username("user1")
            user_obj = User(id=user1["id"], username=user1["username"], password=user1["password"])
            with client.session_transaction() as sess:
                sess["_user_id"] = user_obj.get_id()

            response = client.get("/profile")
            assert response.status_code == 200
            assert b"Profile" in response.data


    def test_uploads(client: FlaskClient, init_db):
        with client:
            # Create user and log in
            sqlite.query("INSERT INTO Users (username, password) VALUES (?, ?)", ("user1", "password1"))
            user1 = sqlite.get_user_by_username("user1")
            user_obj = User(id=user1["id"], username=user1["username"], password=user1["password"])
            with client.session_transaction() as sess:
                sess["_user_id"] = user_obj.get_id()

            # Upload a file
            data = {
                "image": (io.BytesIO(b"fake image data"), "test.jpg")
            }
            response = client.post("/stream", data=data, content_type="multipart/form-data")
            assert response.status_code == 302  # Redirect to stream page

            # Access the uploaded file
            response = client.get("/uploads/test.jpg")
            assert response.status_code == 200
            assert response.mimetype.startswith("image/")


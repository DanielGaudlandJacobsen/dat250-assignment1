# social_insecurity/database.py

from __future__ import annotations

import sqlite3
from os import PathLike
from pathlib import Path
from typing import Any, Optional  # Removed unused import 'cast'

from flask import Flask, current_app, g


class SQLite3:
    """Provides a SQLite3 database extension for Flask."""

    def __init__(
        self,
        app: Optional[Flask] = None,
        *,
        path: Optional[PathLike | str] = None,
        schema: Optional[PathLike | str] = None,
    ) -> None:
        """Initializes the extension."""
        if app is not None:
            self.init_app(app, path=path, schema=schema)

    def init_app(
        self,
        app: Flask,
        *,
        path: Optional[PathLike | str] = None,
        schema: Optional[PathLike | str] = None,
    ) -> None:
        """Initializes the extension."""
        if not hasattr(app, "extensions"):
            app.extensions = {}

        if "sqlite3" not in app.extensions:
            app.extensions["sqlite3"] = self
        else:
            raise RuntimeError("Flask SQLite3 extension already initialized")

        instance_path = Path(app.instance_path)
        database_path = path or app.config.get("SQLITE3_DATABASE_PATH")

        if database_path:
            if ":memory:" in str(database_path):
                self._path = Path(database_path)
            else:
                self._path = instance_path / database_path
        else:
            raise ValueError("No database path provided to SQLite3 extension")

        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            if schema:
                with app.app_context():
                    self._init_database(schema)

        app.teardown_appcontext(self._close_connection)

    @property
    def connection(self) -> sqlite3.Connection:
        """Returns the connection to the SQLite3 database."""
        conn = getattr(g, "flask_sqlite3_connection", None)
        if conn is None:
            conn = sqlite3.connect(self._path)
            conn.row_factory = sqlite3.Row
            g.flask_sqlite3_connection = conn  # Fixed assignment to 'conn'
        return conn

    def query(self, query: str, params: tuple = (), one: bool = False) -> Any:
        """Queries the database and returns the result."""
        cursor = self.connection.execute(query, params)
        response = cursor.fetchone() if one else cursor.fetchall()
        cursor.close()
        self.connection.commit()
        return response

    def get_user_by_id(self, user_id: int) -> Optional[sqlite3.Row]:
        """Fetches a user from the database by their ID."""
        query = "SELECT * FROM Users WHERE id = ?;"
        return self.query(query, (user_id,), one=True)

    def get_user_by_username(self, username: str) -> Optional[sqlite3.Row]:
        """Fetches a user from the database by their username."""
        query = "SELECT * FROM Users WHERE username = ?;"
        return self.query(query, (username,), one=True)

    def _init_database(self, schema: PathLike | str) -> None:
        """Initializes the database with the supplied schema if it does not exist yet."""
        with current_app.open_resource(str(schema), mode="r") as file:
            self.connection.executescript(file.read())
            self.connection.commit()

    def _close_connection(self, exception: Optional[BaseException] = None) -> None:
        """Closes the connection to the database."""
        conn = getattr(g, "flask_sqlite3_connection", None)
        if conn is not None:
            conn.close()
            g.flask_sqlite3_connection = None  # Ensure the connection is removed from 'g'

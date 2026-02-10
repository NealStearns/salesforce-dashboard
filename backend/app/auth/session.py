"""Simple server-side session store.

Tokens are stored in-memory keyed by a cryptographically random session ID.
For production use, swap this for Redis or a database-backed store.
"""

import secrets
from typing import Any

_sessions: dict[str, dict[str, Any]] = {}


def create_session(data: dict) -> str:
    """Create a new session and return its ID."""
    session_id = secrets.token_urlsafe(32)
    _sessions[session_id] = data
    return session_id


def get_session(session_id: str) -> dict | None:
    """Retrieve session data, or None if expired/missing."""
    return _sessions.get(session_id)


def update_session(session_id: str, data: dict) -> None:
    """Merge new data into an existing session."""
    if session_id in _sessions:
        _sessions[session_id].update(data)


def delete_session(session_id: str) -> None:
    """Remove a session."""
    _sessions.pop(session_id, None)

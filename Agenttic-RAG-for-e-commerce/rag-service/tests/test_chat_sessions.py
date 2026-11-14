from uuid import UUID

import pytest


SESSION = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"


def chat(client, message, token=None, session=SESSION, **extra):
    body = {"message": message, **extra}
    if session is not None:
        body["session_id"] = session
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = client.post("/chat", json=body, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.parametrize("session", [None, ""])
def test_missing_session_generates_new_uuid_and_separate_history(client, session):
    first = chat(client, "private first request", session=session)
    second = chat(client, "independent second request", session=session)
    assert UUID(first["session_id"]).version == 4
    assert UUID(second["session_id"]).version == 4
    assert first["session_id"] != second["session_id"]
    assert second["reply"] == "independent second request"


def test_same_session_cannot_share_history_between_users(client):
    chat(client, "private message A", token="token-a")
    second = chat(client, "private message B", token="token-b")
    assert second["reply"] == "private message B"
    assert chat(client, "follow-up A", token="token-a")["reply"] == "private message A | follow-up A"


def test_authenticated_history_is_separate_from_guest_with_same_session(client):
    chat(client, "signed-in private message", token="token-a")
    assert chat(client, "guest message")["reply"] == "guest message"


def test_invalid_token_cannot_resume_authenticated_history(client):
    chat(client, "signed-in private message", token="token-a")
    assert chat(client, "invalid token message", token="invalid")["reply"] == "invalid token message"


def test_same_user_and_session_preserve_history(client):
    first = chat(client, "first", token="token-a")
    second = chat(client, "second", token="token-a")
    assert second["reply"] == "first | second"
    assert first["session_id"] == second["session_id"] == SESSION


def test_same_user_different_sessions_are_independent(client):
    chat(client, "first session", token="token-a")
    other = chat(client, "second session", token="token-a", session="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
    assert other["reply"] == "second session"


def test_refreshed_token_for_same_user_preserves_session(client):
    chat(client, "before token refresh", token="token-a")
    assert chat(client, "after token refresh", token="token-a-refreshed")["reply"] == "before token refresh | after token refresh"


def test_authorization_header_takes_precedence_over_body_token(client):
    chat(client, "private A", token="token-a")
    second = chat(client, "private B", token="token-b", user_token="token-a")
    assert second["reply"] == "private B"


def test_body_token_remains_supported(client):
    chat(client, "body A", user_token="token-a")
    assert chat(client, "body B", user_token="token-b")["reply"] == "body B"
    assert chat(client, "follow-up A", user_token="token-a")["reply"] == "body A | follow-up A"

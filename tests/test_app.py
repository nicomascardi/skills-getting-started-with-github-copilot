from copy import deepcopy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    """Restore in-memory activities after each test to avoid state leakage."""
    orig = deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(orig)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect at least one known activity
    assert "Basketball" in data


def test_signup_adds_participant():
    email = "tester@example.com"
    activity = "Basketball"

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]
    assert "Signed up" in resp.json().get("message", "")


def test_signup_duplicate_fails():
    activity = "Basketball"
    existing = activities[activity]["participants"][0]

    resp = client.post(f"/activities/{activity}/signup?email={existing}")
    assert resp.status_code == 400


def test_unregister_removes_participant():
    activity = "Chess Club"
    participant = activities[activity]["participants"][0]

    resp = client.post(f"/activities/{activity}/unregister?email={participant}")
    assert resp.status_code == 200
    assert participant not in activities[activity]["participants"]
    assert "Unregistered" in resp.json().get("message", "")


def test_unregister_nonexistent_returns_404():
    activity = "Chess Club"
    resp = client.post(f"/activities/{activity}/unregister?email=notfound@example.com")
    assert resp.status_code == 404


def test_signup_activity_not_found():
    resp = client.post("/activities/NotAnActivity/signup?email=test@example.com")
    assert resp.status_code == 404


def test_unregister_activity_not_found():
    resp = client.post("/activities/NotAnActivity/unregister?email=test@example.com")
    assert resp.status_code == 404

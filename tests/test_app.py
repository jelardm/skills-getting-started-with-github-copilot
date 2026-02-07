import copy

import pytest

from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def _clone_activities():
    return copy.deepcopy(activities)


def _restore_activities(snapshot):
    activities.clear()
    activities.update(snapshot)


def _unique_email(activity_name):
    email_prefix = activity_name.lower().replace(" ", "-").replace("/", "-")
    return f"test-{email_prefix}@mergington.edu"


@pytest.fixture(autouse=True)
def _reset_activities():
    snapshot = _clone_activities()
    yield
    _restore_activities(snapshot)


def test_get_activities_returns_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()

    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_adds_participant():
    activity_name = "Chess Club"
    email = _unique_email(activity_name)

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_rejected():
    activity_name = "Math Team"
    email = _unique_email(activity_name)

    first = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    second = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert first.status_code == 200
    assert second.status_code == 400


def test_unregister_removes_participant():
    activity_name = "Science Club"
    email = _unique_email(activity_name)

    signup = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    unregister = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    assert signup.status_code == 200
    assert unregister.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    activity_name = "Art Club"
    email = _unique_email(activity_name)

    response = client.post(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    assert response.status_code == 404

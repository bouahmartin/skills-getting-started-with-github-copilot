import urllib.parse

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activity keys
    assert "Chess Club" in data


def test_signup_and_remove_participant():
    activity = "Chess Club"
    email = "test_user@example.com"

    # Ensure email not present initially
    data = client.get("/activities").json()
    participants_before = list(data[activity]["participants"])
    assert email not in participants_before

    # Sign up the user
    signup_resp = client.post(f"/activities/{urllib.parse.quote(activity)}/signup", params={"email": email})
    assert signup_resp.status_code == 200
    assert "Signed up" in signup_resp.json().get("message", "")

    # Verify participant was added
    data_after_signup = client.get("/activities").json()
    assert email in data_after_signup[activity]["participants"]

    # Remove the participant
    del_resp = client.delete(f"/activities/{urllib.parse.quote(activity)}/participants", params={"email": email})
    assert del_resp.status_code == 200
    assert "Unregistered" in del_resp.json().get("message", "")

    # Verify participant was removed
    data_after_delete = client.get("/activities").json()
    assert email not in data_after_delete[activity]["participants"]


def test_remove_nonexistent_participant_returns_404():
    activity = "Chess Club"
    email = "no_such_user@example.com"

    # Make sure this email is not present
    data = client.get("/activities").json()
    if email in data[activity]["participants"]:
        # remove it first to ensure test condition
        client.delete(f"/activities/{urllib.parse.quote(activity)}/participants", params={"email": email})

    resp = client.delete(f"/activities/{urllib.parse.quote(activity)}/participants", params={"email": email})
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Participant not found"

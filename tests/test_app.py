import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities dict before each test
    app_module.activities = copy.deepcopy(original_activities)
    yield


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_unregister():
    email = "testuser@mergington.edu"
    # ensure not present
    resp = client.get("/activities")
    assert email not in resp.json()["Chess Club"]["participants"]

    # signup
    resp = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # now present
    resp = client.get("/activities")
    assert email in resp.json()["Chess Club"]["participants"]

    # unregister
    resp = client.post(f"/activities/Chess%20Club/unregister?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json()["message"]

    # removed
    resp = client.get("/activities")
    assert email not in resp.json()["Chess Club"]["participants"]


def test_signup_duplicate_fails():
    # michael@mergington.edu is pre-registered in Chess Club
    resp = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
    assert resp.status_code == 400


def test_unregister_non_member_fails():
    resp = client.post("/activities/Chess%20Club/unregister?email=nosuch@mergington.edu")
    assert resp.status_code == 400


def test_activity_not_found():
    resp = client.post("/activities/NoSuchActivity/signup?email=test@x")
    assert resp.status_code == 404
    resp = client.post("/activities/NoSuchActivity/unregister?email=test@x")
    assert resp.status_code == 404


def test_root_redirect():
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302, 307, 308)
    assert "/static/index.html" in resp.headers.get("location", "")

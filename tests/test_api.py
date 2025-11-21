"""Tests for the activities API endpoints"""
import pytest


class TestGetActivities:
    """Test GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that the activities endpoint returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that the activities endpoint returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_expected_keys(self, client):
        """Test that activities have the expected structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check that we have some activities
        assert len(data) > 0
        
        # Check structure of first activity
        first_activity = next(iter(data.values()))
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)

    def test_get_activities_has_chess_club(self, client):
        """Test that Chess Club activity exists"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "new_student@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]

    def test_signup_for_activity_not_found(self, client):
        """Test signing up for non-existent activity"""
        response = client.post(
            "/activities/Fake Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_already_registered(self, client):
        """Test signing up when already registered"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_adds_participant_to_list(self, client):
        """Test that signup actually adds participant to activity"""
        email = "test_user@mergington.edu"
        
        # Sign up
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Test DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_from_activity_success(self, client):
        """Test successfully unregistering from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]

    def test_unregister_from_activity_not_found(self, client):
        """Test unregistering from non-existent activity"""
        response = client.delete(
            "/activities/Fake Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregistering when not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "not_registered@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_removes_participant_from_list(self, client):
        """Test that unregister actually removes participant from activity"""
        email = "james@mergington.edu"  # In Basketball Team
        
        # Unregister
        response = client.delete(
            "/activities/Basketball Team/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities["Basketball Team"]["participants"]


class TestRootEndpoint:
    """Test GET / endpoint"""

    def test_root_redirects_to_index(self, client):
        """Test that root endpoint redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

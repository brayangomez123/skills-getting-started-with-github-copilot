"""
Backend tests for Mergington High School Activities API

Tests cover all endpoints using the AAA (Arrange-Act-Assert) pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


# Create a test client
client = TestClient(app)


class TestGetActivities:
    """Test cases for GET /activities endpoint"""

    def test_get_activities_returns_success(self):
        """
        ARRANGE: API is configured
        ACT: Make GET request to /activities
        ASSERT: Response should have status 200 and return activities dictionary
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert "Chess Club" in response.json()
        assert "Programming Class" in response.json()

    def test_get_activities_returns_expected_fields(self):
        """
        ARRANGE: API is configured
        ACT: Fetch activities
        ASSERT: Each activity has required fields
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants_are_populated(self):
        """
        ARRANGE: API is configured with sample participants
        ACT: Fetch activities
        ASSERT: Chess Club should have at least 2 participants
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert len(activities["Chess Club"]["participants"]) >= 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]


class TestSignupEndpoint:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """
        ARRANGE: Student email and valid activity
        ACT: Submit signup request
        ASSERT: Should return 200 and confirmation message
        """
        # Arrange
        test_email = "test.student@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 200
        assert "message" in response.json()
        assert test_email in response.json()["message"]

    def test_signup_adds_participant(self):
        """
        ARRANGE: Student email
        ACT: Sign up student, then fetch activities
        ASSERT: Student should appear in participants list
        """
        # Arrange
        test_email = "add.me@mergington.edu"
        activity_name = "Programming Class"

        # Act - Signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Act - Get activities
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert test_email in activities[activity_name]["participants"]

    def test_signup_duplicate_fails(self):
        """
        ARRANGE: Student already signed up
        ACT: Try to sign up again
        ASSERT: Should return 400 error
        """
        # Arrange
        test_email = "duplicate.test@mergington.edu"
        activity_name = "Gym Class"

        # Act - First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Act - Second signup attempt
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 400
        assert "Already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self):
        """
        ARRANGE: Activity that doesn't exist
        ACT: Try to signup for non-existent activity
        ASSERT: Should return 404 error
        """
        # Arrange
        test_email = "test@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_url_encoded_activity_name(self):
        """
        ARRANGE: Activity with spaces in name
        ACT: Signup with URL encoded activity name
        ASSERT: Should work correctly
        """
        # Arrange
        test_email = "encoded.test@mergington.edu"
        activity_name = "Programming Class"  # Has space in name

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 200


class TestUnregisterEndpoint:
    """Test cases for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """
        ARRANGE: Student is registered for activity
        ACT: Submit unregister request
        ASSERT: Should return 200 and confirmation message
        """
        # Arrange
        test_email = "unregister.test@mergington.edu"
        activity_name = "Art Club"

        # Arrange - Sign them up first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self):
        """
        ARRANGE: Student is registered
        ACT: Unregister and fetch activities
        ASSERT: Student should not be in participants
        """
        # Arrange
        test_email = "remove.me@mergington.edu"
        activity_name = "Drama Club"

        # Arrange - Sign them up
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )

        # Act - Unregister
        client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": test_email}
        )

        # Act - Get activities
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert test_email not in activities[activity_name]["participants"]

    def test_unregister_not_registered_fails(self):
        """
        ARRANGE: Student is not registered
        ACT: Try to unregister
        ASSERT: Should return 400 error
        """
        # Arrange
        test_email = "not.registered@mergington.edu"
        activity_name = "Debate Team"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self):
        """
        ARRANGE: Activity doesn't exist
        ACT: Try to unregister from non-existent activity
        ASSERT: Should return 404 error
        """
        # Arrange
        test_email = "test@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": test_email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRootEndpoint:
    """Test cases for GET / endpoint"""

    def test_root_redirects_to_index(self):
        """
        ARRANGE: Homepage request
        ACT: Make GET request to /
        ASSERT: Should redirect to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]

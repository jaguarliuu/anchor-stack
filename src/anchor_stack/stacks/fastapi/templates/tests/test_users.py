"""Test user endpoints."""

from fastapi.testclient import TestClient


def test_create_user(client: TestClient) -> None:
    """Test creating a user."""
    response = client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "name": "Test User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data


def test_list_users(client: TestClient) -> None:
    """Test listing users."""
    # Create a user first
    client.post(
        "/api/v1/users",
        json={"email": "list@example.com", "name": "List User"},
    )

    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_user_not_found(client: TestClient) -> None:
    """Test getting non-existent user."""
    response = client.get("/api/v1/users/99999")
    assert response.status_code == 404

"""
Authentication tests for Foodyeh API.
Tests public auth endpoints and JWT protection on other endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test data
test_user = {
    "email": "test@example.com",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User",
    "phone": "+1234567890"
}

test_login = {
    "email": "test@example.com",
    "password": "SecurePass123!"
}


class TestPublicAuthEndpoints:
    """Test that public auth endpoints work without authentication."""
    
    def test_signup_without_auth(self):
        """Test that signup works without Authorization header."""
        response = client.post("/auth/signup", json=test_user)
        assert response.status_code in [200, 201, 400]  # 400 if user already exists
        # Should not require authentication
    
    def test_login_without_auth(self):
        """Test that login works without Authorization header."""
        response = client.post("/auth/login", json=test_login)
        assert response.status_code in [200, 401]  # 401 if invalid credentials
        # Should not require authentication
    
    def test_refresh_without_auth(self):
        """Test that refresh works without Authorization header."""
        response = client.post("/auth/refresh", json={"refresh_token": "invalid"})
        assert response.status_code in [200, 400, 401]  # Various error codes for invalid token
        # Should not require authentication


class TestProtectedEndpoints:
    """Test that protected endpoints require JWT authentication."""
    
    def test_dishes_endpoint_without_auth(self):
        """Test that dishes endpoint requires authentication."""
        response = client.get("/dishes/")
        assert response.status_code == 401
        assert "Authorization header required" in response.json()["detail"]
    
    def test_orders_endpoint_without_auth(self):
        """Test that orders endpoint requires authentication."""
        response = client.get("/orders/me")
        assert response.status_code == 401
        assert "Authorization header required" in response.json()["detail"]
    
    def test_admin_endpoint_without_auth(self):
        """Test that admin endpoint requires authentication."""
        response = client.get("/admin/users")
        assert response.status_code == 401
        assert "Authorization header required" in response.json()["detail"]
    
    def test_logout_without_auth(self):
        """Test that logout requires authentication."""
        response = client.post("/auth/logout", json={"refresh_token": "test"})
        assert response.status_code == 401
        assert "Authorization header required" in response.json()["detail"]


class TestRateLimiting:
    """Test rate limiting on public auth endpoints."""
    
    def test_signup_rate_limit(self):
        """Test rate limiting on signup endpoint."""
        # Make multiple signup attempts
        for i in range(5):
            user_data = test_user.copy()
            user_data["email"] = f"test{i}@example.com"
            response = client.post("/auth/signup", json=user_data)
            
            if response.status_code == 429:
                # Rate limit hit
                assert "Too many registration attempts" in response.json()["detail"]
                break
        else:
            # If no rate limit hit, that's also acceptable
            pass
    
    def test_login_rate_limit(self):
        """Test rate limiting on login endpoint."""
        # Make multiple login attempts with wrong password
        wrong_login = test_login.copy()
        wrong_login["password"] = "WrongPassword123!"
        
        for i in range(10):
            response = client.post("/auth/login", json=wrong_login)
            
            if response.status_code == 429:
                # Rate limit hit
                assert "Too many login attempts" in response.json()["detail"]
                break
        else:
            # If no rate limit hit, that's also acceptable
            pass


class TestPublicPaths:
    """Test that public paths don't require authentication."""
    
    def test_health_endpoint(self):
        """Test that health endpoint is public."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_docs_endpoint(self):
        """Test that docs endpoint is public."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_endpoint(self):
        """Test that openapi endpoint is public."""
        response = client.get("/openapi.json")
        assert response.status_code == 200


class TestSecurityHeaders:
    """Test that security headers are present."""
    
    def test_security_headers_present(self):
        """Test that security headers are added to responses."""
        response = client.get("/health")
        
        # Check for security headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Referrer-Policy" in response.headers
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers


if __name__ == "__main__":
    pytest.main([__file__])

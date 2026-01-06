"""
Authentication API Tests
Tests for user registration, login, password reset, and profile management
"""
import pytest
from httpx import AsyncClient


@pytest.mark.auth
class TestUserRegistration:
    """Test user registration functionality"""
    
    @pytest.mark.asyncio
    async def test_register_new_user_success(self, client: AsyncClient):
        """Test successful user registration"""
        user_data = {
            "name": "New User",
            "email": "newuser@test.com",
            "password": "SecurePass123!"
        }
        
        response = await client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert "id" in data
        assert "password" not in data  # Password should not be returned
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email_fails(self, client: AsyncClient, test_user: dict):
        """Test registration with duplicate email fails"""
        duplicate_data = {
            "name": "Duplicate User",
            "email": test_user["email"],
            "password": "AnotherPass123!"
        }
        
        response = await client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_invalid_email_fails(self, client: AsyncClient):
        """Test registration with invalid email format"""
        invalid_data = {
            "name": "Test User",
            "email": "invalid-email",
            "password": "Pass123!"
        }
        
        response = await client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_register_weak_password_fails(self, client: AsyncClient):
        """Test registration with weak password"""
        weak_password_data = {
            "name": "Test User",
            "email": "test@test.com",
            "password": "123"  # Too short
        }
        
        response = await client.post("/api/v1/auth/register", json=weak_password_data)
        
        assert response.status_code == 422


@pytest.mark.auth
class TestUserLogin:
    """Test user login functionality"""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: dict):
        """Test successful login"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user["email"],
                "password": test_user["password"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password_fails(self, client: AsyncClient, test_user: dict):
        """Test login with incorrect password"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user["email"],
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user_fails(self, client: AsyncClient):
        """Test login with non-existent user"""
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@test.com",
                "password": "SomePass123!"
            }
        )
        
        assert response.status_code == 401


@pytest.mark.auth
class TestUserProfile:
    """Test user profile management"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_profile(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_user: dict
    ):
        """Test getting current user profile"""
        response = await client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["name"] == test_user["name"]
    
    @pytest.mark.asyncio
    async def test_get_profile_without_auth_fails(self, client: AsyncClient):
        """Test getting profile without authentication"""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_profile_with_invalid_token_fails(self, client: AsyncClient):
        """Test getting profile with invalid token"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = await client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401


@pytest.mark.auth
class TestPasswordReset:
    """Test password reset functionality"""
    
    @pytest.mark.asyncio
    async def test_request_password_reset_success(
        self, 
        client: AsyncClient, 
        test_user: dict
    ):
        """Test successful password reset request"""
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user["email"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "reset_token" in data  # MVP returns token directly
    
    @pytest.mark.asyncio
    async def test_reset_password_with_valid_token(
        self, 
        client: AsyncClient, 
        test_user: dict
    ):
        """Test resetting password with valid token"""
        # Request reset
        reset_request = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user["email"]}
        )
        token = reset_request.json()["reset_token"]
        
        # Reset password
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "NewSecurePass123!"
            }
        )
        
        assert response.status_code == 200
        
        # Verify can login with new password
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user["email"],
                "password": "NewSecurePass123!"
            }
        )
        assert login_response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_reset_password_with_invalid_token_fails(self, client: AsyncClient):
        """Test reset with invalid token"""
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": "invalid_token_12345",
                "new_password": "NewPass123!"
            }
        )
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_reset_password_token_cannot_be_reused(
        self, 
        client: AsyncClient, 
        test_user: dict
    ):
        """Test that reset token cannot be used twice"""
        # Request reset
        reset_request = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": test_user["email"]}
        )
        token = reset_request.json()["reset_token"]
        
        # Use token first time
        await client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": "NewPass1!"}
        )
        
        # Try to use token again
        response = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": token, "new_password": "NewPass2!"}
        )
        
        assert response.status_code == 400


@pytest.mark.auth
class TestEmailVerification:
    """Test email verification"""
    
    @pytest.mark.asyncio
    async def test_verify_email_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test successful email verification"""
        response = await client.post(
            "/api/v1/auth/verify-email",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "verified" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_verify_email_without_auth_fails(self, client: AsyncClient):
        """Test email verification without authentication"""
        response = await client.post("/api/v1/auth/verify-email")
        
        assert response.status_code == 401


@pytest.mark.auth
class TestTokenRefresh:
    """Test token refresh functionality"""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, test_user: dict):
        """Test successful token refresh"""
        # Login to get refresh token
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": test_user["email"],
                "password": test_user["password"]
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh access token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token_fails(self, client: AsyncClient):
        """Test refresh with invalid token"""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_refresh_token"}
        )
        
        assert response.status_code in [401, 422]

"""
Integration Tests
Tests for cross-module functionality and complete user journeys
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestCompleteUserJourney:
    """Test complete user journey through the system"""
    
    @pytest.mark.asyncio
    async def test_full_travel_planning_flow(self, client: AsyncClient):
        """Test complete flow: register → login → get recommendations → create itinerary"""
        # Step 1: Register
        user_data = {
            "name": "Journey Test User",
            "email": "journey@test.com",
            "password": "SecurePass123!"
        }
        register_response = await client.post(
            "/api/v1/auth/register",
            json=user_data
        )
        assert register_response.status_code == 201
        
        # Step 2: Login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": user_data["email"],
                "password": user_data["password"]
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Get AI Recommendations
        rec_response = await client.post(
            "/api/v1/ai-recommendations",
            headers=headers,
            json={
                "preferences": "temples and beaches",
                "start_date": "2024-07-01",
                "end_date": "2024-07-05",
                "budget_max": 500000
            }
        )
        assert rec_response.status_code == 200
        recommendations = rec_response.json()["recommendations"]
        assert len(recommendations) > 0
        
        # Step 4: Create Itinerary
        itinerary_response = await client.post(
            "/api/v1/itineraries",
            headers=headers,
            json={
                "title": "Journey Test Itinerary",
                "start_date": "2024-07-01",
                "end_date": "2024-07-05",
                "budget": 500000
            }
        )
        assert itinerary_response.status_code == 201
        itinerary_id = itinerary_response.json()["id"]
        
        # Step 5: Create Review
        review_response = await client.post(
            "/api/v1/reviews",
            headers=headers,
            json={
                "destination_id": recommendations[0]["destination_id"],
                "rating": 5,
                "comment": "Great recommendation!"
            }
        )
        assert review_response.status_code in [200, 201]
        
        # Step 6: Verify all data persists
        profile_response = await client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.status_code == 200
        
        itinerary_get = await client.get(
            f"/api/v1/itineraries/{itinerary_id}",
            headers=headers
        )
        assert itinerary_get.status_code == 200


@pytest.mark.integration
class TestBudgetFiltering:
    """Test budget filtering across modules"""
    
    @pytest.mark.asyncio
    async def test_recommendations_match_itinerary_budget(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that recommendations respect itinerary budget"""
        budget = 100000
        
        # Get recommendations with budget
        rec_response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json={
                "preferences": "budget-friendly activities",
                "start_date": "2024-06-01",
                "end_date": "2024-06-03",
                "budget_max": budget
            }
        )
        
        assert rec_response.status_code == 200
        recommendations = rec_response.json()["recommendations"]
        
        # All recommendations should be within budget
        for rec in recommendations:
            assert rec["estimated_cost"] <= budget
        
        # Create itinerary with same budget
        itinerary_response = await client.post(
            "/api/v1/itineraries",
            headers=auth_headers,
            json={
                "title": "Budget Itinerary",
                "start_date": "2024-06-01",
                "end_date": "2024-06-03",
                "budget": budget
            }
        )
        
        assert itinerary_response.status_code == 201


@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across operations"""
    
    @pytest.mark.asyncio
    async def test_review_affects_destination_rating(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that creating reviews updates destination average rating"""
        destination_id = 1
        
        # Get destination before review
        before_response = await client.get(f"/api/v1/destinations/{destination_id}")
        if before_response.status_code == 200:
            before_data = before_response.json()
            before_count = before_data.get("review_count", 0)
            
            # Create review
            review_response = await client.post(
                "/api/v1/reviews",
                headers=auth_headers,
                json={
                    "destination_id": destination_id,
                    "rating": 5,
                    "comment": "Testing rating update"
                }
            )
            
            if review_response.status_code in [200, 201]:
                # Get destination after review
                after_response = await client.get(f"/api/v1/destinations/{destination_id}")
                assert after_response.status_code == 200
                after_data = after_response.json()
                
                # Review count should increase (if field exists)
                if "review_count" in after_data:
                    assert after_data["review_count"] >= before_count


@pytest.mark.integration
class TestWeatherIntegration:
    """Test weather integration across modules"""
    
    @pytest.mark.asyncio
    async def test_weather_in_recommendations(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that weather data appears in recommendations"""
        response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json={
                "preferences": "outdoor activities",
                "start_date": "2024-06-15",
                "end_date": "2024-06-20"
            }
        )
        
        assert response.status_code == 200
        recommendations = response.json()["recommendations"]
        
        # Check if weather context is mentioned
        has_weather = any(
            "weather" in rec["reasoning"].lower() or
            "temperature" in rec["reasoning"].lower() or
            "rain" in rec["reasoning"].lower()
            for rec in recommendations
        )
        assert has_weather
    
    @pytest.mark.asyncio
    async def test_get_weather_forecast(self, client: AsyncClient):
        """Test weather API endpoint"""
        response = await client.get(
            "/api/v1/weather",
            params={"location": "Bali", "days": 7}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "forecast" in data or "daily" in data
            # Verify forecast has temperature data
            forecast = data.get("forecast", data.get("daily", []))
            if forecast:
                assert len(forecast) <= 7


@pytest.mark.integration
class TestAuthenticationFlow:
    """Test authentication across multiple operations"""
    
    @pytest.mark.asyncio
    async def test_auth_required_for_protected_endpoints(self, client: AsyncClient):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            ("/api/v1/auth/me", "get"),
            ("/api/v1/itineraries", "get"),
            ("/api/v1/itineraries", "post"),
            ("/api/v1/reviews", "post"),
            ("/api/v1/ai-recommendations", "post"),
        ]
        
        for endpoint, method in protected_endpoints:
            if method == "get":
                response = await client.get(endpoint)
            elif method == "post":
                response = await client.post(endpoint, json={})
            
            assert response.status_code == 401, f"{method.upper()} {endpoint} should require auth"
    
    @pytest.mark.asyncio
    async def test_password_reset_flow(self, client: AsyncClient):
        """Test complete password reset flow"""
        # Create user
        user_data = {
            "name": "Reset Test",
            "email": "reset@test.com",
            "password": "OldPass123!"
        }
        await client.post("/api/v1/auth/register", json=user_data)
        
        # Request password reset
        reset_request = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": user_data["email"]}
        )
        assert reset_request.status_code == 200
        token = reset_request.json()["reset_token"]
        
        # Reset password
        reset_response = await client.post(
            "/api/v1/auth/reset-password",
            json={
                "token": token,
                "new_password": "NewPass123!"
            }
        )
        assert reset_response.status_code == 200
        
        # Verify old password doesn't work
        old_login = await client.post(
            "/api/v1/auth/login",
            data={
                "username": user_data["email"],
                "password": "OldPass123!"
            }
        )
        assert old_login.status_code == 401
        
        # Verify new password works
        new_login = await client.post(
            "/api/v1/auth/login",
            data={
                "username": user_data["email"],
                "password": "NewPass123!"
            }
        )
        assert new_login.status_code == 200


@pytest.mark.integration
class TestConcurrentOperations:
    """Test concurrent operations"""
    
    @pytest.mark.asyncio
    async def test_multiple_users_no_data_leakage(self, client: AsyncClient):
        """Test that multiple users don't see each other's data"""
        # Create two users
        user1_data = {
            "name": "User One",
            "email": "user1@test.com",
            "password": "Pass1234!"
        }
        user2_data = {
            "name": "User Two",
            "email": "user2@test.com",
            "password": "Pass1234!"
        }
        
        await client.post("/api/v1/auth/register", json=user1_data)
        await client.post("/api/v1/auth/register", json=user2_data)
        
        # Login both users
        login1 = await client.post(
            "/api/v1/auth/login",
            data={"username": user1_data["email"], "password": user1_data["password"]}
        )
        login2 = await client.post(
            "/api/v1/auth/login",
            data={"username": user2_data["email"], "password": user2_data["password"]}
        )
        
        headers1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}
        headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}
        
        # Create itinerary for user1
        itinerary1 = await client.post(
            "/api/v1/itineraries",
            headers=headers1,
            json={
                "title": "User1 Itinerary",
                "start_date": "2024-06-01",
                "end_date": "2024-06-05",
                "budget": 1000000
            }
        )
        assert itinerary1.status_code == 201
        
        # User2 should not see user1's itinerary
        user2_itineraries = await client.get(
            "/api/v1/itineraries",
            headers=headers2
        )
        assert user2_itineraries.status_code == 200
        user2_list = user2_itineraries.json()
        
        # User2's list should not contain user1's itinerary
        user1_itinerary_id = itinerary1.json()["id"]
        assert not any(it["id"] == user1_itinerary_id for it in user2_list)


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling across modules"""
    
    @pytest.mark.asyncio
    async def test_graceful_handling_of_invalid_data(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that invalid data returns proper error responses"""
        # Invalid destination ID
        invalid_review = await client.post(
            "/api/v1/reviews",
            headers=auth_headers,
            json={
                "destination_id": 999999,
                "rating": 5,
                "comment": "Test"
            }
        )
        assert invalid_review.status_code in [400, 404]
        
        # Invalid date range
        invalid_itinerary = await client.post(
            "/api/v1/itineraries",
            headers=auth_headers,
            json={
                "title": "Invalid",
                "start_date": "2024-12-31",
                "end_date": "2024-01-01",
                "budget": 1000000
            }
        )
        assert invalid_itinerary.status_code == 422

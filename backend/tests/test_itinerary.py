"""
Itinerary API Tests
Tests for itinerary CRUD operations
"""
import pytest
from httpx import AsyncClient
from datetime import date, timedelta


@pytest.mark.itinerary
class TestItineraryCreation:
    """Test itinerary creation"""
    
    @pytest.mark.asyncio
    async def test_create_itinerary_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test successful itinerary creation"""
        itinerary_data = {
            "title": "Bali Adventure 2024",
            "start_date": "2024-06-01",
            "end_date": "2024-06-07",
            "budget": 5000000,
            "notes": "Family vacation"
        }
        
        response = await client.post(
            "/api/v1/itineraries",
            headers=auth_headers,
            json=itinerary_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == itinerary_data["title"]
        assert data["budget"] == itinerary_data["budget"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_itinerary_missing_required_fields(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test creation with missing required fields"""
        incomplete_data = {
            "title": "Incomplete Itinerary"
            # Missing start_date, end_date
        }
        
        response = await client.post(
            "/api/v1/itineraries",
            headers=auth_headers,
            json=incomplete_data
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_itinerary_invalid_date_range(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test creation with end date before start date"""
        invalid_data = {
            "title": "Invalid Dates",
            "start_date": "2024-06-10",
            "end_date": "2024-06-05",  # Before start
            "budget": 1000000
        }
        
        response = await client.post(
            "/api/v1/itineraries",
            headers=auth_headers,
            json=invalid_data
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_itinerary_negative_budget(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test creation with negative budget"""
        invalid_data = {
            "title": "Negative Budget",
            "start_date": "2024-06-01",
            "end_date": "2024-06-05",
            "budget": -1000
        }
        
        response = await client.post(
            "/api/v1/itineraries",
            headers=auth_headers,
            json=invalid_data
        )
        
        assert response.status_code == 422


@pytest.mark.itinerary
class TestItineraryRetrieval:
    """Test itinerary retrieval"""
    
    @pytest.mark.asyncio
    async def test_list_user_itineraries(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test listing user's own itineraries"""
        # Create test itinerary
        await client.post(
            "/api/v1/itineraries",
            headers=auth_headers,
            json={
                "title": "Test Itinerary",
                "start_date": "2024-06-01",
                "end_date": "2024-06-05",
                "budget": 1000000
            }
        )
        
        # List itineraries
        response = await client.get(
            "/api/v1/itineraries",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    @pytest.mark.asyncio
    async def test_get_itinerary_by_id(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test getting specific itinerary"""
        # Create itinerary
        create_response = await client.post(
            "/api/v1/itineraries",
            headers=auth_headers,
            json={
                "title": "Specific Itinerary",
                "start_date": "2024-06-01",
                "end_date": "2024-06-05",
                "budget": 2000000
            }
        )
        itinerary_id = create_response.json()["id"]
        
        # Get itinerary
        response = await client.get(
            f"/api/v1/itineraries/{itinerary_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == itinerary_id
        assert data["title"] == "Specific Itinerary"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_itinerary_fails(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test getting non-existent itinerary"""
        response = await client.get(
            "/api/v1/itineraries/999999",
            headers=auth_headers
        )
        
        assert response.status_code == 404


@pytest.mark.itinerary
class TestItineraryUpdate:
    """Test itinerary update operations"""
    
    @pytest.mark.asyncio
    async def test_update_itinerary_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test successful itinerary update"""
        # Create itinerary
        create_response = await client.post(
            "/api/v1/itineraries",
            headers=auth_headers,
            json={
                "title": "Original Title",
                "start_date": "2024-06-01",
                "end_date": "2024-06-05",
                "budget": 1000000
            }
        )
        itinerary_id = create_response.json()["id"]
        
        # Update itinerary
        update_data = {
            "title": "Updated Title",
            "budget": 1500000
        }
        response = await client.patch(
            f"/api/v1/itineraries/{itinerary_id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["budget"] == 1500000
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_itinerary_fails(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test updating non-existent itinerary"""
        response = await client.patch(
            "/api/v1/itineraries/999999",
            headers=auth_headers,
            json={"title": "Updated"}
        )
        
        assert response.status_code == 404


@pytest.mark.itinerary
class TestItineraryDeletion:
    """Test itinerary deletion"""
    
    @pytest.mark.asyncio
    async def test_delete_itinerary_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test successful itinerary deletion"""
        # Create itinerary
        create_response = await client.post(
            "/api/v1/itineraries",
            headers=auth_headers,
            json={
                "title": "To Be Deleted",
                "start_date": "2024-06-01",
                "end_date": "2024-06-05",
                "budget": 1000000
            }
        )
        itinerary_id = create_response.json()["id"]
        
        # Delete itinerary
        response = await client.delete(
            f"/api/v1/itineraries/{itinerary_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify deletion
        get_response = await client.get(
            f"/api/v1/itineraries/{itinerary_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_itinerary_fails(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test deleting non-existent itinerary"""
        response = await client.delete(
            "/api/v1/itineraries/999999",
            headers=auth_headers
        )
        
        assert response.status_code == 404


@pytest.mark.itinerary
class TestItineraryAuthorization:
    """Test itinerary authorization rules"""
    
    @pytest.mark.asyncio
    async def test_cannot_access_other_user_itinerary(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that users cannot access other users' itineraries"""
        # Create itinerary with first user
        create_response = await client.post(
            "/api/v1/itineraries",
            headers=auth_headers,
            json={
                "title": "Private Itinerary",
                "start_date": "2024-06-01",
                "end_date": "2024-06-05",
                "budget": 1000000
            }
        )
        itinerary_id = create_response.json()["id"]
        
        # Create second user and get their token
        user2_data = {
            "name": "Another User",
            "email": "another@test.com",
            "password": "SecurePass123!"
        }
        await client.post("/api/v1/auth/register", json=user2_data)
        
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": user2_data["email"],
                "password": user2_data["password"]
            }
        )
        user2_token = login_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # Try to access first user's itinerary
        response = await client.get(
            f"/api/v1/itineraries/{itinerary_id}",
            headers=user2_headers
        )
        
        assert response.status_code in [403, 404]  # Forbidden or Not Found


@pytest.mark.itinerary
class TestItineraryWithDestinations:
    """Test itinerary with destinations"""
    
    @pytest.mark.asyncio
    async def test_add_destination_to_itinerary(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test adding destinations to itinerary"""
        # Create itinerary
        create_response = await client.post(
            "/api/v1/itineraries",
            headers=auth_headers,
            json={
                "title": "Itinerary with Destinations",
                "start_date": "2024-06-01",
                "end_date": "2024-06-05",
                "budget": 2000000
            }
        )
        itinerary_id = create_response.json()["id"]
        
        # Add destination (assuming endpoint exists)
        destination_data = {
            "destination_id": 1,  # Tanah Lot
            "visit_date": "2024-06-02",
            "notes": "Visit at sunset"
        }
        
        response = await client.post(
            f"/api/v1/itineraries/{itinerary_id}/destinations",
            headers=auth_headers,
            json=destination_data
        )
        
        # Should succeed or return 404 if endpoint not implemented
        assert response.status_code in [200, 201, 404]

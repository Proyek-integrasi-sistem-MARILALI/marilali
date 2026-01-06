"""
Review API Tests
Tests for review CRUD operations and rating system
"""
import pytest
from httpx import AsyncClient


@pytest.mark.review
class TestReviewCreation:
    """Test review creation"""
    
    @pytest.mark.asyncio
    async def test_create_review_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test successful review creation"""
        review_data = {
            "destination_id": 1,  # Tanah Lot
            "rating": 5,
            "comment": "Amazing sunset view! Highly recommended.",
            "visit_date": "2024-05-15"
        }
        
        response = await client.post(
            "/api/v1/reviews",
            headers=auth_headers,
            json=review_data
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == review_data["comment"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_review_invalid_rating(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test review with invalid rating (out of 1-5 range)"""
        invalid_review = {
            "destination_id": 1,
            "rating": 6,  # Invalid: > 5
            "comment": "Test comment"
        }
        
        response = await client.post(
            "/api/v1/reviews",
            headers=auth_headers,
            json=invalid_review
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_review_zero_rating(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test review with zero rating"""
        invalid_review = {
            "destination_id": 1,
            "rating": 0,  # Invalid: < 1
            "comment": "Test comment"
        }
        
        response = await client.post(
            "/api/v1/reviews",
            headers=auth_headers,
            json=invalid_review
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_review_missing_required_fields(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test review creation with missing fields"""
        incomplete_review = {
            "destination_id": 1
            # Missing rating
        }
        
        response = await client.post(
            "/api/v1/reviews",
            headers=auth_headers,
            json=incomplete_review
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_duplicate_review_fails(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that user cannot review same destination twice"""
        review_data = {
            "destination_id": 2,
            "rating": 4,
            "comment": "First review"
        }
        
        # Create first review
        first_response = await client.post(
            "/api/v1/reviews",
            headers=auth_headers,
            json=review_data
        )
        assert first_response.status_code in [200, 201]
        
        # Try to create duplicate
        second_response = await client.post(
            "/api/v1/reviews",
            headers=auth_headers,
            json={
                "destination_id": 2,
                "rating": 5,
                "comment": "Second review"
            }
        )
        
        assert second_response.status_code in [400, 409]  # Bad Request or Conflict


@pytest.mark.review
class TestReviewRetrieval:
    """Test review retrieval"""
    
    @pytest.mark.asyncio
    async def test_get_reviews_by_destination(
        self, 
        client: AsyncClient
    ):
        """Test getting reviews for a destination"""
        destination_id = 1
        response = await client.get(f"/api/v1/destinations/{destination_id}/reviews")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_reviews_empty_destination(
        self, 
        client: AsyncClient
    ):
        """Test getting reviews for destination with no reviews"""
        # Use unlikely destination ID
        response = await client.get("/api/v1/destinations/999/reviews")
        
        # Should return empty list or 404
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_get_user_reviews(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test getting user's own reviews"""
        response = await client.get(
            "/api/v1/reviews/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.review
class TestReviewUpdate:
    """Test review update operations"""
    
    @pytest.mark.asyncio
    async def test_update_own_review_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test updating user's own review"""
        # Create review
        create_response = await client.post(
            "/api/v1/reviews",
            headers=auth_headers,
            json={
                "destination_id": 3,
                "rating": 3,
                "comment": "Original comment"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip("Could not create review")
        
        review_id = create_response.json()["id"]
        
        # Update review
        update_data = {
            "rating": 5,
            "comment": "Updated comment - much better!"
        }
        response = await client.patch(
            f"/api/v1/reviews/{review_id}",
            headers=auth_headers,
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == update_data["comment"]
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_review_fails(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test updating non-existent review"""
        response = await client.patch(
            "/api/v1/reviews/999999",
            headers=auth_headers,
            json={"rating": 4}
        )
        
        assert response.status_code == 404


@pytest.mark.review
class TestReviewDeletion:
    """Test review deletion"""
    
    @pytest.mark.asyncio
    async def test_delete_own_review_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test deleting user's own review"""
        # Create review
        create_response = await client.post(
            "/api/v1/reviews",
            headers=auth_headers,
            json={
                "destination_id": 4,
                "rating": 4,
                "comment": "To be deleted"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip("Could not create review")
        
        review_id = create_response.json()["id"]
        
        # Delete review
        response = await client.delete(
            f"/api/v1/reviews/{review_id}",
            headers=auth_headers
        )
        
        assert response.status_code in [200, 204]
        
        # Verify deletion
        get_response = await client.get(f"/api/v1/reviews/{review_id}")
        assert get_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_review_fails(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test deleting non-existent review"""
        response = await client.delete(
            "/api/v1/reviews/999999",
            headers=auth_headers
        )
        
        assert response.status_code == 404


@pytest.mark.review
class TestReviewAuthorization:
    """Test review authorization"""
    
    @pytest.mark.asyncio
    async def test_cannot_update_other_user_review(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that users cannot update other users' reviews"""
        # Create review with first user
        create_response = await client.post(
            "/api/v1/reviews",
            headers=auth_headers,
            json={
                "destination_id": 5,
                "rating": 4,
                "comment": "First user review"
            }
        )
        
        if create_response.status_code not in [200, 201]:
            pytest.skip("Could not create review")
        
        review_id = create_response.json()["id"]
        
        # Create second user
        user2_data = {
            "name": "Second User",
            "email": "second@test.com",
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
        
        # Try to update first user's review
        response = await client.patch(
            f"/api/v1/reviews/{review_id}",
            headers=user2_headers,
            json={"rating": 1}
        )
        
        assert response.status_code in [403, 404]


@pytest.mark.review
class TestRatingValidation:
    """Test rating validation"""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("rating", [1, 2, 3, 4, 5])
    async def test_valid_ratings(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        rating: int
    ):
        """Test that ratings 1-5 are all valid"""
        review_data = {
            "destination_id": rating,  # Use different destinations
            "rating": rating,
            "comment": f"Rating {rating} test"
        }
        
        response = await client.post(
            "/api/v1/reviews",
            headers=auth_headers,
            json=review_data
        )
        
        assert response.status_code in [200, 201]
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("invalid_rating", [-1, 0, 6, 10, 100])
    async def test_invalid_ratings(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        invalid_rating: int
    ):
        """Test that invalid ratings are rejected"""
        review_data = {
            "destination_id": 1,
            "rating": invalid_rating,
            "comment": "Invalid rating test"
        }
        
        response = await client.post(
            "/api/v1/reviews",
            headers=auth_headers,
            json=review_data
        )
        
        assert response.status_code == 422


@pytest.mark.review
class TestReviewAggregation:
    """Test review aggregation and average ratings"""
    
    @pytest.mark.asyncio
    async def test_destination_average_rating(
        self, 
        client: AsyncClient
    ):
        """Test that destination shows average rating"""
        destination_id = 1
        response = await client.get(f"/api/v1/destinations/{destination_id}")
        
        if response.status_code == 200:
            data = response.json()
            # Check if average_rating field exists
            if "average_rating" in data:
                assert 1.0 <= data["average_rating"] <= 5.0
            if "review_count" in data:
                assert isinstance(data["review_count"], int)
                assert data["review_count"] >= 0

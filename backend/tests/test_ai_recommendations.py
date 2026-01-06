"""
AI Recommendations API Tests
Tests for AI-powered travel recommendations with budget filtering
"""
import pytest
from httpx import AsyncClient


@pytest.mark.ai
class TestAIRecommendations:
    """Test AI recommendation system"""
    
    @pytest.mark.asyncio
    async def test_get_recommendations_without_budget(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test getting recommendations without budget limit"""
        request_data = {
            "preferences": "I want to visit temples in Bali",
            "start_date": "2024-06-01",
            "end_date": "2024-06-07"
        }
        
        response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0
        
        # Verify each recommendation has required fields
        for rec in data["recommendations"]:
            assert "destination_id" in rec
            assert "name" in rec
            assert "confidence_score" in rec
            assert "reasoning" in rec
            assert 0.0 <= rec["confidence_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_budget_filter_very_low(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test recommendations with very low budget (50K IDR)"""
        request_data = {
            "preferences": "beaches or temples",
            "start_date": "2024-06-01",
            "end_date": "2024-06-03",
            "budget_max": 50000
        }
        
        response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        recommendations = data["recommendations"]
        
        # Should have at least some recommendations
        assert len(recommendations) >= 2
        
        # All recommendations should be within budget
        for rec in recommendations:
            assert rec["estimated_cost"] <= 50000
    
    @pytest.mark.asyncio
    async def test_budget_filter_medium(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test recommendations with medium budget (500K IDR)"""
        request_data = {
            "preferences": "nature and adventure activities",
            "start_date": "2024-07-01",
            "end_date": "2024-07-05",
            "budget_max": 500000
        }
        
        response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        recommendations = data["recommendations"]
        
        # Should have more options with higher budget
        assert len(recommendations) >= 3
        
        # All should be within budget
        for rec in recommendations:
            assert rec["estimated_cost"] <= 500000
    
    @pytest.mark.asyncio
    async def test_confidence_scores_in_valid_range(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that confidence scores are in valid range"""
        request_data = {
            "preferences": "cultural experiences and temples",
            "start_date": "2024-08-01",
            "end_date": "2024-08-05"
        }
        
        response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json=request_data
        )
        
        assert response.status_code == 200
        recommendations = response.json()["recommendations"]
        
        for rec in recommendations:
            # Confidence scores should be between 0.70 and 0.95
            assert 0.70 <= rec["confidence_score"] <= 0.95
    
    @pytest.mark.asyncio
    async def test_weather_integration_in_reasoning(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that weather data is included in recommendation reasoning"""
        request_data = {
            "preferences": "beaches",
            "start_date": "2024-06-15",
            "end_date": "2024-06-20"
        }
        
        response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json=request_data
        )
        
        assert response.status_code == 200
        recommendations = response.json()["recommendations"]
        
        # At least one recommendation should mention weather
        weather_mentions = any(
            "weather" in rec["reasoning"].lower() or 
            "temperature" in rec["reasoning"].lower() or
            "rain" in rec["reasoning"].lower()
            for rec in recommendations
        )
        assert weather_mentions
    
    @pytest.mark.asyncio
    async def test_unrealistic_budget_returns_empty_or_few(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that unrealistic low budget returns few/no results"""
        request_data = {
            "preferences": "luxury resorts",
            "start_date": "2024-06-01",
            "end_date": "2024-06-03",
            "budget_max": 1000  # Unrealistically low
        }
        
        response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json=request_data
        )
        
        assert response.status_code == 200
        recommendations = response.json()["recommendations"]
        
        # Should return very few or no results
        assert len(recommendations) <= 2
    
    @pytest.mark.asyncio
    async def test_invalid_date_range_fails(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that invalid date range returns error"""
        request_data = {
            "preferences": "beaches",
            "start_date": "2024-06-10",
            "end_date": "2024-06-05"  # End before start
        }
        
        response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json=request_data
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_missing_required_fields_fails(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that missing required fields returns validation error"""
        request_data = {
            "preferences": "temples"
            # Missing start_date and end_date
        }
        
        response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json=request_data
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_recommendations_without_auth_fails(self, client: AsyncClient):
        """Test that recommendations require authentication"""
        request_data = {
            "preferences": "beaches",
            "start_date": "2024-06-01",
            "end_date": "2024-06-05"
        }
        
        response = await client.post(
            "/api/v1/ai-recommendations",
            json=request_data
        )
        
        assert response.status_code == 401


@pytest.mark.ai
class TestPreferenceCategorization:
    """Test different preference categories"""
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("preferences,expected_category", [
        ("temples and spiritual places", "temple"),
        ("beautiful beaches and ocean views", "beach"),
        ("waterfalls and nature", "waterfall"),
        ("mountains and hiking", "mountain"),
        ("cultural experiences", "culture"),
    ])
    async def test_preference_matching(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        preferences: str,
        expected_category: str
    ):
        """Test that recommendations match user preferences"""
        request_data = {
            "preferences": preferences,
            "start_date": "2024-06-01",
            "end_date": "2024-06-05"
        }
        
        response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json=request_data
        )
        
        assert response.status_code == 200
        recommendations = response.json()["recommendations"]
        assert len(recommendations) > 0
        
        # At least one recommendation should mention the category
        category_match = any(
            expected_category in rec["reasoning"].lower() or
            expected_category in rec["name"].lower()
            for rec in recommendations
        )
        assert category_match


@pytest.mark.ai
class TestRecommendationDetails:
    """Test recommendation response structure and details"""
    
    @pytest.mark.asyncio
    async def test_recommendation_has_complete_destination_info(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that recommendations include complete destination information"""
        request_data = {
            "preferences": "famous tourist spots",
            "start_date": "2024-06-01",
            "end_date": "2024-06-03"
        }
        
        response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json=request_data
        )
        
        assert response.status_code == 200
        recommendations = response.json()["recommendations"]
        
        for rec in recommendations:
            # Check all required fields
            assert "destination_id" in rec
            assert "name" in rec
            assert "location" in rec
            assert "description" in rec
            assert "estimated_cost" in rec
            assert "confidence_score" in rec
            assert "reasoning" in rec
            
            # Check data types
            assert isinstance(rec["destination_id"], int)
            assert isinstance(rec["name"], str)
            assert isinstance(rec["estimated_cost"], (int, float))
            assert isinstance(rec["confidence_score"], float)
    
    @pytest.mark.asyncio
    async def test_recommendations_are_sorted_by_confidence(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """Test that recommendations are sorted by confidence score"""
        request_data = {
            "preferences": "popular destinations",
            "start_date": "2024-06-01",
            "end_date": "2024-06-05"
        }
        
        response = await client.post(
            "/api/v1/ai-recommendations",
            headers=auth_headers,
            json=request_data
        )
        
        assert response.status_code == 200
        recommendations = response.json()["recommendations"]
        
        if len(recommendations) >= 2:
            # Check that scores are in descending order
            scores = [rec["confidence_score"] for rec in recommendations]
            assert scores == sorted(scores, reverse=True)

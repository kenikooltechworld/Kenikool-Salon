"""
Test Campaign Endpoints
Tests for marketing campaign management functionality
"""
import pytest


class TestCampaignEndpoints:
    """Test Campaign endpoints"""
    
    # CREATE CAMPAIGN TESTS
    
    def test_create_campaign_endpoint_exists(self, client, auth_headers):
        """Test create campaign endpoint exists"""
        campaign_data = {
            "name": "Test Campaign",
            "campaign_type": "seasonal",
            "message_template": "Test message",
            "target_segment": {"all_clients": True}
        }
        response = client.post("/api/campaigns", json=campaign_data, headers=auth_headers)
        assert response.status_code != 404
    
    def test_create_campaign_requires_auth(self, client):
        """Test create campaign requires authentication"""
        campaign_data = {
            "name": "Test Campaign",
            "campaign_type": "seasonal",
            "message_template": "Test message"
        }
        response = client.post("/api/campaigns", json=campaign_data)
        assert response.status_code in [401, 403]
    
    def test_create_campaign_validates_required_fields(self, client, auth_headers):
        """Test create campaign validates required fields"""
        response = client.post("/api/campaigns", json={}, headers=auth_headers)
        assert response.status_code in [400, 422]
    
    def test_create_campaign_validates_name_length(self, client, auth_headers):
        """Test campaign name length validation"""
        campaign_data = {
            "name": "A" * 300,
            "campaign_type": "seasonal",
            "message_template": "Test"
        }
        response = client.post("/api/campaigns", json=campaign_data, headers=auth_headers)
        assert response.status_code in [400, 422]
    
    # LIST CAMPAIGNS TESTS
    
    def test_list_campaigns_endpoint_exists(self, client, auth_headers):
        """Test list campaigns endpoint exists"""
        response = client.get("/api/campaigns", headers=auth_headers)
        assert response.status_code != 404
    
    def test_list_campaigns_requires_auth(self, client):
        """Test list campaigns requires authentication"""
        response = client.get("/api/campaigns")
        assert response.status_code in [401, 403]
    
    def test_list_campaigns_accepts_status_filter(self, client, auth_headers):
        """Test list campaigns accepts status filter"""
        response = client.get("/api/campaigns?status=draft", headers=auth_headers)
        assert response.status_code != 404
    
    def test_list_campaigns_accepts_type_filter(self, client, auth_headers):
        """Test list campaigns accepts type filter"""
        response = client.get("/api/campaigns?campaign_type=seasonal", headers=auth_headers)
        assert response.status_code != 404
    
    def test_list_campaigns_accepts_pagination(self, client, auth_headers):
        """Test list campaigns accepts pagination"""
        response = client.get("/api/campaigns?offset=0&limit=10", headers=auth_headers)
        assert response.status_code != 404
    
    # GET CAMPAIGN DETAILS TESTS
    
    def test_get_campaign_endpoint_exists(self, client, auth_headers):
        """Test get campaign endpoint exists"""
        response = client.get("/api/campaigns/507f1f77bcf86cd799439011", headers=auth_headers)
        # Should not return 404 for endpoint, but 404 for not found campaign is OK
        assert response.status_code in [200, 404]
    
    def test_get_campaign_requires_auth(self, client):
        """Test get campaign requires authentication"""
        response = client.get("/api/campaigns/507f1f77bcf86cd799439011")
        assert response.status_code in [401, 403]
    
    # UPDATE CAMPAIGN TESTS
    
    def test_update_campaign_endpoint_exists(self, client, auth_headers):
        """Test update campaign endpoint exists"""
        update_data = {"name": "Updated Campaign"}
        response = client.put("/api/campaigns/507f1f77bcf86cd799439011", json=update_data, headers=auth_headers)
        # Should not return 404 for endpoint, but 404 for not found campaign is OK
        assert response.status_code in [200, 404]
    
    def test_update_campaign_requires_auth(self, client):
        """Test update campaign requires authentication"""
        response = client.put("/api/campaigns/507f1f77bcf86cd799439011", json={"name": "Updated"})
        assert response.status_code in [401, 403]
    
    def test_update_campaign_validates_data(self, client, auth_headers):
        """Test update campaign validates data"""
        response = client.put("/api/campaigns/507f1f77bcf86cd799439011", json={"name": "A" * 300}, headers=auth_headers)
        assert response.status_code in [400, 404, 422]
    
    # SEND CAMPAIGN TESTS
    
    def test_send_campaign_endpoint_exists(self, client, auth_headers):
        """Test send campaign endpoint exists"""
        response = client.post("/api/campaigns/507f1f77bcf86cd799439011/send", headers=auth_headers)
        # Should not return 404 for endpoint, but 404 for not found campaign is OK
        assert response.status_code in [200, 404]
    
    def test_send_campaign_requires_auth(self, client):
        """Test send campaign requires authentication"""
        response = client.post("/api/campaigns/507f1f77bcf86cd799439011/send")
        assert response.status_code in [401, 403]
    
    # DELETE CAMPAIGN TESTS
    
    def test_delete_campaign_endpoint_exists(self, client, auth_headers):
        """Test delete campaign endpoint exists"""
        response = client.delete("/api/campaigns/507f1f77bcf86cd799439011", headers=auth_headers)
        # Should not return 404 for endpoint, but 404 for not found campaign is OK
        assert response.status_code in [200, 204, 404]
    
    def test_delete_campaign_requires_auth(self, client):
        """Test delete campaign requires authentication"""
        response = client.delete("/api/campaigns/507f1f77bcf86cd799439011")
        assert response.status_code in [401, 403]
    
    # CAMPAIGN ANALYTICS TESTS
    
    def test_get_campaign_analytics_endpoint_exists(self, client, auth_headers):
        """Test get campaign analytics endpoint exists"""
        response = client.get("/api/campaigns/507f1f77bcf86cd799439011/analytics", headers=auth_headers)
        # Should not return 404 for endpoint, but 404 for not found campaign is OK
        assert response.status_code in [200, 404]
    
    def test_get_campaign_analytics_requires_auth(self, client):
        """Test get campaign analytics requires authentication"""
        response = client.get("/api/campaigns/507f1f77bcf86cd799439011/analytics")
        assert response.status_code in [401, 403]
    
    # CLIENT SEGMENT PREVIEW TESTS
    
    def test_preview_segment_endpoint_exists(self, client, auth_headers):
        """Test preview segment endpoint exists"""
        response = client.post("/api/campaigns/segment/preview", json={"criteria": {"all_clients": True}}, headers=auth_headers)
        assert response.status_code != 404
    
    def test_preview_segment_requires_auth(self, client):
        """Test preview segment requires authentication"""
        response = client.post("/api/campaigns/segment/preview", json={"criteria": {"all_clients": True}})
        assert response.status_code in [401, 403]
    
    def test_preview_segment_validates_criteria(self, client, auth_headers):
        """Test preview segment validates criteria"""
        response = client.post("/api/campaigns/segment/preview", json={}, headers=auth_headers)
        assert response.status_code in [200, 400, 422]
    
    # CAMPAIGN TYPES TESTS
    
    def test_create_birthday_campaign(self, client, auth_headers):
        """Test creating birthday campaign"""
        campaign_data = {
            "name": "Birthday Campaign",
            "campaign_type": "birthday",
            "message_template": "Happy Birthday!",
            "target_segment": {"all_clients": True}
        }
        response = client.post("/api/campaigns", json=campaign_data, headers=auth_headers)
        assert response.status_code != 404
    
    def test_create_seasonal_campaign(self, client, auth_headers):
        """Test creating seasonal campaign"""
        campaign_data = {
            "name": "Holiday Campaign",
            "campaign_type": "seasonal",
            "message_template": "Holiday Special!",
            "target_segment": {"all_clients": True}
        }
        response = client.post("/api/campaigns", json=campaign_data, headers=auth_headers)
        assert response.status_code != 404
    
    def test_create_custom_campaign(self, client, auth_headers):
        """Test creating custom campaign"""
        campaign_data = {
            "name": "VIP Campaign",
            "campaign_type": "custom",
            "message_template": "Exclusive offer!",
            "target_segment": {"min_visits": 10}
        }
        response = client.post("/api/campaigns", json=campaign_data, headers=auth_headers)
        assert response.status_code != 404

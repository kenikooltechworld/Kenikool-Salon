"""
Unit tests for Public Gift Card API Endpoints
Tests balance check, purchase, transfer, and rate limiting
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId
from fastapi.testclient import TestClient

from app.main import app
from app.api.exceptions import BadRequestException, NotFoundException


client = TestClient(app)


class TestPublicBalanceCheckEndpoint:
    """Test public balance check endpoint"""

    @patch('app.api.public_gift_cards.Database.get_db')
    def test_balance_check_valid_card(self, mock_get_db):
        """Test balance check with valid card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        card_data = {
            "_id": ObjectId(),
            "card_number": "GC-TEST123456",
            "balance": 25000,
            "amount": 50000,
            "status": "active",
            "expires_at": datetime.now(timezone.utc) + timedelta(days=365),
            "transactions": [
                {"type": "redeem", "amount": 25000, "timestamp": datetime.now(timezone.utc) - timedelta(days=1)}
            ]
        }
        
        mock_db.gift_cards.find_one.return_value = card_data
        
        response = client.get(
            "/api/public/gift-cards/balance",
            params={"card_number": "GC-TEST123456"}
        )
        
        assert response.status_code == 200
        data = respons
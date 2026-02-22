"""
Extended unit tests for Gift Card Service - Phase 8 Comprehensive Testing
Tests all service methods with 80%+ code coverage
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from bson import ObjectId
import bcrypt

from app.services.gift_card_service import GiftCardService
from app.api.exceptions import BadRequestException, NotFoundException


class TestGiftCardServiceTransfer:
    """Test gift card transfer functionality"""

    @patch('app.services.gift_card_service.Database.get_db')
    def test_transfer_balance_to_existing_card(self, mock_get_db):
        """Test transferring balance to existing card"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        source_card = {
            "_id": ObjectId(),
            "card_number": "GC-SOURCE123",
            "balance": 50000,
            "status": "active"
        }
        
        dest_card = {
            "_id": ObjectId(),
            "card_number": "GC-DEST456",
            "balance": 10000,
            "status": "active"
        }
        
        mock_db.gift_cards.find_one.side_effect = [source_card, dest_card]
        mock_db.gift_cards.update_one.return_value = Mock(modified_count=1)
        
        result = GiftCardService.transfer_balance(
            source_card="GC-SOURCE123",
            destination_card="GC-DEST456",
            amount=20000
        )
        
        assert result["success"] is True
        asser
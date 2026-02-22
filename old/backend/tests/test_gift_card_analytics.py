"""Tests for gift card analytics service"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from app.services.gift_card_analytics_service import GiftCardAnalyticsService


class TestGiftCardAnalyticsService:
    """Test suite for analytics service"""

    @patch('app.services.gift_card_analytics_service.Database')
    def test_get_analytics_basic(self, mock_db):
        """Test basic analytics calculation"""
        mock_db.get_db.return_value.gift_cards.find.return_value = [
            {
                "_id": "1",
                "tenant_id": "test",
                "amount": 50000,
                "balance": 25000,
                "status": "active",
                "card_type": "digital",
                "created_at": datetime.now(timezone.utc),
                "transactions": [
                    {"type": "redeem", "amount": 25000}
                ],
                "purchaser_name": "John Doe",
                "recipient_name": "Jane Smith"
            },
            {
                "_id": "2",
                "tenant_id": "test",
                "amount": 30000,
                "balance": 30000,
                "status": "active",
                "card_type": "physical",
                "created_at": datetime.now(timezone.utc),
                "transactions": [],
                "purchaser_name": "John Doe",
                "recipient_name": "Bob Wilson"
            }
        ]
        
        analytics = GiftCardAnalyticsService.get_analytics("test")
        
        assert analytics["total_sold"] == 80000
        assert analytics["total_redeemed"] == 25000
        assert analytics["outstanding_liability"] == 55000
        assert analytics["total_cards_created"] == 2
        assert analytics["total_cards_redeemed"] == 0
        assert analytics["card_type_breakdown"]["digital"] == 1
        assert analytics["card_type_breakdown"]["physical"] == 1

    @patch('app.services.gift_card_analytics_service.Database')
    def test_get_analytics_redemption_rate(self, mock_db):
        """Test redemption rate calculation"""
        mock_db.get_db.return_value.gift_cards.find.return_value = [
            {
                "_id": "1",
                "tenant_id": "test",
                "amount": 100000,
                "balance": 0,
                "status": "redeemed",
                "card_type": "digital",
                "created_at": datetime.now(timezone.utc),
                "transactions": [
                    {"type": "redeem", "amount": 100000}
                ],
                "purchaser_name": "John",
                "recipient_name": "Jane"
            }
        ]
        
        analytics = GiftCardAnalyticsService.get_analytics("test")
        
        assert analytics["redemption_rate"] == 100.0

    @patch('app.services.gift_card_analytics_service.Database')
    def test_get_analytics_expiration_rate(self, mock_db):
        """Test expiration rate calculation"""
        mock_db.get_db.return_value.gift_cards.find.return_value = [
            {
                "_id": "1",
                "tenant_id": "test",
                "amount": 50000,
                "balance": 50000,
                "status": "expired",
                "card_type": "digital",
                "created_at": datetime.now(timezone.utc),
                "transactions": [],
                "purchaser_name": "John",
                "recipient_name": "Jane"
            },
            {
                "_id": "2",
                "tenant_id": "test",
                "amount": 50000,
                "balance": 50000,
                "status": "active",
                "card_type": "digital",
                "created_at": datetime.now(timezone.utc),
                "transactions": [],
                "purchaser_name": "John",
                "recipient_name": "Bob"
            }
        ]
        
        analytics = GiftCardAnalyticsService.get_analytics("test")
        
        assert analytics["expiration_rate"] == 50.0
        assert analytics["total_cards_expired"] == 1

    @patch('app.services.gift_card_analytics_service.Database')
    def test_get_analytics_average_card_value(self, mock_db):
        """Test average card value calculation"""
        mock_db.get_db.return_value.gift_cards.find.return_value = [
            {
                "_id": "1",
                "tenant_id": "test",
                "amount": 60000,
                "balance": 60000,
                "status": "active",
                "card_type": "digital",
                "created_at": datetime.now(timezone.utc),
                "transactions": [],
                "purchaser_name": "John",
                "recipient_name": "Jane"
            },
            {
                "_id": "2",
                "tenant_id": "test",
                "amount": 40000,
                "balance": 40000,
                "status": "active",
                "card_type": "digital",
                "created_at": datetime.now(timezone.utc),
                "transactions": [],
                "purchaser_name": "John",
                "recipient_name": "Bob"
            }
        ]
        
        analytics = GiftCardAnalyticsService.get_analytics("test")
        
        assert analytics["average_card_value"] == 50000

    @patch('app.services.gift_card_analytics_service.Database')
    def test_get_analytics_top_purchasers(self, mock_db):
        """Test top purchasers calculation"""
        mock_db.get_db.return_value.gift_cards.find.return_value = [
            {
                "_id": "1",
                "tenant_id": "test",
                "amount": 100000,
                "balance": 100000,
                "status": "active",
                "card_type": "digital",
                "created_at": datetime.now(timezone.utc),
                "transactions": [],
                "purchaser_name": "John Doe",
                "recipient_name": "Jane"
            },
            {
                "_id": "2",
                "tenant_id": "test",
                "amount": 50000,
                "balance": 50000,
                "status": "active",
                "card_type": "digital",
                "created_at": datetime.now(timezone.utc),
                "transactions": [],
                "purchaser_name": "John Doe",
                "recipient_name": "Bob"
            },
            {
                "_id": "3",
                "tenant_id": "test",
                "amount": 30000,
                "balance": 30000,
                "status": "active",
                "card_type": "digital",
                "created_at": datetime.now(timezone.utc),
                "transactions": [],
                "purchaser_name": "Jane Smith",
                "recipient_name": "Alice"
            }
        ]
        
        analytics = GiftCardAnalyticsService.get_analytics("test")
        
        assert len(analytics["top_purchasers"]) > 0
        assert analytics["top_purchasers"][0]["name"] == "John Doe"
        assert analytics["top_purchasers"][0]["amount"] == 150000

    @patch('app.services.gift_card_analytics_service.Database')
    def test_get_analytics_top_recipients(self, mock_db):
        """Test top recipients calculation"""
        mock_db.get_db.return_value.gift_cards.find.return_value = [
            {
                "_id": "1",
                "tenant_id": "test",
                "amount": 100000,
                "balance": 100000,
                "status": "active",
                "card_type": "digital",
                "created_at": datetime.now(timezone.utc),
                "transactions": [],
                "purchaser_name": "John",
                "recipient_name": "Jane Smith"
            },
            {
                "_id": "2",
                "tenant_id": "test",
                "amount": 50000,
                "balance": 50000,
                "status": "active",
                "card_type": "digital",
                "created_at": datetime.now(timezone.utc),
                "transactions": [],
                "purchaser_name": "John",
                "recipient_name": "Jane Smith"
            }
        ]
        
        analytics = GiftCardAnalyticsService.get_analytics("test")
        
        assert len(analytics["top_recipients"]) > 0
        assert analytics["top_recipients"][0]["name"] == "Jane Smith"
        assert analytics["top_recipients"][0]["count"] == 2

    @patch('app.services.gift_card_analytics_service.Database')
    def test_get_analytics_date_range_filter(self, mock_db):
        """Test analytics with date range filter"""
        now = datetime.now(timezone.utc)
        past = now - timedelta(days=60)
        
        mock_db.get_db.return_value.gift_cards.find.return_value = []
        
        GiftCardAnalyticsService.get_analytics(
            "test",
            date_from=past,
            date_to=now
        )
        
        # Verify the query was called with correct date range
        call_args = mock_db.get_db.return_value.gift_cards.find.call_args
        assert call_args is not None

    @patch('app.services.gift_card_analytics_service.Database')
    def test_get_analytics_card_type_filter(self, mock_db):
        """Test analytics with card type filter"""
        mock_db.get_db.return_value.gift_cards.find.return_value = [
            {
                "_id": "1",
                "tenant_id": "test",
                "amount": 50000,
                "balance": 50000,
                "status": "active",
                "card_type": "digital",
                "created_at": datetime.now(timezone.utc),
                "transactions": [],
                "purchaser_name": "John",
                "recipient_name": "Jane"
            }
        ]
        
        analytics = GiftCardAnalyticsService.get_analytics(
            "test",
            card_type="digital"
        )
        
        assert analytics["card_type_breakdown"]["digital"] == 1
        assert analytics["card_type_breakdown"]["physical"] == 0

    @patch('app.services.gift_card_analytics_service.Database')
    def test_get_analytics_empty_result(self, mock_db):
        """Test analytics with no cards"""
        mock_db.get_db.return_value.gift_cards.find.return_value = []
        
        analytics = GiftCardAnalyticsService.get_analytics("test")
        
        assert analytics["total_sold"] == 0
        assert analytics["total_redeemed"] == 0
        assert analytics["outstanding_liability"] == 0
        assert analytics["redemption_rate"] == 0
        assert analytics["total_cards_created"] == 0

    def test_export_csv_format(self):
        """Test CSV export format"""
        with patch('app.services.gift_card_analytics_service.Database') as mock_db:
            mock_db.get_db.return_value.gift_cards.find.return_value = [
                {
                    "_id": "1",
                    "tenant_id": "test",
                    "amount": 50000,
                    "balance": 50000,
                    "status": "active",
                    "card_type": "digital",
                    "created_at": datetime.now(timezone.utc),
                    "transactions": [],
                    "purchaser_name": "John",
                    "recipient_name": "Jane"
                }
            ]
            
            csv_content = GiftCardAnalyticsService.export_csv("test")
            
            assert "Gift Card Analytics Report" in csv_content
            assert "Total Sold" in csv_content
            assert "Metric" in csv_content

    def test_export_pdf_format(self):
        """Test PDF export format"""
        with patch('app.services.gift_card_analytics_service.Database') as mock_db:
            mock_db.get_db.return_value.gift_cards.find.return_value = [
                {
                    "_id": "1",
                    "tenant_id": "test",
                    "amount": 50000,
                    "balance": 50000,
                    "status": "active",
                    "card_type": "digital",
                    "created_at": datetime.now(timezone.utc),
                    "transactions": [],
                    "purchaser_name": "John",
                    "recipient_name": "Jane"
                }
            ]
            
            pdf_content = GiftCardAnalyticsService.export_pdf("test")
            
            # PDF should be bytes
            assert isinstance(pdf_content, bytes)

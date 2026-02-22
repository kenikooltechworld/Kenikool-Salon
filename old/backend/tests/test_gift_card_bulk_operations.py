"""Tests for gift card bulk operations service"""
import pytest
from app.services.gift_card_bulk_operations_service import GiftCardBulkOperationsService


class TestGiftCardBulkOperationsService:
    """Test suite for bulk operations"""

    def test_parse_csv_valid(self):
        """Test parsing valid CSV"""
        csv_content = """recipient_name,recipient_email,message
John Doe,john@example.com,Happy Birthday!
Jane Smith,jane@example.com,Enjoy your gift!"""
        
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 2
        assert len(errors) == 0
        assert cards_data[0]["recipient_name"] == "John Doe"
        assert cards_data[0]["recipient_email"] == "john@example.com"
        assert cards_data[0]["message"] == "Happy Birthday!"

    def test_parse_csv_missing_required_fields(self):
        """Test parsing CSV with missing required fields"""
        csv_content = """recipient_name,message
John Doe,Happy Birthday!"""
        
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 0
        assert len(errors) > 0
        assert "Missing required fields" in errors[0]

    def test_parse_csv_invalid_email(self):
        """Test parsing CSV with invalid email"""
        csv_content = """recipient_name,recipient_email,message
John Doe,invalid-email,Happy Birthday!"""
        
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 0
        assert len(errors) > 0
        assert "Invalid email" in errors[0]

    def test_parse_csv_missing_recipient_name(self):
        """Test parsing CSV with missing recipient name"""
        csv_content = """recipient_name,recipient_email,message
,john@example.com,Happy Birthday!"""
        
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 0
        assert len(errors) > 0
        assert "Recipient name is required" in errors[0]

    def test_parse_csv_empty_file(self):
        """Test parsing empty CSV"""
        csv_content = ""
        
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 0
        assert len(errors) > 0
        assert "CSV file is empty" in errors[0]

    def test_parse_csv_with_optional_message(self):
        """Test parsing CSV with optional message field"""
        csv_content = """recipient_name,recipient_email,message
John Doe,john@example.com,
Jane Smith,jane@example.com,Happy Birthday!"""
        
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 2
        assert len(errors) == 0
        assert cards_data[0]["message"] is None
        assert cards_data[1]["message"] == "Happy Birthday!"

    def test_parse_csv_whitespace_handling(self):
        """Test parsing CSV with whitespace"""
        csv_content = """recipient_name,recipient_email,message
  John Doe  ,  john@example.com  ,  Happy Birthday!  """
        
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 1
        assert len(errors) == 0
        assert cards_data[0]["recipient_name"] == "John Doe"
        assert cards_data[0]["recipient_email"] == "john@example.com"

    def test_parse_csv_special_characters(self):
        """Test parsing CSV with special characters"""
        csv_content = """recipient_name,recipient_email,message
João Silva,joao@example.com,Feliz Aniversário!
François Dupont,francois@example.com,Joyeux Anniversaire!"""
        
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 2
        assert len(errors) == 0
        assert cards_data[0]["recipient_name"] == "João Silva"

    def test_parse_csv_max_rows(self):
        """Test parsing CSV with many rows"""
        rows = ["recipient_name,recipient_email,message"]
        for i in range(100):
            rows.append(f"User {i},user{i}@example.com,Message {i}")
        
        csv_content = "\n".join(rows)
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 100
        assert len(errors) == 0

    def test_parse_csv_duplicate_emails(self):
        """Test parsing CSV with duplicate emails (should be allowed)"""
        csv_content = """recipient_name,recipient_email,message
John Doe,john@example.com,Message 1
Jane Doe,john@example.com,Message 2"""
        
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 2
        assert len(errors) == 0

    def test_parse_csv_long_message(self):
        """Test parsing CSV with long message"""
        long_message = "A" * 200
        csv_content = f"""recipient_name,recipient_email,message
John Doe,john@example.com,{long_message}"""
        
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 1
        assert len(errors) == 0
        assert cards_data[0]["message"] == long_message

    def test_parse_csv_quoted_fields(self):
        """Test parsing CSV with quoted fields"""
        csv_content = '''recipient_name,recipient_email,message
"John Doe","john@example.com","Happy Birthday!"
"Jane Smith","jane@example.com","Enjoy your gift!"'''
        
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 2
        assert len(errors) == 0
        assert cards_data[0]["recipient_name"] == "John Doe"

    def test_parse_csv_commas_in_quoted_fields(self):
        """Test parsing CSV with commas in quoted fields"""
        csv_content = '''recipient_name,recipient_email,message
"Doe, John","john@example.com","Happy Birthday!"'''
        
        cards_data, errors = GiftCardBulkOperationsService.parse_csv(csv_content)
        
        assert len(cards_data) == 1
        assert len(errors) == 0
        assert cards_data[0]["recipient_name"] == "Doe, John"

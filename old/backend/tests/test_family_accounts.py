"""
Property-based tests for family account features
Feature: enhanced-customer-booking, Properties 18-20
Validates: Requirements 20
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from hypothesis import given, strategies as st, settings
from bson import ObjectId
from app.services.family_account_service import FamilyAccountService
from app.schemas.family_account import FamilyAccountCreate, FamilyMember, FamilyBookingCreate


# Strategies for generating test data
name_strategy = st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_characters='\x00'))
email_strategy = st.emails()
phone_strategy = st.from_regex(r'\+?[0-9]{10,15}', fullmatch=True)
relationship_strategy = st.sampled_from(['spouse', 'child', 'parent', 'sibling', 'other'])
account_name_strategy = st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_characters='\x00'))
credit_limit_strategy = st.floats(min_value=1000, max_value=100000, allow_nan=False, allow_infinity=False)
price_strategy = st.floats(min_value=100, max_value=10000, allow_nan=False, allow_infinity=False)
member_count_strategy = st.integers(min_value=1, max_value=5)


def create_mock_family_account(account_id, family_account_id, primary_client_id, members_count=2):
    """Helper to create mock family account"""
    members = [
        {
            "client_id": f"client_{i}",
            "name": f"Member {i}",
            "relationship": "spouse" if i == 1 else "child",
            "email": f"member{i}@example.com",
            "phone": f"+1234567890{i}"
        }
        for i in range(members_count)
    ]
    
    return {
        "_id": ObjectId(account_id) if isinstance(account_id, str) else account_id,
        "family_account_id": family_account_id,
        "primary_client_id": primary_client_id,
        "salon_id": "salon_123",
        "account_name": "Test Family",
        "members": members,
        "credit_limit": 5000.0,
        "outstanding_balance": 0.0,
        "total_loyalty_points": 0,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@given(
    account_name=account_name_strategy,
    member_count=member_count_strategy,
    credit_limit=credit_limit_strategy,
)
@settings(max_examples=10)
def test_family_member_addition_removal_consistency(
    account_name, member_count, credit_limit
):
    """
    Property 18: Family member addition/removal consistency
    
    This property validates that adding and removing family members maintains
    consistency in the family account member list.
    """
    import asyncio
    
    async def run_test():
        service = FamilyAccountService()
        
        # Mock the database
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.family_accounts = mock_collection
        mock_db.bookings = MagicMock()
        mock_db.clients = MagicMock()
        
        service._db = mock_db
        service._family_accounts_collection = mock_collection
        service._bookings_collection = mock_db.bookings
        service._clients_collection = mock_db.clients
        
        account_id = str(ObjectId())
        family_account_id = "FAM-TEST123"
        primary_client_id = "primary_client"
        
        # Create initial account with members
        initial_account = create_mock_family_account(
            account_id, family_account_id, primary_client_id, member_count
        )
        
        mock_collection.find_one.return_value = initial_account
        mock_collection.update_one = MagicMock()
        
        # Property: Adding a member should increase member count
        new_member = FamilyMember(
            client_id="new_client",
            name="New Member",
            relationship="sibling",
            email="new@example.com",
            phone="+1234567890"
        )
        
        await service.add_family_member(account_id, new_member)
        
        # Verify update was called with push operation
        assert mock_collection.update_one.called, "Update should be called when adding member"
        call_args = mock_collection.update_one.call_args
        update_dict = call_args[0][1]
        assert "$push" in update_dict, "Should use $push operator to add member"
        
        # Property: Removing a member should decrease member count
        mock_collection.reset_mock()
        mock_collection.find_one.return_value = initial_account
        
        await service.remove_family_member(account_id, "client_1")
        
        # Verify update was called with pull operation
        assert mock_collection.update_one.called, "Update should be called when removing member"
        call_args = mock_collection.update_one.call_args
        update_dict = call_args[0][1]
        assert "$pull" in update_dict, "Should use $pull operator to remove member"
        
        # Property: Cannot remove primary account holder
        with pytest.raises(ValueError, match="Cannot remove primary account holder"):
            await service.remove_family_member(account_id, primary_client_id)
    
    asyncio.run(run_test())


@given(
    member_count=member_count_strategy,
    price_per_booking=price_strategy,
)
@settings(max_examples=10)
def test_family_booking_data_consistency(
    member_count, price_per_booking
):
    """
    Property 19: Family booking data consistency
    
    This property validates that family bookings maintain data consistency
    across multiple members and bookings.
    """
    import asyncio
    
    async def run_test():
        service = FamilyAccountService()
        
        # Mock the database
        mock_db = MagicMock()
        mock_family_collection = MagicMock()
        mock_bookings_collection = MagicMock()
        mock_db.family_accounts = mock_family_collection
        mock_db.bookings = mock_bookings_collection
        mock_db.clients = MagicMock()
        
        service._db = mock_db
        service._family_accounts_collection = mock_family_collection
        service._bookings_collection = mock_bookings_collection
        service._clients_collection = mock_db.clients
        
        account_id = str(ObjectId())
        family_account_id = "FAM-TEST123"
        primary_client_id = "primary_client"
        
        # Create account
        account = create_mock_family_account(
            account_id, family_account_id, primary_client_id, member_count
        )
        
        mock_family_collection.find_one.return_value = account
        mock_bookings_collection.insert_one = MagicMock(return_value=MagicMock(inserted_id=ObjectId()))
        mock_bookings_collection.find_many = MagicMock(return_value=[])
        
        # Create family booking
        booking_data = FamilyBookingCreate(
            client_id="client_1",
            stylist_id="stylist_123",
            service_id="service_123",
            booking_date="2025-02-01",
            total_price=price_per_booking,
            notes="Test booking"
        )
        
        booking_id = await service.create_family_booking(
            booking_data, family_account_id, "salon_123"
        )
        
        # Property: Booking ID should be returned
        assert booking_id is not None, "Booking ID should be returned"
        assert isinstance(booking_id, str), "Booking ID should be string"
        
        # Property: Booking should be inserted with correct family_account_id
        assert mock_bookings_collection.insert_one.called, "Booking should be inserted"
        call_args = mock_bookings_collection.insert_one.call_args[0][0]
        assert call_args["family_account_id"] == family_account_id, "Booking should have correct family_account_id"
        assert call_args["total_price"] == price_per_booking, "Booking should have correct price"
        assert call_args["payment_status"] == "deferred", "Family booking should have deferred payment"
        
        # Property: Family account balance should be updated
        assert mock_family_collection.update_one.called, "Family account should be updated"
        update_call = mock_family_collection.update_one.call_args
        update_dict = update_call[0][1]
        assert "$inc" in update_dict, "Should increment outstanding balance"
        assert update_dict["$inc"]["outstanding_balance"] == price_per_booking, "Balance should increase by booking price"
    
    asyncio.run(run_test())


@given(
    initial_balance=st.floats(min_value=0, max_value=5000, allow_nan=False, allow_infinity=False),
    booking_price=price_strategy,
    credit_limit=credit_limit_strategy,
)
@settings(max_examples=10)
def test_deferred_payment_balance_accuracy(
    initial_balance, booking_price, credit_limit
):
    """
    Property 20: Deferred payment balance accuracy
    
    This property validates that deferred payment balances are calculated
    accurately and credit limits are enforced correctly.
    """
    import asyncio
    
    async def run_test():
        service = FamilyAccountService()
        
        # Mock the database
        mock_db = MagicMock()
        mock_family_collection = MagicMock()
        mock_bookings_collection = MagicMock()
        mock_db.family_accounts = mock_family_collection
        mock_db.bookings = mock_bookings_collection
        mock_db.clients = MagicMock()
        
        service._db = mock_db
        service._family_accounts_collection = mock_family_collection
        service._bookings_collection = mock_bookings_collection
        service._clients_collection = mock_db.clients
        
        account_id = str(ObjectId())
        family_account_id = "FAM-TEST123"
        primary_client_id = "primary_client"
        
        # Create account with initial balance
        account = create_mock_family_account(
            account_id, family_account_id, primary_client_id, 2
        )
        account["outstanding_balance"] = initial_balance
        account["credit_limit"] = credit_limit
        
        mock_family_collection.find_one.return_value = account
        
        # Mock unpaid bookings
        unpaid_bookings = [
            {"_id": ObjectId(), "total_price": initial_balance}
        ] if initial_balance > 0 else []
        
        mock_bookings_collection.find = MagicMock(return_value=MagicMock(
            sort=MagicMock(return_value=unpaid_bookings)
        ))
        
        # Test credit limit check
        credit_check = await service.check_credit_limit(account_id, booking_price)
        
        # Property: Credit check should return approval status
        assert "approved" in credit_check, "Credit check should return approval status"
        assert isinstance(credit_check["approved"], bool), "Approval should be boolean"
        
        # Property: New balance should be calculated correctly
        expected_new_balance = initial_balance + booking_price
        assert credit_check["new_balance"] == round(expected_new_balance, 2), "New balance should be accurate"
        
        # Property: Approval should match credit limit check
        within_limit = expected_new_balance <= credit_limit
        assert credit_check["approved"] == within_limit, "Approval should match credit limit"
        
        # Property: Available credit should be non-negative when approved
        if credit_check["approved"]:
            assert credit_check["available_credit"] >= 0, "Available credit should be non-negative when approved"
        
        # Property: Current balance should match initial balance
        assert credit_check["current_balance"] == initial_balance, "Current balance should match initial"
        
        # Property: Booking amount should be preserved
        assert credit_check["booking_amount"] == booking_price, "Booking amount should be preserved"
    
    asyncio.run(run_test())


@given(
    payment_amount=price_strategy,
    initial_balance=st.floats(min_value=100, max_value=5000, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=10)
def test_deferred_payment_processing_consistency(
    payment_amount, initial_balance
):
    """
    Property: Deferred payment processing should maintain balance consistency
    
    This property validates that payment processing correctly updates balances
    and marks bookings as paid.
    """
    import asyncio
    
    async def run_test():
        service = FamilyAccountService()
        
        # Mock the database
        mock_db = MagicMock()
        mock_family_collection = MagicMock()
        mock_bookings_collection = MagicMock()
        mock_db.family_accounts = mock_family_collection
        mock_db.bookings = mock_bookings_collection
        mock_db.clients = MagicMock()
        
        service._db = mock_db
        service._family_accounts_collection = mock_family_collection
        service._bookings_collection = mock_bookings_collection
        service._clients_collection = mock_db.clients
        
        account_id = str(ObjectId())
        family_account_id = "FAM-TEST123"
        primary_client_id = "primary_client"
        
        # Create account
        account = create_mock_family_account(
            account_id, family_account_id, primary_client_id, 2
        )
        account["outstanding_balance"] = initial_balance
        
        mock_family_collection.find_one.return_value = account
        
        # Mock unpaid bookings
        unpaid_bookings = [
            {"_id": ObjectId(), "total_price": initial_balance}
        ]
        
        mock_bookings_collection.find = MagicMock(return_value=MagicMock(
            sort=MagicMock(return_value=unpaid_bookings)
        ))
        mock_bookings_collection.update_many = MagicMock()
        
        # Process payment
        result = await service.pay_family_bookings(account_id, payment_amount=payment_amount)
        
        # Property: Result should contain payment details
        assert "amount_paid" in result, "Result should contain amount_paid"
        assert "remaining_balance" in result, "Result should contain remaining_balance"
        
        # Property: Amount paid should not exceed initial balance
        assert result["amount_paid"] <= initial_balance, "Amount paid should not exceed initial balance"
        
        # Property: Remaining balance should be non-negative
        assert result["remaining_balance"] >= 0, "Remaining balance should be non-negative"
        
        # Property: Amount paid + remaining balance should equal initial balance
        total = result["amount_paid"] + result["remaining_balance"]
        assert abs(total - initial_balance) < 0.01, "Amount paid + remaining should equal initial balance"
        
        # Property: Family account should be updated
        assert mock_family_collection.update_one.called, "Family account should be updated"
    
    asyncio.run(run_test())

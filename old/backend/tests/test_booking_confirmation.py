"""
Property-based tests for booking confirmation service
Feature: enhanced-customer-booking, Property 8: Confirmation notification delivery
Validates: Requirements 7, 19
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from hypothesis import given, strategies as st, settings
from app.services.booking_confirmation_service import BookingConfirmationService


# Strategies for generating test data
email_strategy = st.emails()
name_strategy = st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_characters='\x00'))
phone_strategy = st.from_regex(r'\+?[0-9]{10,15}', fullmatch=True)
service_strategy = st.text(min_size=1, max_size=30, alphabet=st.characters(blacklist_characters='\x00'))
stylist_strategy = st.text(min_size=1, max_size=30, alphabet=st.characters(blacklist_characters='\x00'))
date_strategy = st.from_regex(r'\d{4}-\d{2}-\d{2}', fullmatch=True)
time_strategy = st.from_regex(r'\d{2}:\d{2}', fullmatch=True)
code_strategy = st.text(min_size=6, max_size=10, alphabet=st.characters(blacklist_characters='\x00'))
price_strategy = st.floats(min_value=100, max_value=100000, allow_nan=False, allow_infinity=False)


@given(
    email=email_strategy,
    name=name_strategy,
    phone=phone_strategy,
    service=service_strategy,
    stylist=stylist_strategy,
    date=date_strategy,
    time=time_strategy,
    code=code_strategy,
    price=price_strategy,
)
@settings(max_examples=10)
def test_confirmation_result_structure_consistency(
    email, name, phone, service, stylist, date, time, code, price
):
    """
    Property: Confirmation result should have consistent structure
    
    This property validates that the confirmation service always returns
    a result with the expected structure, regardless of input values.
    """
    import asyncio
    
    async def run_test():
        mock_db = MagicMock()
        mock_db.booking_confirmations.insert_one = MagicMock()

        with patch('app.services.booking_confirmation_service.email_service') as mock_email:
            mock_email.send_email = AsyncMock(return_value=True)

            result = await BookingConfirmationService.send_booking_confirmation(
                db=mock_db,
                booking_id="test_booking_123",
                guest_email=email,
                guest_name=name,
                guest_phone=phone,
                service_name=service,
                stylist_name=stylist,
                booking_date=date,
                booking_time=time,
                confirmation_code=code,
                total_price=price,
                preferred_contact="email",
            )

            # Property: Result should have booking_id
            assert "booking_id" in result, "Result should contain booking_id"
            assert result["booking_id"] == "test_booking_123", "booking_id should match input"
            
            # Property: Result should have email_sent status
            assert "email_sent" in result, "Result should contain email_sent status"
            assert isinstance(result["email_sent"], bool), "email_sent should be boolean"
            
            # Property: Result should have sms_sent status
            assert "sms_sent" in result, "Result should contain sms_sent status"
            assert isinstance(result["sms_sent"], bool), "sms_sent should be boolean"
            
            # Property: Result should have errors list
            assert "errors" in result, "Result should contain errors list"
            assert isinstance(result["errors"], list), "errors should be a list"

    asyncio.run(run_test())


@given(
    email=email_strategy,
    name=name_strategy,
    phone=phone_strategy,
    service=service_strategy,
    stylist=stylist_strategy,
    date=date_strategy,
    time=time_strategy,
    code=code_strategy,
    price=price_strategy,
)
@settings(max_examples=10)
def test_confirmation_contains_booking_details(
    email, name, phone, service, stylist, date, time, code, price
):
    """
    Property: Confirmation email should contain all booking details
    
    This property validates that the confirmation email includes all necessary
    booking information for the guest to reference their appointment.
    """
    import asyncio
    
    async def run_test():
        mock_db = MagicMock()
        mock_db.booking_confirmations.insert_one = MagicMock()

        with patch('app.services.booking_confirmation_service.email_service') as mock_email:
            mock_email.send_email = AsyncMock(return_value=True)

            await BookingConfirmationService.send_booking_confirmation(
                db=mock_db,
                booking_id="test_booking_123",
                guest_email=email,
                guest_name=name,
                guest_phone=phone,
                service_name=service,
                stylist_name=stylist,
                booking_date=date,
                booking_time=time,
                confirmation_code=code,
                total_price=price,
                preferred_contact="email",
            )

            # Get the email content that was sent
            call_args = mock_email.send_email.call_args
            email_html = call_args[1]["html"]
            email_text = call_args[1]["text"]

            # Property: Email should contain service name
            assert service in email_html or service in email_text, "Email should contain service name"
            
            # Property: Email should contain stylist name
            assert stylist in email_html or stylist in email_text, "Email should contain stylist name"
            
            # Property: Email should contain booking date
            assert date in email_html or date in email_text, "Email should contain booking date"
            
            # Property: Email should contain booking time
            assert time in email_html or time in email_text, "Email should contain booking time"
            
            # Property: Email should contain confirmation code
            assert code in email_html or code in email_text, "Email should contain confirmation code"

    asyncio.run(run_test())


@given(
    email=email_strategy,
    name=name_strategy,
    phone=phone_strategy,
    service=service_strategy,
    stylist=stylist_strategy,
    date=date_strategy,
    time=time_strategy,
    code=code_strategy,
    price=price_strategy,
)
@settings(max_examples=10)
def test_confirmation_logged_in_database(
    email, name, phone, service, stylist, date, time, code, price
):
    """
    Property: Confirmation should be logged in database for all bookings
    
    This property validates that the confirmation service persists confirmation
    records in the database for audit and tracking purposes.
    """
    import asyncio
    
    async def run_test():
        mock_db = MagicMock()
        mock_db.booking_confirmations.insert_one = MagicMock()

        with patch('app.services.booking_confirmation_service.email_service') as mock_email:
            mock_email.send_email = AsyncMock(return_value=True)

            await BookingConfirmationService.send_booking_confirmation(
                db=mock_db,
                booking_id="test_booking_123",
                guest_email=email,
                guest_name=name,
                guest_phone=phone,
                service_name=service,
                stylist_name=stylist,
                booking_date=date,
                booking_time=time,
                confirmation_code=code,
                total_price=price,
                preferred_contact="email",
            )

            # Property: Database insert should be called
            assert mock_db.booking_confirmations.insert_one.called, "Confirmation should be logged in database"
            
            # Property: Logged confirmation should contain booking_id
            call_args = mock_db.booking_confirmations.insert_one.call_args[0][0]
            assert call_args["booking_id"] == "test_booking_123", "Logged confirmation should contain booking_id"
            
            # Property: Logged confirmation should contain guest email
            assert call_args["guest_email"] == email, "Logged confirmation should contain guest email"
            
            # Property: Logged confirmation should contain confirmation code
            assert call_args["confirmation_code"] == code, "Logged confirmation should contain confirmation code"

    asyncio.run(run_test())

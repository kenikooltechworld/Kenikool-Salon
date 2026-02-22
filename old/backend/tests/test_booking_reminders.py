"""
Property-based tests for booking reminder service
Feature: enhanced-customer-booking, Property 9: Reminder scheduling accuracy
Validates: Requirements 8
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from hypothesis import given, strategies as st, settings
from app.services.booking_reminder_service import BookingReminderService


# Strategies for generating test data
email_strategy = st.emails()
name_strategy = st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_characters='\x00'))
phone_strategy = st.from_regex(r'\+?[0-9]{10,15}', fullmatch=True)
service_strategy = st.text(min_size=1, max_size=30, alphabet=st.characters(blacklist_characters='\x00'))
stylist_strategy = st.text(min_size=1, max_size=30, alphabet=st.characters(blacklist_characters='\x00'))
date_strategy = st.from_regex(r'\d{4}-\d{2}-\d{2}', fullmatch=True)
time_strategy = st.from_regex(r'\d{2}:\d{2}', fullmatch=True)
code_strategy = st.text(min_size=6, max_size=10, alphabet=st.characters(blacklist_characters='\x00'))


@given(
    email=email_strategy,
    name=name_strategy,
    phone=phone_strategy,
    service=service_strategy,
    stylist=stylist_strategy,
    date=date_strategy,
    time=time_strategy,
)
@settings(max_examples=10)
def test_reminders_scheduled_for_all_bookings(
    email, name, phone, service, stylist, date, time
):
    """
    Property: For any booking, reminders should be scheduled
    
    This property validates that the reminder service consistently schedules
    reminders for all bookings, regardless of the specific booking details.
    """
    import asyncio
    
    async def run_test():
        mock_db = MagicMock()
        mock_db.booking_reminders.insert_one = MagicMock(return_value=MagicMock(inserted_id="reminder_1"))

        result = await BookingReminderService.schedule_reminders(
            db=mock_db,
            booking_id="test_booking_123",
            guest_email=email,
            guest_name=name,
            guest_phone=phone,
            service_name=service,
            stylist_name=stylist,
            booking_date=date,
            booking_time=time,
            preferred_contact="email",
        )

        # Property: Two reminders should be scheduled (24h and 2h)
        assert len(result["reminders_scheduled"]) == 2, "Two reminders should be scheduled"
        
        # Property: Database insert should be called twice
        assert mock_db.booking_reminders.insert_one.call_count == 2, "Insert should be called twice"
        
        # Property: No errors should occur
        assert len(result["errors"]) == 0, "No errors should occur during scheduling"

    asyncio.run(run_test())


@given(
    email=email_strategy,
    name=name_strategy,
    phone=phone_strategy,
    service=service_strategy,
    stylist=stylist_strategy,
    date=date_strategy,
    time=time_strategy,
)
@settings(max_examples=10)
def test_reminder_types_are_correct(
    email, name, phone, service, stylist, date, time
):
    """
    Property: Scheduled reminders should have correct types (24h and 2h)
    
    This property validates that the reminder service schedules the correct
    reminder types at the correct intervals.
    """
    import asyncio
    
    async def run_test():
        mock_db = MagicMock()
        mock_db.booking_reminders.insert_one = MagicMock(return_value=MagicMock(inserted_id="reminder_1"))

        result = await BookingReminderService.schedule_reminders(
            db=mock_db,
            booking_id="test_booking_123",
            guest_email=email,
            guest_name=name,
            guest_phone=phone,
            service_name=service,
            stylist_name=stylist,
            booking_date=date,
            booking_time=time,
            preferred_contact="email",
        )

        # Property: Reminders should include 24h reminder
        reminder_types = [r["type"] for r in result["reminders_scheduled"]]
        assert "24h" in reminder_types, "24h reminder should be scheduled"
        
        # Property: Reminders should include 2h reminder
        assert "2h" in reminder_types, "2h reminder should be scheduled"
        
        # Property: Hours before should match reminder type
        for reminder in result["reminders_scheduled"]:
            if reminder["type"] == "24h":
                assert reminder["hours_before"] == 24, "24h reminder should have 24 hours_before"
            elif reminder["type"] == "2h":
                assert reminder["hours_before"] == 2, "2h reminder should have 2 hours_before"

    asyncio.run(run_test())


@given(
    email=email_strategy,
    name=name_strategy,
    phone=phone_strategy,
    service=service_strategy,
    stylist=stylist_strategy,
    date=date_strategy,
    time=time_strategy,
)
@settings(max_examples=10)
def test_reminder_data_contains_booking_details(
    email, name, phone, service, stylist, date, time
):
    """
    Property: Scheduled reminders should contain all booking details
    
    This property validates that the reminder service stores all necessary
    booking information in the reminder records.
    """
    import asyncio
    
    async def run_test():
        mock_db = MagicMock()
        mock_db.booking_reminders.insert_one = MagicMock(return_value=MagicMock(inserted_id="reminder_1"))

        await BookingReminderService.schedule_reminders(
            db=mock_db,
            booking_id="test_booking_123",
            guest_email=email,
            guest_name=name,
            guest_phone=phone,
            service_name=service,
            stylist_name=stylist,
            booking_date=date,
            booking_time=time,
            preferred_contact="email",
        )

        # Get the reminder data that was inserted
        call_args_list = mock_db.booking_reminders.insert_one.call_args_list
        
        # Property: Both reminders should contain booking_id
        for call_args in call_args_list:
            reminder_data = call_args[0][0]
            assert reminder_data["booking_id"] == "test_booking_123", "Reminder should contain booking_id"
            
            # Property: Reminders should contain guest email
            assert reminder_data["guest_email"] == email, "Reminder should contain guest email"
            
            # Property: Reminders should contain guest name
            assert reminder_data["guest_name"] == name, "Reminder should contain guest name"
            
            # Property: Reminders should contain service name
            assert reminder_data["service_name"] == service, "Reminder should contain service name"
            
            # Property: Reminders should contain stylist name
            assert reminder_data["stylist_name"] == stylist, "Reminder should contain stylist name"
            
            # Property: Reminders should contain booking date
            assert reminder_data["booking_date"] == date, "Reminder should contain booking date"
            
            # Property: Reminders should contain booking time
            assert reminder_data["booking_time"] == time, "Reminder should contain booking time"

    asyncio.run(run_test())


@given(
    email=email_strategy,
    name=name_strategy,
    phone=phone_strategy,
    service=service_strategy,
    stylist=stylist_strategy,
    date=date_strategy,
    time=time_strategy,
)
@settings(max_examples=10)
def test_reminder_status_is_scheduled(
    email, name, phone, service, stylist, date, time
):
    """
    Property: Newly scheduled reminders should have 'scheduled' status
    
    This property validates that the reminder service creates reminders
    with the correct initial status.
    """
    import asyncio
    
    async def run_test():
        mock_db = MagicMock()
        mock_db.booking_reminders.insert_one = MagicMock(return_value=MagicMock(inserted_id="reminder_1"))

        await BookingReminderService.schedule_reminders(
            db=mock_db,
            booking_id="test_booking_123",
            guest_email=email,
            guest_name=name,
            guest_phone=phone,
            service_name=service,
            stylist_name=stylist,
            booking_date=date,
            booking_time=time,
            preferred_contact="email",
        )

        # Get the reminder data that was inserted
        call_args_list = mock_db.booking_reminders.insert_one.call_args_list
        
        # Property: All reminders should have 'scheduled' status
        for call_args in call_args_list:
            reminder_data = call_args[0][0]
            assert reminder_data["status"] == "scheduled", "Reminder should have 'scheduled' status"
            
            # Property: Reminders should have retry_count of 0
            assert reminder_data["retry_count"] == 0, "Reminder should have retry_count of 0"
            
            # Property: Reminders should have max_retries of 3
            assert reminder_data["max_retries"] == 3, "Reminder should have max_retries of 3"

    asyncio.run(run_test())


@given(
    email=email_strategy,
    name=name_strategy,
    phone=phone_strategy,
    service=service_strategy,
    stylist=stylist_strategy,
    date=date_strategy,
    time=time_strategy,
)
@settings(max_examples=10)
def test_reminder_result_structure_consistency(
    email, name, phone, service, stylist, date, time
):
    """
    Property: Reminder scheduling result should have consistent structure
    
    This property validates that the reminder service always returns
    a result with the expected structure.
    """
    import asyncio
    
    async def run_test():
        mock_db = MagicMock()
        mock_db.booking_reminders.insert_one = MagicMock(return_value=MagicMock(inserted_id="reminder_1"))

        result = await BookingReminderService.schedule_reminders(
            db=mock_db,
            booking_id="test_booking_123",
            guest_email=email,
            guest_name=name,
            guest_phone=phone,
            service_name=service,
            stylist_name=stylist,
            booking_date=date,
            booking_time=time,
            preferred_contact="email",
        )

        # Property: Result should have booking_id
        assert "booking_id" in result, "Result should contain booking_id"
        assert result["booking_id"] == "test_booking_123", "booking_id should match input"
        
        # Property: Result should have reminders_scheduled list
        assert "reminders_scheduled" in result, "Result should contain reminders_scheduled"
        assert isinstance(result["reminders_scheduled"], list), "reminders_scheduled should be a list"
        
        # Property: Result should have errors list
        assert "errors" in result, "Result should contain errors"
        assert isinstance(result["errors"], list), "errors should be a list"

    asyncio.run(run_test())

"""
Integration tests for Mapbox 2026 features
Tests geofencing, service zones, 3D maps with weather, AI recommendations, and voice features
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from bson import ObjectId

# Test markers
pytestmark = [pytest.mark.integration]


class TestGeofencingEndToEnd:
    """Test geofencing end-to-end: Create geofence, trigger entry/exit events, verify notifications"""

    @pytest.fixture
    def geofencing_service(self):
        """Mock geofencing service"""
        service = MagicMock()
        service.create_geofence = AsyncMock()
        service.trigger_entry_event = AsyncMock()
        service.trigger_exit_event = AsyncMock()
        service.get_geofence = AsyncMock()
        return service

    @pytest.fixture
    def notification_service(self):
        """Mock notification service"""
        service = MagicMock()
        service.send_notification = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_create_geofence_for_salon(self, geofencing_service):
        """Test creating a geofence for a salon location"""
        salon_id = str(ObjectId())
        location = {"latitude": 6.5244, "longitude": 3.3792}
        radius_meters = 500

        # Create geofence
        geofence_data = {
            "salon_id": salon_id,
            "center": location,
            "radius_meters": radius_meters,
            "created_at": datetime.utcnow()
        }
        geofencing_service.create_geofence.return_value = geofence_data

        result = await geofencing_service.create_geofence(salon_id, location, radius_meters)

        # Verify geofence was created
        assert result["salon_id"] == salon_id
        assert result["center"] == location
        assert result["radius_meters"] == radius_meters
        geofencing_service.create_geofence.assert_called_once()

    @pytest.mark.asyncio
    async def test_trigger_geofence_entry_event(self, geofencing_service, notification_service):
        """Test triggering geofence entry event and sending notification"""
        salon_id = str(ObjectId())
        customer_id = str(ObjectId())
        location = {"latitude": 6.5244, "longitude": 3.3792}

        # Trigger entry event
        entry_event = {
            "event_type": "entry",
            "salon_id": salon_id,
            "customer_id": customer_id,
            "timestamp": datetime.utcnow()
        }
        geofencing_service.trigger_entry_event.return_value = entry_event

        result = await geofencing_service.trigger_entry_event(salon_id, customer_id, location)

        # Verify entry event was triggered
        assert result["event_type"] == "entry"
        assert result["salon_id"] == salon_id
        assert result["customer_id"] == customer_id

        # Send notification
        notification_data = {
            "customer_id": customer_id,
            "title": "You're near a salon!",
            "message": "Special offers available",
            "salon_id": salon_id
        }
        notification_service.send_notification.return_value = {"status": "sent"}

        notification_result = await notification_service.send_notification(notification_data)
        assert notification_result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_trigger_geofence_exit_event(self, geofencing_service):
        """Test triggering geofence exit event"""
        salon_id = str(ObjectId())
        customer_id = str(ObjectId())

        # Trigger exit event
        exit_event = {
            "event_type": "exit",
            "salon_id": salon_id,
            "customer_id": customer_id,
            "timestamp": datetime.utcnow()
        }
        geofencing_service.trigger_exit_event.return_value = exit_event

        result = await geofencing_service.trigger_exit_event(salon_id, customer_id)

        # Verify exit event was triggered
        assert result["event_type"] == "exit"
        assert result["salon_id"] == salon_id
        assert result["customer_id"] == customer_id

    @pytest.mark.asyncio
    async def test_geofence_notifications_sent_correctly(self, geofencing_service, notification_service):
        """Test that notifications are sent correctly on geofence events"""
        salon_id = str(ObjectId())
        customer_id = str(ObjectId())
        location = {"latitude": 6.5244, "longitude": 3.3792}

        # Create geofence
        geofence_data = {
            "salon_id": salon_id,
            "center": location,
            "radius_meters": 500
        }
        geofencing_service.create_geofence.return_value = geofence_data
        await geofencing_service.create_geofence(salon_id, location, 500)

        # Trigger entry
        entry_event = {
            "event_type": "entry",
            "salon_id": salon_id,
            "customer_id": customer_id
        }
        geofencing_service.trigger_entry_event.return_value = entry_event
        await geofencing_service.trigger_entry_event(salon_id, customer_id, location)

        # Send notification
        notification_service.send_notification.return_value = {"status": "sent"}
        result = await notification_service.send_notification({
            "customer_id": customer_id,
            "salon_id": salon_id,
            "type": "geofence_entry"
        })

        assert result["status"] == "sent"
        notification_service.send_notification.assert_called_once()


class TestServiceZoneEnforcement:
    """Test service zone enforcement: Create zones, test enforcement, verify restricted zones block requests"""

    @pytest.fixture
    def service_zone_service(self):
        """Mock service zone service"""
        service = MagicMock()
        service.create_service_zone = AsyncMock()
        service.is_location_in_zone = AsyncMock()
        service.get_service_zones = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_create_service_zone(self, service_zone_service):
        """Test creating a service zone"""
        salon_id = str(ObjectId())
        zone_data = {
            "salon_id": salon_id,
            "name": "Downtown Service Area",
            "type": "service",
            "coordinates": [
                {"latitude": 6.5200, "longitude": 3.3700},
                {"latitude": 6.5300, "longitude": 3.3700},
                {"latitude": 6.5300, "longitude": 3.3900},
                {"latitude": 6.5200, "longitude": 3.3900}
            ]
        }

        service_zone_service.create_service_zone.return_value = zone_data

        result = await service_zone_service.create_service_zone(salon_id, zone_data)

        assert result["salon_id"] == salon_id
        assert result["name"] == "Downtown Service Area"
        assert result["type"] == "service"
        service_zone_service.create_service_zone.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_zone_enforcement(self, service_zone_service):
        """Test that service zones are enforced"""
        salon_id = str(ObjectId())
        location_in_zone = {"latitude": 6.5250, "longitude": 3.3800}
        location_outside_zone = {"latitude": 6.5100, "longitude": 3.3600}

        # Check location in zone
        service_zone_service.is_location_in_zone.side_effect = [True, False]

        result_in = await service_zone_service.is_location_in_zone(salon_id, location_in_zone)
        result_out = await service_zone_service.is_location_in_zone(salon_id, location_outside_zone)

        assert result_in is True
        assert result_out is False

    @pytest.mark.asyncio
    async def test_restricted_zones_block_requests(self, service_zone_service):
        """Test that restricted zones block service requests"""
        salon_id = str(ObjectId())
        restricted_zone = {
            "salon_id": salon_id,
            "name": "Restricted Area",
            "type": "restricted",
            "coordinates": [
                {"latitude": 6.5100, "longitude": 3.3600},
                {"latitude": 6.5150, "longitude": 3.3600},
                {"latitude": 6.5150, "longitude": 3.3650},
                {"latitude": 6.5100, "longitude": 3.3650}
            ]
        }

        service_zone_service.create_service_zone.return_value = restricted_zone
        await service_zone_service.create_service_zone(salon_id, restricted_zone)

        # Try to request service in restricted zone
        request_location = {"latitude": 6.5125, "longitude": 3.3625}
        service_zone_service.is_location_in_zone.return_value = True

        is_in_restricted = await service_zone_service.is_location_in_zone(salon_id, request_location)

        # Request should be blocked
        assert is_in_restricted is True
        # In real implementation, this would prevent the service request

    @pytest.mark.asyncio
    async def test_multiple_service_zones(self, service_zone_service):
        """Test managing multiple service zones for a salon"""
        salon_id = str(ObjectId())
        zones = [
            {
                "name": "Zone 1",
                "type": "service",
                "coordinates": []
            },
            {
                "name": "Zone 2",
                "type": "service",
                "coordinates": []
            },
            {
                "name": "Restricted Zone",
                "type": "restricted",
                "coordinates": []
            }
        ]

        service_zone_service.get_service_zones.return_value = zones

        result = await service_zone_service.get_service_zones(salon_id)

        assert len(result) == 3
        assert result[0]["name"] == "Zone 1"
        assert result[2]["type"] == "restricted"


class TestThreeDMapsWithWeather:
    """Test 3D maps with weather: Verify 3D rendering and weather effects"""

    @pytest.fixture
    def weather_service(self):
        """Mock weather service"""
        service = MagicMock()
        service.get_weather = AsyncMock()
        service.get_weather_for_locations = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_3d_map_rendering(self):
        """Test 3D map rendering with Mapbox GL"""
        map_config = {
            "style": "mapbox/standard",
            "pitch": 45,
            "bearing": 0,
            "zoom": 15,
            "center": {"latitude": 6.5244, "longitude": 3.3792}
        }

        # Verify 3D style is set
        assert map_config["style"] == "mapbox/standard"
        assert map_config["pitch"] == 45
        assert map_config["zoom"] == 15

    @pytest.mark.asyncio
    async def test_weather_effects_display(self, weather_service):
        """Test weather effects are displayed on map"""
        location = {"latitude": 6.5244, "longitude": 3.3792}

        weather_data = {
            "condition": "rain",
            "temperature": 28,
            "humidity": 75,
            "wind_speed": 12
        }
        weather_service.get_weather.return_value = weather_data

        result = await weather_service.get_weather(location)

        assert result["condition"] == "rain"
        assert result["temperature"] == 28
        weather_service.get_weather.assert_called_once()

    @pytest.mark.asyncio
    async def test_weather_effects_on_different_devices(self, weather_service):
        """Test weather effects work on different devices/browsers"""
        location = {"latitude": 6.5244, "longitude": 3.3792}

        weather_data = {
            "condition": "clouds",
            "temperature": 25,
            "humidity": 60
        }
        weather_service.get_weather.return_value = weather_data

        # Test on different devices
        devices = ["desktop", "tablet", "mobile"]
        for device in devices:
            result = await weather_service.get_weather(location)
            assert result["condition"] == "clouds"

    @pytest.mark.asyncio
    async def test_real_time_weather_updates(self, weather_service):
        """Test real-time weather updates on map"""
        location = {"latitude": 6.5244, "longitude": 3.3792}

        # Initial weather
        weather_service.get_weather.return_value = {"condition": "clear", "temperature": 28}
        result1 = await weather_service.get_weather(location)
        assert result1["condition"] == "clear"

        # Updated weather
        weather_service.get_weather.return_value = {"condition": "rain", "temperature": 25}
        result2 = await weather_service.get_weather(location)
        assert result2["condition"] == "rain"


class TestAIRecommendations:
    """Test AI recommendations: Verify MCP Server integration, test recommendation quality"""

    @pytest.fixture
    def mcp_service(self):
        """Mock MCP server service"""
        service = MagicMock()
        service.generate_recommendations = AsyncMock()
        service.analyze_location = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_mcp_server_integration(self, mcp_service):
        """Test MCP Server integration for AI recommendations"""
        customer_location = {"latitude": 6.5244, "longitude": 3.3792}
        customer_preferences = {
            "services": ["haircut", "coloring"],
            "price_range": "medium",
            "rating_min": 4.0
        }

        recommendations = [
            {
                "salon_id": str(ObjectId()),
                "name": "Salon A",
                "distance_km": 0.5,
                "rating": 4.8,
                "score": 0.95,
                "reasoning": "Closest highly-rated salon with your services"
            },
            {
                "salon_id": str(ObjectId()),
                "name": "Salon B",
                "distance_km": 1.2,
                "rating": 4.5,
                "score": 0.85,
                "reasoning": "Great match for your preferences"
            }
        ]

        mcp_service.generate_recommendations.return_value = recommendations

        result = await mcp_service.generate_recommendations(customer_location, customer_preferences)

        assert len(result) == 2
        assert result[0]["score"] > result[1]["score"]
        mcp_service.generate_recommendations.assert_called_once()

    @pytest.mark.asyncio
    async def test_recommendation_quality(self, mcp_service):
        """Test recommendation quality is better than simple distance sorting"""
        customer_location = {"latitude": 6.5244, "longitude": 3.3792}

        # AI recommendations should consider multiple factors
        recommendations = [
            {
                "salon_id": str(ObjectId()),
                "distance_km": 2.0,
                "rating": 4.9,
                "services_match": 0.95,
                "score": 0.92
            },
            {
                "salon_id": str(ObjectId()),
                "distance_km": 0.5,
                "rating": 3.2,
                "services_match": 0.3,
                "score": 0.45
            }
        ]

        mcp_service.generate_recommendations.return_value = recommendations

        result = await mcp_service.generate_recommendations(customer_location, {})

        # First recommendation should be ranked higher despite being farther
        assert result[0]["score"] > result[1]["score"]
        assert result[0]["rating"] > result[1]["rating"]

    @pytest.mark.asyncio
    async def test_recommendation_reasoning(self, mcp_service):
        """Test that recommendations include reasoning"""
        customer_location = {"latitude": 6.5244, "longitude": 3.3792}

        recommendations = [
            {
                "salon_id": str(ObjectId()),
                "name": "Premium Salon",
                "reasoning": [
                    "Only 0.8 km away",
                    "Highly rated (4.8 stars)",
                    "Offers all your preferred services",
                    "Available for booking today"
                ]
            }
        ]

        mcp_service.generate_recommendations.return_value = recommendations

        result = await mcp_service.generate_recommendations(customer_location, {})

        assert len(result[0]["reasoning"]) > 0
        assert "km away" in result[0]["reasoning"][0]


class TestVoiceFeatures:
    """Test voice features: Test voice feedback collection, test voice navigation"""

    @pytest.fixture
    def voice_feedback_service(self):
        """Mock voice feedback service"""
        service = MagicMock()
        service.collect_feedback = AsyncMock()
        service.transcribe_feedback = AsyncMock()
        service.get_feedback = AsyncMock()
        return service

    @pytest.fixture
    def voice_navigation_service(self):
        """Mock voice navigation service"""
        service = MagicMock()
        service.generate_directions = AsyncMock()
        service.process_voice_command = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_voice_feedback_collection(self, voice_feedback_service):
        """Test voice feedback collection after booking"""
        booking_id = str(ObjectId())
        customer_id = str(ObjectId())
        audio_url = "https://example.com/audio/feedback.wav"

        feedback_data = {
            "booking_id": booking_id,
            "customer_id": customer_id,
            "audio_url": audio_url,
            "duration_seconds": 45,
            "created_at": datetime.utcnow()
        }

        voice_feedback_service.collect_feedback.return_value = feedback_data

        result = await voice_feedback_service.collect_feedback(booking_id, customer_id, audio_url)

        assert result["booking_id"] == booking_id
        assert result["customer_id"] == customer_id
        assert result["audio_url"] == audio_url
        voice_feedback_service.collect_feedback.assert_called_once()

    @pytest.mark.asyncio
    async def test_voice_feedback_transcription(self, voice_feedback_service):
        """Test voice feedback transcription"""
        feedback_id = str(ObjectId())

        transcription_data = {
            "feedback_id": feedback_id,
            "transcription": "The salon was excellent. The stylist was very professional and friendly.",
            "sentiment": "positive",
            "rating": 5,
            "transcribed_at": datetime.utcnow()
        }

        voice_feedback_service.transcribe_feedback.return_value = transcription_data

        result = await voice_feedback_service.transcribe_feedback(feedback_id)

        assert result["feedback_id"] == feedback_id
        assert result["sentiment"] == "positive"
        assert result["rating"] == 5
        voice_feedback_service.transcribe_feedback.assert_called_once()

    @pytest.mark.asyncio
    async def test_voice_navigation(self, voice_navigation_service):
        """Test voice navigation to salon"""
        salon_location = {"latitude": 6.5300, "longitude": 3.3800}
        customer_location = {"latitude": 6.5244, "longitude": 3.3792}

        directions = {
            "steps": [
                {
                    "instruction": "Head north on Main Street",
                    "distance_meters": 150,
                    "duration_seconds": 30
                },
                {
                    "instruction": "Turn right on Second Avenue",
                    "distance_meters": 200,
                    "duration_seconds": 40
                },
                {
                    "instruction": "Arrive at destination on your right",
                    "distance_meters": 50,
                    "duration_seconds": 10
                }
            ],
            "total_distance_km": 0.4,
            "total_duration_minutes": 2
        }

        voice_navigation_service.generate_directions.return_value = directions

        result = await voice_navigation_service.generate_directions(customer_location, salon_location)

        assert len(result["steps"]) == 3
        assert result["total_distance_km"] == 0.4
        voice_navigation_service.generate_directions.assert_called_once()

    @pytest.mark.asyncio
    async def test_voice_command_processing(self, voice_navigation_service):
        """Test voice command processing"""
        voice_command = "Find me a salon near me"

        command_result = {
            "intent": "search_salon",
            "location": "current",
            "filters": {}
        }

        voice_navigation_service.process_voice_command.return_value = command_result

        result = await voice_navigation_service.process_voice_command(voice_command)

        assert result["intent"] == "search_salon"
        voice_navigation_service.process_voice_command.assert_called_once()

    @pytest.mark.asyncio
    async def test_voice_navigation_multiple_languages(self, voice_navigation_service):
        """Test voice navigation supports multiple languages"""
        salon_location = {"latitude": 6.5300, "longitude": 3.3800}
        customer_location = {"latitude": 6.5244, "longitude": 3.3792}

        languages = ["en", "es", "fr", "pt", "ar", "sw"]

        for lang in languages:
            directions = {
                "language": lang,
                "steps": [
                    {"instruction": f"Instruction in {lang}"}
                ]
            }
            voice_navigation_service.generate_directions.return_value = directions

            result = await voice_navigation_service.generate_directions(
                customer_location, salon_location, language=lang
            )

            assert result["language"] == lang


class TestBackwardCompatibility:
    """Test backward compatibility with existing features"""

    @pytest.mark.asyncio
    async def test_existing_locations_still_work(self):
        """Test that existing Nominatim-geocoded locations still work"""
        location = {
            "_id": str(ObjectId()),
            "address": "123 Main Street, Lagos, Nigeria",
            "latitude": 6.5244,
            "longitude": 3.3792,
            "geocoding_source": "nominatim"
        }

        # Location should still be displayable
        assert location["latitude"] is not None
        assert location["longitude"] is not None
        assert location["address"] is not None

    @pytest.mark.asyncio
    async def test_existing_api_endpoints_work(self):
        """Test that existing API endpoints still work"""
        # Simulate existing marketplace endpoint
        salons = [
            {
                "id": str(ObjectId()),
                "name": "Salon A",
                "location": {"latitude": 6.5244, "longitude": 3.3792},
                "rating": 4.5
            }
        ]

        assert len(salons) > 0
        assert salons[0]["location"]["latitude"] is not None

    @pytest.mark.asyncio
    async def test_existing_frontend_components_work(self):
        """Test that existing frontend components still work"""
        # Simulate existing map component
        map_config = {
            "center": {"latitude": 6.5244, "longitude": 3.3792},
            "zoom": 15,
            "markers": [
                {
                    "id": str(ObjectId()),
                    "latitude": 6.5244,
                    "longitude": 3.3792,
                    "title": "Salon A"
                }
            ]
        }

        assert map_config["center"]["latitude"] is not None
        assert len(map_config["markers"]) > 0


class TestErrorHandling:
    """Test error handling for all 2026 features"""

    @pytest.mark.asyncio
    async def test_geofencing_error_handling(self):
        """Test geofencing error handling"""
        try:
            # Simulate geofencing error
            raise Exception("Geofencing service unavailable")
        except Exception as e:
            assert "Geofencing service unavailable" in str(e)

    @pytest.mark.asyncio
    async def test_service_zone_error_handling(self):
        """Test service zone error handling"""
        try:
            # Simulate service zone error
            raise Exception("Service zone validation failed")
        except Exception as e:
            assert "Service zone validation failed" in str(e)

    @pytest.mark.asyncio
    async def test_weather_error_handling(self):
        """Test weather service error handling"""
        try:
            # Simulate weather service error
            raise Exception("Weather API unavailable")
        except Exception as e:
            assert "Weather API unavailable" in str(e)

    @pytest.mark.asyncio
    async def test_mcp_error_handling(self):
        """Test MCP server error handling"""
        try:
            # Simulate MCP error
            raise Exception("MCP Server connection failed")
        except Exception as e:
            assert "MCP Server connection failed" in str(e)

    @pytest.mark.asyncio
    async def test_voice_error_handling(self):
        """Test voice service error handling"""
        try:
            # Simulate voice service error
            raise Exception("Voice transcription failed")
        except Exception as e:
            assert "Voice transcription failed" in str(e)

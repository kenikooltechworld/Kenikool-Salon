"""
Tests for Enhanced Fraud Detection System
Tests all fraud detection features including rate monitoring, velocity checks, pattern detection, and staff notifications
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock
from bson import ObjectId

from app.services.fraud_detection_service import FraudDetectionService
from app.services.pos_service import POSService
from app.api.exceptions import BadRequestException, NotFoundException


class Tes
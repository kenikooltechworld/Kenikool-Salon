"""
Unit tests for package audit service
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.package_audit_service import PackageAuditService


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = MagicMock()
    db.package_audit_logs = MagicMock()
    return db


@pytest.fixture
def audit_service(mock_db):
    """Create an audit service instance"""
    return PackageAuditService(mock_db)


class TestPackageAuditService:
    """Test cases for PackageAuditService"""

    @pytest.mark.asyncio
    async def test_log_action_creates_audit_log(self, audit_service, mock_db):
        """Test that log_action creates an audit log entry"""
        # Arrange
        tenant_id = "test_tenant"
        action_type = "purchase"
        entity_type = "purchase"
        entity_id = "purchase_123"
        user_id = "user_456"
        role = "staff"
        client_id = "client_789"
        details = {"amount": 100.0, "package_name": "Premium Package"}

        mock_db.package_audit_logs.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )

        # Act
        result = await audit_service.log_action(
            tenant_id=tenant_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            performed_by_user_id=user_id,
            performed_by_role=role,
            client_id=client_id,
            details=details,
        )

        # Assert
        assert result is not None
        mock_db.package_audit_logs.insert_one.assert_called_once()
        call_args = mock_db.package_audit_logs.insert_one.call_args[0][0]
        assert call_args["tenant_id"] == tenant_id
        assert call_args["action_type"] == action_type
        assert call_args["entity_type"] == entity_type
        assert call_args["entity_id"] == entity_id
        assert call_args["performed_by_user_id"] == user_id
        assert call_args["performed_by_role"] == role
        assert call_args["client_id"] == client_id
        assert call_args["details"] == details

    @pytest.mark.asyncio
    async def test_log_package_creation(self, audit_service, mock_db):
        """Test logging package creation"""
        # Arrange
        tenant_id = "test_tenant"
        package_id = "pkg_123"
        user_id = "user_456"
        role = "admin"
        package_name = "Premium Package"
        package_price = 99.99

        mock_db.package_audit_logs.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )

        # Act
        result = await audit_service.log_package_creation(
            tenant_id=tenant_id,
            package_id=package_id,
            performed_by_user_id=user_id,
            performed_by_role=role,
            package_name=package_name,
            package_price=package_price,
        )

        # Assert
        assert result is not None
        call_args = mock_db.package_audit_logs.insert_one.call_args[0][0]
        assert call_args["action_type"] == "create"
        assert call_args["entity_type"] == "definition"
        assert call_args["details"]["package_name"] == package_name
        assert call_args["details"]["package_price"] == package_price

    @pytest.mark.asyncio
    async def test_log_package_purchase(self, audit_service, mock_db):
        """Test logging package purchase"""
        # Arrange
        tenant_id = "test_tenant"
        purchase_id = "purchase_123"
        user_id = "user_456"
        role = "staff"
        client_id = "client_789"
        package_name = "Premium Package"
        amount = 99.99
        is_gift = False

        mock_db.package_audit_logs.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )

        # Act
        result = await audit_service.log_package_purchase(
            tenant_id=tenant_id,
            purchase_id=purchase_id,
            performed_by_user_id=user_id,
            performed_by_role=role,
            client_id=client_id,
            package_name=package_name,
            amount=amount,
            is_gift=is_gift,
        )

        # Assert
        assert result is not None
        call_args = mock_db.package_audit_logs.insert_one.call_args[0][0]
        assert call_args["action_type"] == "purchase"
        assert call_args["entity_type"] == "purchase"
        assert call_args["client_id"] == client_id
        assert call_args["details"]["amount"] == amount
        assert call_args["details"]["is_gift"] == is_gift

    @pytest.mark.asyncio
    async def test_log_package_redemption(self, audit_service, mock_db):
        """Test logging package redemption"""
        # Arrange
        tenant_id = "test_tenant"
        purchase_id = "purchase_123"
        user_id = "user_456"
        role = "staff"
        client_id = "client_789"
        service_name = "Haircut"
        service_value = 50.0

        mock_db.package_audit_logs.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )

        # Act
        result = await audit_service.log_package_redemption(
            tenant_id=tenant_id,
            purchase_id=purchase_id,
            performed_by_user_id=user_id,
            performed_by_role=role,
            client_id=client_id,
            service_name=service_name,
            service_value=service_value,
        )

        # Assert
        assert result is not None
        call_args = mock_db.package_audit_logs.insert_one.call_args[0][0]
        assert call_args["action_type"] == "redeem"
        assert call_args["entity_type"] == "credit"
        assert call_args["details"]["service_name"] == service_name
        assert call_args["details"]["service_value"] == service_value

    @pytest.mark.asyncio
    async def test_log_package_transfer(self, audit_service, mock_db):
        """Test logging package transfer"""
        # Arrange
        tenant_id = "test_tenant"
        purchase_id = "purchase_123"
        user_id = "user_456"
        role = "staff"
        from_client_id = "client_111"
        to_client_id = "client_222"

        mock_db.package_audit_logs.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )

        # Act
        result = await audit_service.log_package_transfer(
            tenant_id=tenant_id,
            purchase_id=purchase_id,
            performed_by_user_id=user_id,
            performed_by_role=role,
            from_client_id=from_client_id,
            to_client_id=to_client_id,
        )

        # Assert
        assert result is not None
        call_args = mock_db.package_audit_logs.insert_one.call_args[0][0]
        assert call_args["action_type"] == "transfer"
        assert call_args["entity_type"] == "purchase"
        assert call_args["client_id"] == to_client_id
        assert call_args["details"]["from_client_id"] == from_client_id
        assert call_args["details"]["to_client_id"] == to_client_id

    @pytest.mark.asyncio
    async def test_log_package_refund(self, audit_service, mock_db):
        """Test logging package refund"""
        # Arrange
        tenant_id = "test_tenant"
        purchase_id = "purchase_123"
        user_id = "user_456"
        role = "staff"
        client_id = "client_789"
        reason = "Customer request"
        refund_amount = 50.0

        mock_db.package_audit_logs.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )

        # Act
        result = await audit_service.log_package_refund(
            tenant_id=tenant_id,
            purchase_id=purchase_id,
            performed_by_user_id=user_id,
            performed_by_role=role,
            client_id=client_id,
            reason=reason,
            refund_amount=refund_amount,
        )

        # Assert
        assert result is not None
        call_args = mock_db.package_audit_logs.insert_one.call_args[0][0]
        assert call_args["action_type"] == "refund"
        assert call_args["entity_type"] == "purchase"
        assert call_args["details"]["reason"] == reason
        assert call_args["details"]["refund_amount"] == refund_amount

    @pytest.mark.asyncio
    async def test_log_expiration_extension(self, audit_service, mock_db):
        """Test logging expiration extension"""
        # Arrange
        tenant_id = "test_tenant"
        purchase_id = "purchase_123"
        user_id = "user_456"
        role = "staff"
        client_id = "client_789"
        additional_days = 30
        new_expiration = datetime.utcnow() + timedelta(days=30)

        mock_db.package_audit_logs.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )

        # Act
        result = await audit_service.log_expiration_extension(
            tenant_id=tenant_id,
            purchase_id=purchase_id,
            performed_by_user_id=user_id,
            performed_by_role=role,
            client_id=client_id,
            additional_days=additional_days,
            new_expiration_date=new_expiration,
        )

        # Assert
        assert result is not None
        call_args = mock_db.package_audit_logs.insert_one.call_args[0][0]
        assert call_args["action_type"] == "extend"
        assert call_args["entity_type"] == "purchase"
        assert call_args["details"]["additional_days"] == additional_days

    @pytest.mark.asyncio
    async def test_get_audit_logs_with_filters(self, audit_service, mock_db):
        """Test getting audit logs with filters"""
        # Arrange
        tenant_id = "test_tenant"
        action_type = "purchase"
        entity_type = "purchase"
        entity_id = "purchase_123"
        client_id = "client_789"
        page = 1
        page_size = 50

        mock_logs = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "action_type": action_type,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "performed_by_user_id": "user_456",
                "performed_by_role": "staff",
                "client_id": client_id,
                "details": {"amount": 100.0},
                "timestamp": datetime.utcnow(),
            }
        ]

        mock_db.package_audit_logs.count_documents.return_value = 1
        mock_db.package_audit_logs.find.return_value.sort.return_value.skip.return_value.limit.return_value = (
            mock_logs
        )

        # Act
        result = await audit_service.get_audit_logs(
            tenant_id=tenant_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            client_id=client_id,
            page=page,
            page_size=page_size,
        )

        # Assert
        assert result["total"] == 1
        assert len(result["logs"]) == 1
        assert result["page"] == page
        assert result["page_size"] == page_size

    @pytest.mark.asyncio
    async def test_get_audit_logs_with_date_range(self, audit_service, mock_db):
        """Test getting audit logs with date range filter"""
        # Arrange
        tenant_id = "test_tenant"
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()

        mock_logs = []
        mock_db.package_audit_logs.count_documents.return_value = 0
        mock_db.package_audit_logs.find.return_value.sort.return_value.skip.return_value.limit.return_value = (
            mock_logs
        )

        # Act
        result = await audit_service.get_audit_logs(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
        )

        # Assert
        assert result["total"] == 0
        assert len(result["logs"]) == 0

    @pytest.mark.asyncio
    async def test_get_entity_audit_history(self, audit_service, mock_db):
        """Test getting audit history for a specific entity"""
        # Arrange
        tenant_id = "test_tenant"
        entity_id = "purchase_123"

        mock_logs = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "action_type": "purchase",
                "entity_type": "purchase",
                "entity_id": entity_id,
                "performed_by_user_id": "user_456",
                "performed_by_role": "staff",
                "client_id": "client_789",
                "details": {"amount": 100.0},
                "timestamp": datetime.utcnow(),
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "action_type": "redeem",
                "entity_type": "credit",
                "entity_id": entity_id,
                "performed_by_user_id": "user_456",
                "performed_by_role": "staff",
                "client_id": "client_789",
                "details": {"service_name": "Haircut"},
                "timestamp": datetime.utcnow(),
            },
        ]

        mock_db.package_audit_logs.find.return_value.sort.return_value.limit.return_value = (
            mock_logs
        )

        # Act
        result = await audit_service.get_entity_audit_history(
            tenant_id=tenant_id, entity_id=entity_id
        )

        # Assert
        assert len(result) == 2
        assert result[0]["entity_id"] == entity_id
        assert result[1]["entity_id"] == entity_id

    @pytest.mark.asyncio
    async def test_get_user_audit_activity(self, audit_service, mock_db):
        """Test getting audit activity for a specific user"""
        # Arrange
        tenant_id = "test_tenant"
        user_id = "user_456"

        mock_logs = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "action_type": "purchase",
                "entity_type": "purchase",
                "entity_id": "purchase_123",
                "performed_by_user_id": user_id,
                "performed_by_role": "staff",
                "client_id": "client_789",
                "details": {"amount": 100.0},
                "timestamp": datetime.utcnow(),
            }
        ]

        mock_db.package_audit_logs.find.return_value.sort.return_value.limit.return_value = (
            mock_logs
        )

        # Act
        result = await audit_service.get_user_audit_activity(
            tenant_id=tenant_id, performed_by_user_id=user_id
        )

        # Assert
        assert len(result) == 1
        assert result[0]["performed_by_user_id"] == user_id

    @pytest.mark.asyncio
    async def test_get_client_audit_history(self, audit_service, mock_db):
        """Test getting audit history for a specific client"""
        # Arrange
        tenant_id = "test_tenant"
        client_id = "client_789"

        mock_logs = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "action_type": "purchase",
                "entity_type": "purchase",
                "entity_id": "purchase_123",
                "performed_by_user_id": "user_456",
                "performed_by_role": "staff",
                "client_id": client_id,
                "details": {"amount": 100.0},
                "timestamp": datetime.utcnow(),
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "action_type": "redeem",
                "entity_type": "credit",
                "entity_id": "purchase_123",
                "performed_by_user_id": "user_456",
                "performed_by_role": "staff",
                "client_id": client_id,
                "details": {"service_name": "Haircut"},
                "timestamp": datetime.utcnow(),
            },
        ]

        mock_db.package_audit_logs.find.return_value.sort.return_value.limit.return_value = (
            mock_logs
        )

        # Act
        result = await audit_service.get_client_audit_history(
            tenant_id=tenant_id, client_id=client_id
        )

        # Assert
        assert len(result) == 2
        assert result[0]["client_id"] == client_id
        assert result[1]["client_id"] == client_id

    @pytest.mark.asyncio
    async def test_log_action_handles_missing_details(self, audit_service, mock_db):
        """Test that log_action handles missing details gracefully"""
        # Arrange
        tenant_id = "test_tenant"
        action_type = "purchase"
        entity_type = "purchase"
        entity_id = "purchase_123"
        user_id = "user_456"
        role = "staff"

        mock_db.package_audit_logs.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )

        # Act
        result = await audit_service.log_action(
            tenant_id=tenant_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            performed_by_user_id=user_id,
            performed_by_role=role,
        )

        # Assert
        assert result is not None
        call_args = mock_db.package_audit_logs.insert_one.call_args[0][0]
        assert call_args["details"] == {}

    @pytest.mark.asyncio
    async def test_get_audit_logs_pagination(self, audit_service, mock_db):
        """Test pagination in get_audit_logs"""
        # Arrange
        tenant_id = "test_tenant"
        page = 2
        page_size = 25

        mock_logs = []
        mock_db.package_audit_logs.count_documents.return_value = 100
        mock_db.package_audit_logs.find.return_value.sort.return_value.skip.return_value.limit.return_value = (
            mock_logs
        )

        # Act
        result = await audit_service.get_audit_logs(
            tenant_id=tenant_id, page=page, page_size=page_size
        )

        # Assert
        assert result["page"] == page
        assert result["page_size"] == page_size
        assert result["total"] == 100
        assert result["total_pages"] == 4

        # Verify skip was called with correct offset
        skip_call = mock_db.package_audit_logs.find.return_value.sort.return_value.skip
        skip_call.assert_called_once_with((page - 1) * page_size)

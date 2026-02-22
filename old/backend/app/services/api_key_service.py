"""
API Key Service - API key generation, management, and validation
"""
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from bson import ObjectId

from app.database import Database
from app.utils.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class APIKeyException(Exception):
    """Base exception for API key operations"""
    pass


class UnauthorizedException(APIKeyException):
    """Raised when authentication fails"""
    pass


class BadRequestException(APIKeyException):
    """Raised when request is invalid"""
    pass


class NotFoundException(APIKeyException):
    """Raised when resource is not found"""
    pass


class APIKeyService:
    """Service for API key generation, management, and validation"""

    # API Key prefix for display
    KEY_PREFIX_LENGTH = 8
    KEY_LENGTH = 32  # 32 bytes = 256 bits

    @staticmethod
    def _generate_key() -> str:
        """
        Generate secure random API key
        
        Requirements: 4.1, 4.2
        
        Returns:
            Secure random key (32 bytes, hex encoded)
        """
        return secrets.token_hex(APIKeyService.KEY_LENGTH)

    @staticmethod
    def _hash_key(key: str) -> str:
        """
        Hash API key for storage
        
        Requirements: 4.2
        
        Args:
            key: Plain API key
            
        Returns:
            SHA256 hash of the key
        """
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def _get_key_prefix(key: str) -> str:
        """
        Get key prefix for display (first 8 characters)
        
        Args:
            key: Plain API key
            
        Returns:
            Key prefix for display
        """
        return f"sk_live_{key[:APIKeyService.KEY_PREFIX_LENGTH]}"

    @staticmethod
    async def create_api_key(
        user_id: str,
        tenant_id: str,
        name: str,
        expires_at: Optional[datetime] = None,
        permissions: Optional[List[str]] = None
    ) -> Tuple[str, Dict]:
        """
        Create new API key
        
        Requirements: 4.1, 4.2, 4.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            name: Key name
            expires_at: Optional expiration datetime
            permissions: List of permissions (optional)
            
        Returns:
            Tuple of (plain_key, key_metadata_dict)
            
        Raises:
            BadRequestException: If request is invalid
        """
        db = Database.get_db()
        
        # Validate name
        if not name or len(name) > 100:
            raise BadRequestException("Key name must be between 1 and 100 characters")
        
        # Generate secure random key (Requirement 4.1)
        plain_key = APIKeyService._generate_key()
        key_hash = APIKeyService._hash_key(plain_key)
        key_prefix = APIKeyService._get_key_prefix(plain_key)
        
        # Create API key document
        api_key_doc = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "name": name,
            "key_hash": key_hash,
            "key_prefix": key_prefix,
            "permissions": permissions or [],
            "last_used": None,
            "expires_at": expires_at,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        result = db.api_keys.insert_one(api_key_doc)
        key_id = str(result.inserted_id)
        
        logger.info(f"API key created for user {user_id}: {key_id}")
        
        # Return plain key (only time it's visible) and metadata
        return plain_key, {
            "id": key_id,
            "name": name,
            "key": plain_key,
            "key_prefix": key_prefix,
            "created_at": api_key_doc["created_at"],
            "expires_at": expires_at,
            "permissions": permissions or []
        }

    @staticmethod
    async def list_api_keys(user_id: str, tenant_id: str) -> List[Dict]:
        """
        List all API keys for user
        
        Requirements: 4.3, 4.5
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            List of API key metadata (without plain keys)
        """
        db = Database.get_db()
        
        keys = list(db.api_keys.find({
            "user_id": user_id,
            "tenant_id": tenant_id,
            "is_active": True
        }).sort("created_at", -1))
        
        # Convert to response format
        result = []
        for key in keys:
            result.append({
                "id": str(key["_id"]),
                "name": key["name"],
                "key_prefix": key["key_prefix"],
                "created_at": key["created_at"],
                "last_used": key.get("last_used"),
                "expires_at": key.get("expires_at"),
                "is_active": key["is_active"]
            })
        
        return result

    @staticmethod
    async def revoke_api_key(user_id: str, tenant_id: str, key_id: str) -> bool:
        """
        Revoke API key
        
        Requirements: 4.4
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            key_id: API key ID to revoke
            
        Returns:
            True if key revoked successfully
            
        Raises:
            NotFoundException: If key not found
        """
        db = Database.get_db()
        
        result = db.api_keys.update_one(
            {
                "_id": ObjectId(key_id),
                "user_id": user_id,
                "tenant_id": tenant_id
            },
            {
                "$set": {
                    "is_active": False,
                    "revoked_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise NotFoundException("API key not found")
        
        # Clear cache for this key
        cache_key = f"api_key:{key_id}"
        RedisCache.delete(cache_key)
        
        logger.info(f"API key revoked: {key_id}")
        return True

    @staticmethod
    async def validate_api_key(key: str) -> Optional[Dict]:
        """
        Validate API key and return user info
        
        Requirements: 4.5, 4.6
        
        Args:
            key: Plain API key to validate
            
        Returns:
            Dict with user_id, tenant_id, permissions if valid, None otherwise
            
        Raises:
            UnauthorizedException: If key is invalid or expired
        """
        db = Database.get_db()
        
        # Hash the provided key
        key_hash = APIKeyService._hash_key(key)
        
        # Check cache first
        cache_key = f"api_key_validation:{key_hash}"
        cached_result = RedisCache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Find key in database
        api_key = db.api_keys.find_one({
            "key_hash": key_hash,
            "is_active": True
        })
        
        if not api_key:
            raise UnauthorizedException("Invalid API key")
        
        # Check expiration
        if api_key.get("expires_at") and api_key["expires_at"] < datetime.utcnow():
            raise UnauthorizedException("API key has expired")
        
        # Update last_used timestamp (Requirement 4.5)
        db.api_keys.update_one(
            {"_id": api_key["_id"]},
            {"$set": {"last_used": datetime.utcnow()}}
        )
        
        # Prepare result
        result = {
            "user_id": api_key["user_id"],
            "tenant_id": api_key["tenant_id"],
            "key_id": str(api_key["_id"]),
            "permissions": api_key.get("permissions", [])
        }
        
        # Cache result for 1 hour
        RedisCache.set(cache_key, result, timedelta(hours=1))
        
        logger.info(f"API key validated: {api_key['_id']}")
        return result

    @staticmethod
    async def update_api_key_metadata(
        user_id: str,
        tenant_id: str,
        key_id: str,
        name: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        permissions: Optional[List[str]] = None
    ) -> Dict:
        """
        Update API key metadata
        
        Requirements: 4.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            key_id: API key ID
            name: New name (optional)
            expires_at: New expiration (optional)
            permissions: New permissions (optional)
            
        Returns:
            Updated key metadata
            
        Raises:
            NotFoundException: If key not found
        """
        db = Database.get_db()
        
        # Build update dict
        update_dict = {}
        if name is not None:
            if not name or len(name) > 100:
                raise BadRequestException("Key name must be between 1 and 100 characters")
            update_dict["name"] = name
        
        if expires_at is not None:
            update_dict["expires_at"] = expires_at
        
        if permissions is not None:
            update_dict["permissions"] = permissions
        
        if not update_dict:
            raise BadRequestException("No fields to update")
        
        result = db.api_keys.find_one_and_update(
            {
                "_id": ObjectId(key_id),
                "user_id": user_id,
                "tenant_id": tenant_id
            },
            {"$set": update_dict},
            return_document=True
        )
        
        if not result:
            raise NotFoundException("API key not found")
        
        # Clear cache
        cache_key = f"api_key:{key_id}"
        RedisCache.delete(cache_key)
        
        logger.info(f"API key metadata updated: {key_id}")
        
        return {
            "id": str(result["_id"]),
            "name": result["name"],
            "key_prefix": result["key_prefix"],
            "created_at": result["created_at"],
            "last_used": result.get("last_used"),
            "expires_at": result.get("expires_at"),
            "permissions": result.get("permissions", []),
            "is_active": result["is_active"]
        }

    @staticmethod
    async def get_api_key_by_id(
        user_id: str,
        tenant_id: str,
        key_id: str
    ) -> Dict:
        """
        Get API key by ID
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            key_id: API key ID
            
        Returns:
            API key metadata
            
        Raises:
            NotFoundException: If key not found
        """
        db = Database.get_db()
        
        api_key = db.api_keys.find_one({
            "_id": ObjectId(key_id),
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        if not api_key:
            raise NotFoundException("API key not found")
        
        return {
            "id": str(api_key["_id"]),
            "name": api_key["name"],
            "key_prefix": api_key["key_prefix"],
            "created_at": api_key["created_at"],
            "last_used": api_key.get("last_used"),
            "expires_at": api_key.get("expires_at"),
            "permissions": api_key.get("permissions", []),
            "is_active": api_key["is_active"]
        }

    @staticmethod
    async def cleanup_expired_keys() -> int:
        """
        Delete expired API keys (background job)
        
        Returns:
            Number of keys deleted
        """
        db = Database.get_db()
        
        result = db.api_keys.delete_many({
            "expires_at": {"$lt": datetime.utcnow()},
            "is_active": True
        })
        
        logger.info(f"Cleaned up {result.deleted_count} expired API keys")
        return result.deleted_count


# Create singleton instance
api_key_service = APIKeyService()

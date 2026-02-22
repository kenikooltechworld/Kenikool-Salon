"""
Domain service - Business logic for custom domain management
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import dns.resolver
import secrets
import subprocess
import os
import asyncio

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException
from app.services.ssl_service import SSLService
from app.services.domain_notification_service import DomainNotificationService

logger = logging.getLogger(__name__)


class DomainService:
    """Domain service for handling custom domain operations"""
    
    # Platform's main domain
    PLATFORM_DOMAIN = os.getenv("PLATFORM_DOMAIN", "salonapp.com")
    PLATFORM_IP = os.getenv("PLATFORM_IP", "0.0.0.0")
    
    # SSL provisioning retry configuration
    SSL_RETRY_ATTEMPTS = 3
    SSL_RETRY_DELAY = 5  # seconds, will use exponential backoff
    
    def __init__(self):
        self.ssl_service = SSLService()
    
    @staticmethod
    async def create_domain_request(
        tenant_id: str,
        domain: str
    ) -> Dict:
        """
        Create a custom domain request
        
        Returns:
            Dict with domain data and DNS instructions
        """
        db = Database.get_db()
        
        # Check if domain already exists
        existing = db.domains.find_one({"domain": domain})
        if existing:
            if existing["tenant_id"] == tenant_id:
                return DomainService._format_domain_response(existing)
            else:
                raise BadRequestException("Domain is already in use by another salon")
        
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Create domain record
        domain_data = {
            "tenant_id": tenant_id,
            "domain": domain,
            "status": "pending",
            "verification_token": verification_token,
            "ssl_status": "none",
            "ssl_expires_at": None,
            "verified_at": None,
            "activated_at": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.domains.insert_one(domain_data)
        domain_id = str(result.inserted_id)
        
        logger.info(f"Domain request created: {domain_id} for tenant: {tenant_id}")
        
        # Fetch created domain
        domain_doc = db.domains.find_one({"_id": ObjectId(domain_id)})
        return DomainService._format_domain_response(domain_doc)
    
    @staticmethod
    async def verify_domain(
        tenant_id: str,
        domain: str
    ) -> Dict:
        """
        Verify domain DNS configuration
        
        Returns:
            Dict with verification results
        """
        db = Database.get_db()
        notification_service = DomainNotificationService()
        
        # Get domain record
        domain_doc = db.domains.find_one({
            "domain": domain,
            "tenant_id": tenant_id
        })
        
        if not domain_doc:
            raise NotFoundException("Domain not found")
        
        verification_result = {
            "domain": domain,
            "verified": False,
            "dns_records_valid": False,
            "ssl_provisioned": False,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check A record
            a_record_valid = await DomainService._verify_a_record(domain)
            
            # Check TXT record for verification
            txt_record_valid = await DomainService._verify_txt_record(
                domain,
                domain_doc["verification_token"]
            )
            
            verification_result["dns_records_valid"] = a_record_valid and txt_record_valid
            
            if not a_record_valid:
                verification_result["errors"].append(
                    f"A record not pointing to {DomainService.PLATFORM_IP}"
                )
            
            if not txt_record_valid:
                verification_result["errors"].append(
                    "TXT verification record not found or incorrect"
                )
            
            # If DNS is valid, provision SSL with retry logic
            if verification_result["dns_records_valid"]:
                ssl_success, ssl_error = await DomainService._provision_ssl_with_retry(
                    domain,
                    DomainService.SSL_RETRY_ATTEMPTS
                )
                verification_result["ssl_provisioned"] = ssl_success
                
                if not ssl_success:
                    verification_result["warnings"].append(
                        f"SSL certificate provisioning failed: {ssl_error}. Will retry automatically."
                    )
                
                # Update domain status
                update_data = {
                    "status": "verified" if ssl_success else "pending",
                    "verified_at": datetime.utcnow(),
                    "ssl_status": "active" if ssl_success else "pending",
                    "updated_at": datetime.utcnow()
                }
                
                if ssl_success:
                    update_data["activated_at"] = datetime.utcnow()
                    update_data["ssl_expires_at"] = datetime.utcnow() + timedelta(days=90)
                
                db.domains.update_one(
                    {"_id": domain_doc["_id"]},
                    {"$set": update_data}
                )
                
                verification_result["verified"] = ssl_success
                
                logger.info(f"Domain verified: {domain}")
                
                # Send notification
                if ssl_success:
                    await notification_service.send_domain_verified(tenant_id, domain)
                else:
                    await notification_service.send_verification_failed(
                        tenant_id,
                        domain,
                        verification_result["errors"] + verification_result["warnings"]
                    )
            else:
                # Update status to failed
                db.domains.update_one(
                    {"_id": domain_doc["_id"]},
                    {"$set": {
                        "status": "failed",
                        "updated_at": datetime.utcnow()
                    }}
                )
                
                # Send failure notification
                await notification_service.send_verification_failed(
                    tenant_id,
                    domain,
                    verification_result["errors"]
                )
        
        except Exception as e:
            logger.error(f"Domain verification error: {e}", exc_info=True)
            verification_result["errors"].append(str(e))
            
            # Send error notification
            await notification_service.send_verification_failed(
                tenant_id,
                domain,
                verification_result["errors"]
            )
        
        return verification_result
    
    @staticmethod
    async def _verify_a_record(domain: str) -> bool:
        """Verify A record points to platform IP"""
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            answers = resolver.resolve(domain, 'A')
            for rdata in answers:
                if str(rdata) == DomainService.PLATFORM_IP:
                    return True
            return False
        except Exception as e:
            logger.warning(f"A record verification failed for {domain}: {e}")
            return False
    
    @staticmethod
    async def _verify_txt_record(domain: str, expected_token: str) -> bool:
        """Verify TXT record contains verification token"""
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            verification_domain = f"_salon-verify.{domain}"
            answers = resolver.resolve(verification_domain, 'TXT')
            
            for rdata in answers:
                txt_value = str(rdata).strip('"')
                if txt_value == expected_token:
                    return True
            return False
        except Exception as e:
            logger.warning(f"TXT record verification failed for {domain}: {e}")
            return False
    
    @staticmethod
    async def _provision_ssl_with_retry(
        domain: str,
        max_attempts: int = 3
    ) -> tuple:
        """
        Provision SSL certificate with exponential backoff retry logic.
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
        """
        ssl_service = SSLService()
        last_error = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"SSL provisioning attempt {attempt}/{max_attempts} for {domain}")
                
                success, error = await ssl_service.provision_certificate(domain)
                
                if success:
                    logger.info(f"SSL provisioning succeeded for {domain}")
                    return True, None
                else:
                    last_error = error
                    logger.warning(f"SSL provisioning attempt {attempt} failed: {error}")
                    
                    # Don't retry on rate limit or invalid domain errors
                    if error and ("rate limit" in error.lower() or "invalid" in error.lower()):
                        return False, error
                    
                    # Wait before retrying with exponential backoff
                    if attempt < max_attempts:
                        wait_time = DomainService.SSL_RETRY_DELAY * (2 ** (attempt - 1))
                        logger.info(f"Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"SSL provisioning error on attempt {attempt}: {last_error}")
                
                if attempt < max_attempts:
                    wait_time = DomainService.SSL_RETRY_DELAY * (2 ** (attempt - 1))
                    await asyncio.sleep(wait_time)
        
        return False, last_error or "SSL provisioning failed after all retry attempts"
    
    @staticmethod
    async def _provision_ssl(domain: str) -> bool:
        """
        Provision SSL certificate using Let's Encrypt.
        
        Note: This method is kept for backward compatibility.
        Use _provision_ssl_with_retry for new code.
        """
        success, _ = await DomainService._provision_ssl_with_retry(domain, 1)
        return success
    
    @staticmethod
    async def _revoke_ssl(domain: str) -> bool:
        """Revoke SSL certificate"""
        try:
            ssl_service = SSLService()
            success, error = await ssl_service.revoke_certificate(domain)
            
            if success:
                logger.info(f"SSL revocation succeeded for {domain}")
            else:
                logger.error(f"SSL revocation failed for {domain}: {error}")
            
            return success
        except Exception as e:
            logger.error(f"SSL revocation error for {domain}: {e}")
            return False
    
    @staticmethod
    async def get_domains(tenant_id: str) -> List[Dict]:
        """Get all domains for tenant"""
        db = Database.get_db()
        
        domains = list(db.domains.find({"tenant_id": tenant_id}))
        return [DomainService._format_domain_response(d) for d in domains]
    
    @staticmethod
    async def get_domain(domain_id: str, tenant_id: str) -> Dict:
        """Get single domain"""
        db = Database.get_db()
        
        domain_doc = db.domains.find_one({
            "_id": ObjectId(domain_id),
            "tenant_id": tenant_id
        })
        
        if not domain_doc:
            raise NotFoundException("Domain not found")
        
        return DomainService._format_domain_response(domain_doc)
    
    @staticmethod
    async def delete_domain(domain_id: str, tenant_id: str) -> None:
        """Delete custom domain"""
        db = Database.get_db()
        
        domain_doc = db.domains.find_one({
            "_id": ObjectId(domain_id),
            "tenant_id": tenant_id
        })
        
        if not domain_doc:
            raise NotFoundException("Domain not found")
        
        # Revoke SSL certificate if active
        if domain_doc.get("ssl_status") == "active":
            await DomainService._revoke_ssl(domain_doc["domain"])
        
        # Update status to revoked instead of deleting
        db.domains.update_one(
            {"_id": ObjectId(domain_id)},
            {"$set": {
                "status": "revoked",
                "ssl_status": "none",
                "updated_at": datetime.utcnow()
            }}
        )
        
        logger.info(f"Domain revoked: {domain_id}")
    
    @staticmethod
    async def get_dns_instructions(domain_id: str, tenant_id: str) -> List[Dict]:
        """Get DNS configuration instructions"""
        db = Database.get_db()
        
        domain_doc = db.domains.find_one({
            "_id": ObjectId(domain_id),
            "tenant_id": tenant_id
        })
        
        if not domain_doc:
            raise NotFoundException("Domain not found")
        
        domain = domain_doc["domain"]
        verification_token = domain_doc["verification_token"]
        
        return [
            {
                "type": "A",
                "name": "@",
                "value": DomainService.PLATFORM_IP,
                "ttl": 3600,
                "status": "pending"
            },
            {
                "type": "CNAME",
                "name": "www",
                "value": domain,
                "ttl": 3600,
                "status": "pending"
            },
            {
                "type": "TXT",
                "name": "_salon-verify",
                "value": verification_token,
                "ttl": 3600,
                "status": "pending"
            }
        ]
    
    @staticmethod
    def _format_domain_response(domain_doc: Dict) -> Dict:
        """Format domain document for response"""
        return {
            "id": str(domain_doc["_id"]),
            "tenant_id": domain_doc["tenant_id"],
            "domain": domain_doc["domain"],
            "status": domain_doc["status"],
            "verification_token": domain_doc.get("verification_token"),
            "ssl_status": domain_doc["ssl_status"],
            "ssl_expires_at": domain_doc.get("ssl_expires_at"),
            "verified_at": domain_doc.get("verified_at"),
            "activated_at": domain_doc.get("activated_at"),
            "created_at": domain_doc["created_at"],
            "updated_at": domain_doc["updated_at"]
        }


# Singleton instance
domain_service = DomainService()

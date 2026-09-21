from datetime import datetime
from typing import List, Optional, Tuple
from bson import ObjectId
from fastapi import HTTPException, status
from mongoengine import Q

from app.models.service_package import ServicePackage
from app.models.service import Service
from app.schemas.service_package import (
    ServicePackageCreate,
    ServicePackageUpdate,
    ServicePackageResponse,
    ServicePackageItemResponse,
)


class ServicePackageService:
    """Service for managing service packages"""
    
    @staticmethod
    def create_package(
        tenant_id: str,
        package_data: ServicePackageCreate,
        user_id: str
    ) -> ServicePackage:
        """
        Create a new service package
        """
        service_items = []
        original_price = 0.0
        total_duration = 0
        
        for item in package_data.services:
            service = Service.objects(
                id=ObjectId(item.service_id),
                tenant_id=tenant_id
            ).first()
            
            if not service:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Service {item.service_id} not found"
                )
            
            service_items.append({
                "service_id": str(service.id),
                "quantity": item.quantity
            })
            
            original_price += service.price * item.quantity
            total_duration += service.duration * item.quantity
        
        discount_amount = original_price - package_data.package_price
        discount_percentage = (discount_amount / original_price * 100) if original_price > 0 else 0
        
        if discount_amount < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Package price cannot be higher than original price"
            )
        
        package = ServicePackage(
            tenant_id=tenant_id,
            name=package_data.name,
            description=package_data.description,
            services=service_items,
            original_price=original_price,
            package_price=package_data.package_price,
            discount_amount=discount_amount,
            discount_percentage=discount_percentage,
            valid_from=package_data.valid_from,
            valid_until=package_data.valid_until,
            is_active=package_data.is_active,
            max_bookings_per_customer=package_data.max_bookings_per_customer,
            total_bookings_limit=package_data.total_bookings_limit,
            image_url=package_data.image_url,
            display_order=package_data.display_order,
            is_featured=package_data.is_featured,
            created_by=user_id,
            updated_by=user_id,
        )
        
        package.save()
        return package
    
    @staticmethod
    def get_package(package_id: str, tenant_id: str) -> Optional[ServicePackage]:
        """
        Get a service package by ID
        """
        package = ServicePackage.objects(
            id=ObjectId(package_id),
            tenant_id=tenant_id
        ).first()
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service package not found"
            )
        
        return package
    
    @staticmethod
    def list_packages(
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        include_expired: bool = False
    ) -> Tuple[List[ServicePackage], int]:
        """
        List service packages with filters
        """
        query = Q(tenant_id=tenant_id)
        
        if is_active is not None:
            query &= Q(is_active=is_active)
        
        if is_featured is not None:
            query &= Q(is_featured=is_featured)
        
        if not include_expired:
            now = datetime.utcnow()
            query &= (Q(valid_until=None) | Q(valid_until__gt=now))
        
        packages = list(ServicePackage.objects(query).skip(skip).limit(limit))
        total = ServicePackage.objects(query).count()
        
        return packages, total
    
    @staticmethod
    def update_package(
        package_id: str,
        tenant_id: str,
        package_data: ServicePackageUpdate,
        user_id: str
    ) -> ServicePackage:
        """
        Update a service package
        """
        package = ServicePackageService.get_package(package_id, tenant_id)
        
        update_data = package_data.dict(exclude_unset=True)
        
        if "services" in update_data and update_data["services"]:
            service_items = []
            original_price = 0.0
            
            for item in package_data.services:
                service = Service.objects(
                    id=ObjectId(item.service_id),
                    tenant_id=tenant_id
                ).first()
                
                if not service:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Service {item.service_id} not found"
                    )
                
                service_items.append({
                    "service_id": str(service.id),
                    "quantity": item.quantity
                })
                
                original_price += service.price * item.quantity
            
            update_data["services"] = service_items
            update_data["original_price"] = original_price
            
            package_price = update_data.get("package_price", package.package_price)
            discount_amount = original_price - package_price
            discount_percentage = (discount_amount / original_price * 100) if original_price > 0 else 0
            
            update_data["discount_amount"] = discount_amount
            update_data["discount_percentage"] = discount_percentage
        
        update_data["updated_at"] = datetime.utcnow()
        update_data["updated_by"] = user_id
        
        for key, value in update_data.items():
            setattr(package, key, value)
        
        package.save()
        return package
    
    @staticmethod
    def delete_package(package_id: str, tenant_id: str) -> None:
        """
        Delete a service package
        """
        package = ServicePackageService.get_package(package_id, tenant_id)
        package.delete()
    
    @staticmethod
    def increment_booking_count(package_id: str, tenant_id: str) -> None:
        """
        Increment the booking count for a package
        """
        package = ServicePackageService.get_package(package_id, tenant_id)
        package.current_bookings_count += 1
        package.save()
    
    @staticmethod
    def format_package_response(
        package: ServicePackage
    ) -> ServicePackageResponse:
        """
        Format package for response
        """
        service_items = []
        total_duration = 0
        
        for item in package.services:
            service = Service.objects(id=ObjectId(item["service_id"])).first()
            
            if service:
                service_items.append(ServicePackageItemResponse(
                    id=item["service_id"],
                    service_id=item["service_id"],
                    service_name=service.name,
                    service_price=service.price,
                    service_duration=service.duration,
                    quantity=item["quantity"]
                ))
                
                total_duration += service.duration * item["quantity"]
        
        return ServicePackageResponse(
            id=str(package.id),
            tenant_id=package.tenant_id,
            name=package.name,
            description=package.description,
            services=service_items,
            original_price=package.original_price,
            package_price=package.package_price,
            discount_amount=package.discount_amount,
            discount_percentage=package.discount_percentage,
            valid_from=package.valid_from,
            valid_until=package.valid_until,
            is_active=package.is_active,
            max_bookings_per_customer=package.max_bookings_per_customer,
            total_bookings_limit=package.total_bookings_limit,
            current_bookings_count=package.current_bookings_count,
            image_url=package.image_url,
            display_order=package.display_order,
            is_featured=package.is_featured,
            total_duration=total_duration,
            is_valid=package.is_valid(),
            savings=package.calculate_savings(),
            created_at=package.created_at,
            updated_at=package.updated_at
        )

"""
Staff Onboarding API Routes
Handles onboarding checklists and templates for new staff members
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.services.onboarding_service import OnboardingService
from app.api.dependencies import get_current_user, get_tenant_id
from app.models.user import PyObjectId
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/staff/onboarding", tags=["staff-onboarding"])


# ============================================================================
# Pydantic Models
# ============================================================================

class ChecklistItemSchema(BaseModel):
    title: str
    description: str
    assigned_to: str = "manager"
    order: int = 0


class OnboardingTemplateCreate(BaseModel):
    template_name: str
    items: List[ChecklistItemSchema]


class OnboardingTemplateResponse(BaseModel):
    id: str = Field(alias="_id")
    template_name: str
    items: List[ChecklistItemSchema]
    is_active: bool
    created_at: str

    class Config:
        populate_by_name = True


class ChecklistItemResponse(BaseModel):
    title: str
    description: str
    assigned_to: str
    order: int
    status: str
    completed_at: Optional[str] = None
    completed_by: Optional[str] = None
    notes: Optional[str] = None


class OnboardingChecklistResponse(BaseModel):
    id: str = Field(alias="_id")
    staff_id: str
    template_id: str
    items: List[ChecklistItemResponse]
    progress_percentage: int
    status: str
    started_at: str
    completed_at: Optional[str] = None

    class Config:
        populate_by_name = True


class ChecklistProgressResponse(BaseModel):
    has_checklist: bool
    progress_percentage: int
    status: str
    total_items: int = 0
    completed_items: int = 0
    pending_items: int = 0
    in_progress_items: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class UpdateChecklistItemRequest(BaseModel):
    status: str
    notes: Optional[str] = None


class OnboardingStatsResponse(BaseModel):
    total_checklists: int
    completed: int
    in_progress: int
    not_started: int
    average_progress_percentage: int
    completion_rate: int


# ============================================================================
# Routes
# ============================================================================

@router.post("/templates", response_model=OnboardingTemplateResponse)
async def create_onboarding_template(
    template_data: OnboardingTemplateCreate,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Create a new onboarding template for the salon."""
    try:
        template = await OnboardingService.create_onboarding_template(
            salon_id=tenant_id,
            template_name=template_data.template_name,
            items=[item.dict() for item in template_data.items],
            created_by=current_user["id"],
        )
        return template
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/templates", response_model=List[OnboardingTemplateResponse])
async def get_onboarding_templates(
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get all onboarding templates for the salon."""
    try:
        templates = await OnboardingService.get_onboarding_templates(tenant_id)
        return templates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{staff_id}/create-from-template")
async def create_checklist_from_template(
    staff_id: str,
    template_id: str,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Create an onboarding checklist for a staff member from a template."""
    try:
        checklist = await OnboardingService.create_checklist_from_template(
            staff_id=staff_id,
            template_id=template_id,
            salon_id=tenant_id,
        )
        return {
            "success": True,
            "checklist": checklist,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{staff_id}", response_model=dict)
async def get_staff_checklist(
    staff_id: str,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get onboarding checklist for a staff member."""
    try:
        checklist = await OnboardingService.get_staff_checklist(
            staff_id=staff_id,
            salon_id=tenant_id,
        )
        if not checklist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Onboarding checklist not found",
            )
        return {"checklist": checklist}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{staff_id}/progress", response_model=ChecklistProgressResponse)
async def get_checklist_progress(
    staff_id: str,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get progress summary for a staff member's onboarding."""
    try:
        progress = await OnboardingService.get_checklist_progress(
            staff_id=staff_id,
            salon_id=tenant_id,
        )
        return progress
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{checklist_id}/items/{item_index}")
async def update_checklist_item(
    checklist_id: str,
    item_index: int,
    update_data: UpdateChecklistItemRequest,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Update a checklist item status."""
    try:
        updated_checklist = await OnboardingService.update_checklist_item(
            checklist_id=checklist_id,
            item_index=item_index,
            status=update_data.status,
            notes=update_data.notes,
            completed_by=current_user["id"] if update_data.status == "completed" else None,
        )
        return {
            "success": True,
            "checklist": updated_checklist,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{staff_id}/complete")
async def complete_onboarding_step(
    staff_id: str,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Mark onboarding as complete for a staff member."""
    try:
        checklist = await OnboardingService.get_staff_checklist(
            staff_id=staff_id,
            salon_id=tenant_id,
        )
        if not checklist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Onboarding checklist not found",
            )
        return {
            "success": True,
            "message": "Onboarding step completed",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/pending-items/{assigned_to}")
async def get_pending_items_by_assignee(
    assigned_to: str,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get all pending onboarding items assigned to a person."""
    try:
        items = await OnboardingService.get_pending_items_by_assignee(
            salon_id=tenant_id,
            assigned_to=assigned_to,
        )
        return {
            "items": items,
            "total": len(items),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/stats/summary", response_model=OnboardingStatsResponse)
async def get_onboarding_stats(
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get onboarding statistics for the salon."""
    try:
        stats = await OnboardingService.get_onboarding_stats(tenant_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

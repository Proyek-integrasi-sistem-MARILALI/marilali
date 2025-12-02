from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.activity import controller
from services.activity.schemas import ActivityCreate, ActivityUpdate, ActivityResponse
from core.security import get_current_user
from database.connection import get_db
from database.models import User

router = APIRouter()

# =============================
#   ADD ACTIVITY
# =============================
@router.post("/", response_model=ActivityResponse)
def add_to_itinerary(
    data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.add_destination_to_itinerary(current_user.id, data, db)


# =============================
#   LIST ACTIVITIES
# =============================
@router.get("/{itinerary_id}", response_model=list[ActivityResponse])
def get_activities(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.list_activities(itinerary_id, current_user.id, db)


# =============================
#   UPDATE ACTIVITY
# =============================
@router.put("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    data: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.update_activity(activity_id, current_user.id, data, db)


# =============================
#   DELETE ACTIVITY
# =============================
@router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.delete_activity(activity_id, current_user.id, db)

@router.put("/{activity_id}/complete", response_model=ActivityResponse)
def complete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.mark_completed(activity_id, current_user.id, db)


@router.post("/{activity_id}/duplicate", response_model=ActivityResponse)
def duplicate_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.duplicate_activity(activity_id, current_user.id, db)

@router.post("/manual", response_model=ActivityResponse)
def create_manual_activity(
    data: ActivityCreateManual,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.create_manual_activity(current_user.id, data, db)

@router.put("/reorder")
def reorder_activities(
    data: ActivityReorderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return controller.reorder_activities(current_user.id, data.items, db)


@router.patch("/{activity_id}/uncomplete", response_model=ActivityResponse)
def uncomplete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.mark_uncompleted(activity_id, current_user.id, db)

@router.patch("/{itinerary_id}/day/{day_number}/reset")
def reset_day(
    itinerary_id: int,
    day_number: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.reset_day(itinerary_id, day_number, current_user.id, db)

@router.patch("/{itinerary_id}/reset")
def reset_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.reset_itinerary(itinerary_id, current_user.id, db)

@router.patch("/{itinerary_id}/complete-all")
def complete_all(
    itinerary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return controller.complete_all_activities(itinerary_id, current_user.id, db)

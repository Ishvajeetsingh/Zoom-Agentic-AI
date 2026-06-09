import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.repositories import meetings as meeting_repo
from app.schemas.meetings import MeetingDetailOut, MeetingListItem, MeetingListOut

router = APIRouter()


@router.get("", response_model=MeetingListOut)
def list_meetings(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    order_by: str = Query("created_at", pattern="^(created_at|updated_at|start_time)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
) -> MeetingListOut:
    rows, total = meeting_repo.list_meetings(
        db,
        offset=offset,
        limit=limit,
        order_by=order_by,
        order_desc=(order == "desc"),
    )

    items = [MeetingListItem.model_validate(m) for m in rows]
    return MeetingListOut(items=items, total=total, offset=offset, limit=limit)


@router.get("/{meeting_id}", response_model=MeetingDetailOut)
def get_meeting(
    meeting_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> MeetingDetailOut:
    detail = meeting_repo.get_meeting_detail(db, meeting_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    return MeetingDetailOut.model_validate(detail)


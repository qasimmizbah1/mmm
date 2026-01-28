# routers/logs.py
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from pydantic import UUID4
from models import LogOut, LogListOut
from deps import require_admin
from services.logging import delete_log_service, get_log_service, list_logs_service

router = APIRouter(prefix="/v1/admin/logs", tags=["Admin Logs"])

@router.get("/", response_model=LogListOut, dependencies=[Depends(require_admin)])
async def list_logs(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: Optional[UUID4] = Query(None),
    level: Optional[str] = Query(None, pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL|AUDIT)$"),
    action_like: Optional[str] = Query(None, description="Search in action (ILIKE)"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
):
   return await list_logs_service(request, page, page_size, user_id, level, action_like, date_from, date_to)

@router.get("/{log_id}", response_model=LogOut, dependencies=[Depends(require_admin)])
async def get_log(log_id: UUID, request: Request):
    return await get_log_service(log_id, request)


@router.delete("/{log_id}", status_code=204, dependencies=[Depends(require_admin)])
async def delete_log(log_id: UUID, request: Request):
    return await delete_log_service(log_id, request)

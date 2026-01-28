from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException, BackgroundTasks
import os
from uuid import UUID
from services.kyc_document_service import view_kyc_document_service, delete_kyc_document_service, accept_kyc_document_service, view_kyc_supplier_service
from models import kycActionModel


router = APIRouter(prefix="/v1/admin", tags=["Supplier KYC"])




@router.get("/kyc/view")
async def view_kyc_document(
    request: Request,
    user_id: UUID
):
    return await view_kyc_document_service(request, user_id)


@router.delete("/kyc/delete")
async def view_kyc_document(
    request: Request,
    kyc_id: UUID,
    user_id: UUID
):
    return await delete_kyc_document_service(request, kyc_id, user_id)


@router.patch("/kyc/action")
async def accept_kyc_document(request: Request,model_res: kycActionModel, background_tasks : BackgroundTasks):
    return await accept_kyc_document_service(request, model_res, background_tasks)



@router.get("/kyc/supplier")
async def view_supplier_profiles(request: Request):
    return await view_kyc_supplier_service(request)



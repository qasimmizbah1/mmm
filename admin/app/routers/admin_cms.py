# routers/admin_crm.py

from typing import  List, Optional
from fastapi import APIRouter, Depends, Request, UploadFile, File, Form
from models import PageOut, MenuData, PageOutAll, HomePageContent
from deps import require_admin
from services.admin_cms_service import create_menu_and_update_services, upload_image_service, update_home_page_services, get_home_page_service, create_page_service, list_pages_service, get_page_service, update_page_service, delete_page_service, delete_image_service, view_all_menus_services, view_menu_by_id_services



router = APIRouter(prefix="/v1/admin/cms", tags=["Admin CMS"])

# GET ALL PAGES
@router.get("/", response_model=List[PageOutAll])
async def get_pages(request: Request):
    return await list_pages_service(request)

@router.get("/home", response_model=dict)
async def get_home_page(request: Request):
    return await get_home_page_service(request)
    


@router.put("/pages/home")
async def update_home_page(data: HomePageContent, request: Request):
    return await update_home_page_services(data, request)


@router.post("/upload-image")
async def upload_image( file: UploadFile = File(...)):
    return await upload_image_service(file)


# CREATE PAGE
@router.post("/", response_model=PageOut,dependencies=[Depends(require_admin)])
async def create_page(request: Request,
    slug: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    status: str = Form("draft"),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    thumbnail: Optional[UploadFile] = File(None),
    ):
    
    return await create_page_service(request, {
        "slug": slug,
        "title": title,
        "content": content,
        "status": status,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "thumbnail": thumbnail
    })
    


# GET SINGLE PAGE
@router.get("/{page_id}", response_model=PageOut)
async def get_page(page_id: int, request: Request):
    return await get_page_service(page_id, request)


# UPDATE PAGE
@router.put("/{page_id}", response_model=PageOut , dependencies=[Depends(require_admin)])
async def update_page(page_id: int, request: Request,    
    slug: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    status: str = Form("draft"),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    thumbnail: Optional[UploadFile] = File(None),
    thumbnail_url: Optional[str] = Form(None),
    ):
    data = {
        "slug": slug,
        "title": title,
        "content": content,
        "status": status,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "thumbnail": thumbnail,
        "thumbnail_url": thumbnail_url
    }
    return await update_page_service(page_id, request, data)


# DELETE PAGE
@router.delete("/{page_id}" , dependencies=[Depends(require_admin)])
async def delete_page(page_id: int, request: Request):
    return await delete_page_service(page_id, request)
   
@router.delete("/image/{image_id}" , dependencies=[Depends(require_admin)])
async def delete_image(image_id: str, request: Request):
    return await delete_image_service(image_id, request)


#menu
@router.post("/menu/add",dependencies=[Depends(require_admin)])
async def create_menu_and_update(payload:MenuData, request: Request):
    return await create_menu_and_update_services(payload, request)

   

@router.get("/menu/view",dependencies=[Depends(require_admin)])
async def view_all_menus(request: Request):
    return await view_all_menus_services(request)
    


@router.get("/menu/view/{MenuName}")
async def view_menu_by_id(MenuName: str, request: Request):
    return await view_menu_by_id_services(MenuName, request)
    

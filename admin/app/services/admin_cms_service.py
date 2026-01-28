import os
from fastapi import  HTTPException, Request
from datetime import datetime
import json
from fastapi.responses import JSONResponse
from services.logs_service import write_log


UPLOAD_FOLDER = "./public_files/images/"
# async def view_buyer_service(request: Request):
#     async with request.app.state.pool.acquire() as conn:
#         rows = await conn.fetch("SELECT app_user.id, app_user.email, app_user.role, app_user.is_active,buyer_profile.buyer_name, buyer_profile.company_name, buyer_profile.vat_number FROM app_user JOIN buyer_profile ON app_user.id = buyer_profile.user_id WHERE app_user.role = 'buyer'")
#         return [dict(row) for row in rows]

async def get_home_page_service(request: Request):
    row = await request.app.state.pool.fetchrow(
        "SELECT content FROM pages WHERE slug='home'"
    )

    if not row:
        return {}

    import json
    return json.loads(row["content"])

async def update_home_page_services(data, request):
    content_json = data.model_dump_json()

    query = """
        INSERT INTO pages (slug, title, content, status)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (slug)
        DO UPDATE SET 
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            updated_at = NOW();
    """

    async with request.app.state.pool.acquire() as conn:
        await conn.execute(
            query,
            "home",
            "Home Page",
            content_json,
            "published"
        )

    return {"message": "Home page updated successfully"}

async def upload_image_service(file):
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid image type")

    # Create unique filename
    file_ext = file.filename.split(".")[-1]
    now = datetime.now()
    datetime_str = now.strftime("%Y%m%d_%H%M_") + f"{int(now.microsecond)}"   
    filename = f"{datetime_str}.{file_ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Save file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return JSONResponse({"url": filename})

async def list_pages_service(request: Request):
    query = "SELECT * FROM pages ORDER BY id DESC"
    rows = await request.app.state.pool.fetch(query)
    return [dict(row) for row in rows]

async def create_page_service(request: Request, data):
    now = datetime.now()
    datetime_str = now.strftime("%Y%m%d_%H%M_") + f"{int(now.microsecond)}"  
    thumbnail_url = None
    if data["thumbnail"]:
        file_extension = os.path.splitext(data["thumbnail"].filename)[1]
        filename = f"{datetime_str}{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        with open(file_path, "wb") as f:
            f.write(await data["thumbnail"].read())

        thumbnail_url = f"{filename}"
    query = """
        INSERT INTO pages (
            slug, title, content, thumbnail, status, meta_title, meta_description
        )
        VALUES ($1,$2,$3,$4,$5,$6,$7)
        RETURNING *
    """
    await write_log(
                request=request,
                action="PAGE_CREATED",
                level="INFO",
                user_id='',
                meta={"email": 'admin@admin.com', "role": 'admin'}
            )
    try:
        row = await request.app.state.pool.fetchrow(
            query,
            data["slug"],
            data["title"],
            data["content"],
            thumbnail_url,
            data["status"],
            data["meta_title"],
            data["meta_description"]
            
        )
    
    except Exception as e:
        if "duplicate key" in str(e):
            raise HTTPException(400, detail="Slug already exists")
        

    return dict(row)

async def get_page_service(page_id: int, request: Request):
    query = "SELECT * FROM pages WHERE id = $1"
    row = await request.app.state.pool.fetchrow(query, page_id)
    if not row:
        raise HTTPException(404, detail="Page not found")
    return dict(row)

async def update_page_service(page_id: int, request: Request, data):
    async with request.app.state.pool.acquire() as conn:
        try:

            existing = await conn.fetchrow("SELECT * FROM pages WHERE id = $1", page_id)
            if not existing:
                raise HTTPException(404, detail="Page not found")

            now = datetime.now()
            datetime_str = now.strftime("%Y%m%d_%H%M_") + f"{int(now.microsecond)}"  
            
            thumbnail_url = data["thumbnail_url"]

            if data["thumbnail"]:
                file_extension = os.path.splitext(data["thumbnail"].filename)[1]
                filename = f"{datetime_str}{file_extension}"
                file_path = os.path.join(UPLOAD_FOLDER, filename)

                with open(file_path, "wb") as f:
                    f.write(await data["thumbnail"].read())

                thumbnail_url = f"{filename}"

            query = """
            UPDATE pages SET
                slug = $1,
                title = $2,
                content = $3,
                thumbnail = $4,
                status = $5,
                meta_title = $6,
                meta_description = $7
                WHERE id = $8
                RETURNING *
            """


            row = await conn.fetchrow(query, 
                    data["slug"],
                    data["title"],
                    data["content"],
                    thumbnail_url,
                    data["status"],
                    data["meta_title"],
                    data["meta_description"],
                    page_id
                    )
            if not row:
                raise HTTPException(404, detail="Page not found")

            await write_log(
                request=request,
                action="PAGE_UPDATED",
                level="INFO",
                user_id='',
                meta={"email": 'admin@admin.com', "role": 'admin'}
            )
            
            return dict(row)
        except Exception as e:
            return JSONResponse(
            status_code=500,
            content={"error": "true", "error_msg": str(e)}
            )
            
    

async def delete_page_service(page_id: int, request: Request):

    await write_log(
        request=request,
        action="PAGE_DELETED",
        level="INFO",
        user_id='',
        meta={"email": 'admin@admin.com', "role": 'admin'}
    )
    query = "DELETE FROM pages WHERE id = $1 RETURNING id"
    row = await request.app.state.pool.fetchrow(query, page_id)

    if not row:
        raise HTTPException(404, detail="Page not found")

    return {"status": "success", "message": "Page deleted"}



async def delete_image_service(image_id: str, request: Request):

    file_path = os.path.join(UPLOAD_FOLDER, image_id)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"status": "success", "message": "image deleted"}
    else:
        return {"status": "failed", "message": "image failed"}
    

async def create_menu_and_update_services(payload:any, request: Request):

    try:
        data_str = json.dumps(payload.data)
        async with request.app.state.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, type, data FROM common_data WHERE type = $1
                """,
                'Menu_cms_data'
            )
            if row:
                row = await conn.fetchrow(
                    """
                    UPDATE common_data
                    SET data = COALESCE($1, data), updated_at = NOW()
                    WHERE type = $2
                    RETURNING id, type, data, created_at, updated_at
                    """,
                    data_str,
                    'Menu_cms_data'
                )
            else:
                row = await conn.fetchrow(
                    """
                    INSERT INTO common_data (type, data)
                    VALUES ($1, $2)
                    RETURNING id, type, data, created_at, updated_at
                    """,
                    'Menu_cms_data',
                    data_str
                )

            await write_log(
                    request=request,
                    action="PAGE_CREATED",
                    level="INFO",
                    user_id='',
                    meta={"email": '', "role": 'admin'}
                )
            
            return {"status": "success", "message": "menu updated", "data": dict(row)}
    except Exception as e:
        return {"status_code": 500, "error": "true", "error_msg": str(e)}
    

async def view_all_menus_services(request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT data
            FROM common_data
            WHERE type = $1
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            "Menu_cms_data"
        )

    return json.loads(row["data"]) if row else {
        "status": "Not Found",
        "message": "no menu found",
        "data": {}
    }


async def view_menu_by_id_services(MenuName: str, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
        """
        SELECT data
        FROM common_data
        WHERE type = $1
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        "Menu_cms_data"
    )

    if not row or not row["data"]:
        raise HTTPException(status_code=404, detail="Menu data not found")

 
    menus = json.loads(row["data"])
    main_menu = next(
        (menu for menu in menus if menu.get("name") == MenuName),
        None
    )

    if not main_menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return main_menu


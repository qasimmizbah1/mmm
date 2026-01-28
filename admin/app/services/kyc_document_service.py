import uuid
from datetime import datetime
from fastapi import HTTPException, Request, BackgroundTasks
import os
from datetime import date, datetime
from utils.email import send_email
from services.logs_service import write_log

UPLOAD_DIR = "./public_files/images/"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def view_kyc_document_service(request, user_id):

    try:

        async with request.app.state.pool.acquire() as conn:
            supplier_exists = await conn.fetchval(
                "SELECT id FROM app_user WHERE id = $1",
                user_id
            )
        if not supplier_exists:
            raise HTTPException(status_code=404, detail="User not found")
        


        # Fetch KYC document entry
        async with request.app.state.pool.acquire() as conn:
            
            kyc_record = await conn.fetch(
                    """
                    SELECT * 
                    FROM kyc_document 
                    WHERE user_id = $1
                    """,
                    user_id
                    )
            
            if not kyc_record:
                raise HTTPException(status_code=404, detail="KYC document not found")

            #return [dict(r) for r in kyc_record]

        result = [
                {
                    "id": r["id"],
                    "status": r["status"],
                    "attachment_name": r["attachment_name"],
                    "created_at": r["created_at"].date().isoformat()
                    # or: r["created_at"].strftime("%Y-%m-%d")
                }
                for r in kyc_record
            ]

        return result
        
                
    except Exception as e:
        # Log the error (optional: replace print with logger)
        print("ERROR in view_kyc_document:", e)

        # Return custom readable error
        # raise HTTPException(
        #     #status_code=200,
        #     "success":false,
        #     detail=f"KYC document not found: {str(e)}"
        # )
        return {
        "success": False,
        "message": "User not found",
        "error": str(e)
        }
    

async def delete_kyc_document_service(request, kyc_id, user_id):
    try:

        async with request.app.state.pool.acquire() as conn:
            kyc_exists = await conn.fetchval(
                "SELECT id FROM kyc_document WHERE id = $1 and user_id = $2",
                kyc_id, user_id
            )
        if not kyc_exists:
            raise HTTPException(status_code=404, detail="KYC document not found")
        


        # Delete KYC document entry
        async with request.app.state.pool.acquire() as conn:
            await conn.execute(
                    """
                    DELETE FROM kyc_document 
                    WHERE id = $1 and user_id = $2
                    """,
                    kyc_id, user_id
                    )
            
            await write_log(
                request=request,
                action="KYC_DELETED",
                level="INFO",
                user_id='',
                meta={"email": '', "role": 'admin'}
            )

            return {
                    "message": "KYC document deleted successfully"
                }
        
                
    except Exception as e:
        # Log the error (optional: replace print with logger)
        print("🔥 ERROR in delete_kyc_document:", e)

        # Return custom readable error
        raise HTTPException(
            status_code=500,
            detail=f"Something went wrong: {str(e)}"
        )
    
# async def accept_kyc_document_service(request,model_res, background_tasks):
#     try:
        
#         async with request.app.state.pool.acquire() as conn:
#             user_record = await conn.fetchrow(
#             "SELECT id, email, user_name FROM app_user WHERE id = $1",
#             model_res.user_id
#         )

#         if not user_record:
#             raise HTTPException(status_code=404, detail="User not found")
        
#         async with request.app.state.pool.acquire() as conn:
#             kyc_exists = await conn.fetchrow(
#                 "SELECT id,status FROM kyc_document WHERE id = $1 and user_id = $2",
#                 model_res.kyc_id, model_res.user_id
#             )
#         if not kyc_exists:
#             raise HTTPException(status_code=404, detail="KYC document not found")
        
#         current_status = kyc_exists["status"]
#         new_status = model_res.type

#         if current_status == new_status:
#             return {"message": f"KYC is already {current_status}"}
        

#         async with request.app.state.pool.acquire() as conn:
#             await conn.execute(
#                 """
#                 UPDATE kyc_document
#                 SET status = $1
#                 WHERE id = $2 AND user_id = $3
#                 """,
#                 new_status, model_res.kyc_id, model_res.user_id
#                 )
#         await write_log(
#                 request=request,
#                 action="KYC_ACTION",
#                 level="INFO",
#                 user_id='',
#                 meta={"email": '', "role": 'admin'}
#             )
            
#         body_content = f"""
#         <p>Hello <strong>{user_record["user_name"]}</strong>,</p>
#         <p>You KYC document is {model_res.type}</p>
#         <p>Check you dashborad KYC section for more update.</p>

#         """ 
#         background_tasks.add_task(send_email, user_record["email"],"KYC Status" , body_content)
        

#         return {"message": "KYC document is "+ model_res.type }
        
                
#     except Exception as e:
#         # Log the error (optional: replace print with logger)
#         print("🔥 ERROR in accept_kyc_document:", e)

#         # Return custom readable error
#         raise HTTPException(
#             status_code=500,
#             detail=f"Something went wrong: {str(e)}"
#         )
    
async def accept_kyc_document_service(request, model_res, background_tasks):

    async with request.app.state.pool.acquire() as conn:
        async with conn.transaction():

            # 1️⃣ Validate user
            user = await conn.fetchrow(
                "SELECT id, email, user_name FROM app_user WHERE id = $1",
                model_res.user_id
            )
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # 2️⃣ Update app_user status
            await conn.execute(
                """
                UPDATE supplier_profile
                SET kyc_status = $1
                WHERE user_id = $2
                """,
                model_res.type,
                model_res.user_id
            )

            # if not model_res.attachment:
            #     raise HTTPException(
            #         status_code=400,
            #         detail="At least one attachment is required"
            #     )

            # 3️⃣ Update each KYC document individually
            for att in model_res.attachment:

                kyc_exists = await conn.fetchrow(
                    """
                    SELECT id FROM kyc_document
                    WHERE id = $1 AND user_id = $2
                    """,
                    att.id,
                    model_res.user_id
                )

                if not kyc_exists:
                    raise HTTPException(
                        status_code=404,
                        detail=f"KYC document {att.id} not found"
                    )

                await conn.execute(
                    """
                    UPDATE kyc_document
                    SET status = $1
                    WHERE id = $2 AND user_id = $3
                    """,
                    att.status,
                    att.id,
                    model_res.user_id
                )

    # 4️⃣ Log
    await write_log(
        request=request,
        action="KYC_ACTION",
        level="INFO",
        user_id=str(model_res.user_id),
        meta={"email": user["email"], "role": "admin"}
    )

    # 5️⃣ Email
    body_content = f"""
    <p>Hello <strong>{user["user_name"]}</strong>,</p>
    <p>Your KYC status has been updated.</p>
    <p>Please check your dashboard.</p>
    """

    background_tasks.add_task(
        send_email,
        user["email"],
        "KYC Status Update",
        body_content
    )

    return {
        "message": "KYC updated successfully",
        "user_id": str(model_res.user_id),
        "user_status": model_res.type,
        "attachments_updated": len(model_res.attachment)
    }
    
async def view_kyc_supplier_service(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT app_user.id, app_user.email, app_user.role, app_user.is_active,app_user.user_name, supplier_profile.company_name, supplier_profile.kyc_status FROM app_user JOIN supplier_profile ON app_user.id = supplier_profile.user_id WHERE app_user.role = 'supplier' and supplier_profile.kyc_status != 'approved' order by app_user.created_at DESC")
        return [dict(row) for row in rows]  
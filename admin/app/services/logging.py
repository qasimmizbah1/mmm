# services/logging.py
from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import Request, HTTPException
import json

async def write_log(
    request: Request,
    *,
    action: str,
    level: str = "INFO",
    user_id: Optional[UUID] = None,
    path: Optional[str] = None,
    ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
):
    

    if path is None and request:
        path = request.url.path
    if ip is None and request:
        ip = request.client.host if request.client else None
    if user_agent is None and request:
        user_agent = request.headers.get("user-agent")

    meta_json = json.dumps(meta) if meta else "{}"

    async with request.app.state.pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO system_log (user_id, level, action, path, ip, user_agent, meta)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            str(user_id) if user_id else None,
            level,
            action,
            path,
            ip,
            user_agent,
            meta_json,
        )


async def delete_log_service(log_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        result = await conn.execute("DELETE FROM system_log WHERE id = $1", str(log_id))
        # result like "DELETE 1"
        if result.endswith("0"):
            raise HTTPException(status_code=404, detail="Log not found")
    return


async def get_log_service(log_id: UUID, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id,
                   user_id,
                   level,
                   action,
                   path,
                   ip::text AS ip,
                   user_agent,
                   meta::json AS meta,
                   created_at
            FROM system_log
            WHERE id = $1
            """,
            str(log_id),
        )

        if not row:
            raise HTTPException(status_code=404, detail="Log not found")

        log = dict(row)

        # Ensure meta is a dict (fix ResponseValidationError)
        if isinstance(log.get("meta"), str):
            import json
            log["meta"] = json.loads(log["meta"])

        return log
    

async def list_logs_service(request, page, page_size, user_id, level, action_like, date_from, date_to):
    where = []
    params = []

    if user_id:
        where.append(f"user_id = ${len(params)+1}")
        params.append(str(user_id))
    if level:
        where.append(f"level = ${len(params)+1}")
        params.append(level)
    if action_like:
        where.append(f"action ILIKE ${len(params)+1}")
        params.append(f"%{action_like}%")
    if date_from:
        where.append(f"created_at >= ${len(params)+1}")
        params.append(date_from)
    if date_to:
        where.append(f"created_at <= ${len(params)+1}")
        params.append(date_to)

    where_sql = "WHERE " + " AND ".join(where) if where else ""

    # Count total rows for pagination
    count_sql = f"SELECT COUNT(*) FROM system_log {where_sql}"
    limit = page_size
    offset = (page - 1) * page_size

    async with request.app.state.pool.acquire() as conn:
        total = await conn.fetchval(count_sql, *params)

        rows = await conn.fetch(
            f"""
            SELECT id,
                   user_id,
                   level,
                   action,
                   path,
                   ip::text AS ip,
                   user_agent,
                   meta::json AS meta,
                   created_at
            FROM system_log
            {where_sql}
            ORDER BY created_at DESC
            LIMIT ${len(params)+1} OFFSET ${len(params)+2}
            """,
            *params, limit, offset
        )

    # Ensure meta is always a dict
    import json
    items = []
    for r in rows:
        log = dict(r)
        if isinstance(log.get("meta"), str):
            log["meta"] = json.loads(log["meta"])
        items.append(log)

    pages = (total + page_size - 1) // page_size if total else 0

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages
    }


from collections import deque
import threading
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from database import lifespan
from routers import auth
from fastapi.middleware.cors import CORSMiddleware
from services.logs_service import write_log
from fastapi.staticfiles import StaticFiles

app = FastAPI(lifespan=lifespan)

#app.mount("/image", StaticFiles(directory="/public_files/images"), name="images")


origins = [
    "https://auto-parts-front.vercel.app",
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # ONLY these origins allowed
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],   # allow all domains
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# -------------------
# Middleware using imported rate_limit
# -------------------
lock = threading.Lock()
REQUEST_LOG = {}  # {ip: deque[timestamps]}
BLOCKED_IPS = {}  # {ip: unblock_time}

LIMIT = 1000         # max requests
WINDOW = 60        # seconds
BLOCK_DURATION = 120  # 1 hour in seconds

@app.middleware("http")
async def rate_limiter_middleware(request: Request, call_next):
    ip = request.client.host
    now = time.time()

    with lock:
        # Check if IP is blocked
        if ip in BLOCKED_IPS:
            if now < BLOCKED_IPS[ip]:
                # Still blocked
                return JSONResponse(
                    status_code=429,
                    content={"error": f"IP blocked. Try again later."}
                )
            else:
                # Unblock IP after time expires
                del BLOCKED_IPS[ip]

        # Initialize log
        if ip not in REQUEST_LOG:
            REQUEST_LOG[ip] = deque()

        # Remove old timestamps
        timestamps = REQUEST_LOG[ip]
        while timestamps and timestamps[0] <= now - WINDOW:
            timestamps.popleft()

        # Check request limit
        if len(timestamps) >= LIMIT:
            # Block IP for 1 hour
            BLOCKED_IPS[ip] = now + BLOCK_DURATION
            REQUEST_LOG[ip].clear()
            return JSONResponse(
                status_code=429,
                content={"error": f"Too many requests. IP blocked for 1 hour."}
            )

        # Record new request
        timestamps.append(now)

    response = await call_next(request)
    return response


@app.middleware("http")
async def admin_action_logger(request: Request, call_next):
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        user_id = getattr(request.state, "user_id", None)  # set during auth
        await write_log(
            request=request,
            action="REQUEST",
            level="INFO",
            user_id=user_id,
            meta={
                "method": request.method,
                "status": response.status_code if response else None,
            }
        )

# include auth routes
app.include_router(auth.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Auto Parts auth API "} 
    

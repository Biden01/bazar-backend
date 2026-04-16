import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.limiter import limiter
from app.routers import auth, users, products, orders, inventory, debts, chat, notifications, b2b, documents, upload, calculator, ai

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bazar")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Bazar Digital API starting up (DEV_MODE=%s)", settings.DEV_MODE)
    yield
    logger.info("Bazar Digital API shutting down")


app = FastAPI(
    title="Bazar Digital Taraz API",
    version="1.0.0",
    docs_url="/docs" if settings.DEV_MODE else None,
    redoc_url="/redoc" if settings.DEV_MODE else None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    duration_ms = int((time.monotonic() - start) * 1000)
    logger.info("%s %s %s %dms", request.method, request.url.path, response.status_code, duration_ms)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/v1/users", tags=["users"])
app.include_router(products.router, prefix="/v1/products", tags=["products"])
app.include_router(orders.router, prefix="/v1/orders", tags=["orders"])
app.include_router(inventory.router, prefix="/v1/inventory", tags=["inventory"])
app.include_router(debts.router, prefix="/v1/debts", tags=["debts"])
app.include_router(chat.router, prefix="/v1/chats", tags=["chat"])
app.include_router(notifications.router, prefix="/v1/notifications", tags=["notifications"])
app.include_router(b2b.router, prefix="/v1/b2b", tags=["b2b"])
app.include_router(documents.router, prefix="/v1/documents", tags=["documents"])
app.include_router(upload.router, prefix="/v1/upload", tags=["upload"])
app.include_router(calculator.router, prefix="/v1/calculator", tags=["calculator"])
app.include_router(ai.router, prefix="/v1/ai", tags=["ai"])


@app.get("/health")
async def health():
    return {"status": "ok"}

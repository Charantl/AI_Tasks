from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import RequestValidationError as FastAPIRequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api import auth
from app.api import user
from app.api import subscription
from app.api import artist
from app.api import album
from app.api import song
from app.api import search
from app.api import recommendations
from app.api import liked_song
from app.api import play_history
from app.api import comment
from app.api import share
from app.api import analytics
from app.api import ws
from app.core.logging_config import get_logger
import time
import traceback
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
logger = get_logger("main")

Instrumentator().instrument(app).expose(app)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

@app.get("/health", tags=["Monitoring"], summary="Health check endpoint")
def health_check():
    """Liveness/readiness probe for monitoring."""
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(subscription.router)
app.include_router(artist.router)
app.include_router(album.router)
app.include_router(song.router)
app.include_router(search.router)
app.include_router(recommendations.router)
app.include_router(liked_song.router)
app.include_router(play_history.router)
app.include_router(comment.router)
app.include_router(share.router)
app.include_router(analytics.router)
app.include_router(ws.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Spotify-like Music Streaming Platform API"} 
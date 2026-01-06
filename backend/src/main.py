import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from src.config import settings
from src.database import init_db

# Import routers (each once, no duplicates)
from src.auth.router import router as auth_router
from src.user.router import router as user_router
from src.review.router import router as review_router
from src.itinerary.router import router as itinerary_router
from src.favorite.router import router as favorite_router
from src.activity.router import router as activity_router
from src.budget.router import router as budget_router
from src.destination.router import router as destination_router
from src.notification.router import router as notification_router
from src.ai_recommendation.router import router as ai_recommendation_router
from src.weather.router import router as weather_router
from src.search.router import router as search_router
from src.transportation.router import router as transportation_router
from src.accommodation.router import router as accommodation_router

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log slow requests and track performance."""
    
    SLOW_REQUEST_THRESHOLD = 2.0  # seconds
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Store request info
        method = request.method
        path = request.url.path
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            # Log uncaught exceptions
            duration = time.time() - start_time
            logger.error(
                f"[ERROR] {method} {path} - Exception: {str(exc)} - Duration: {duration:.2f}s"
            )
            raise
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log slow requests
        if duration >= self.SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"[SLOW REQUEST] {method} {path} - Status: {status_code} - Duration: {duration:.2f}s"
            )
        
        # Add performance header
        response.headers["X-Process-Time"] = f"{duration:.2f}s"
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    
    # Validate secrets (fail fast in staging/production if missing)
    settings.validate_secrets()
    print("Secrets validated")
    
    await init_db()
    print("Database initialized")
    
    yield
    
    # Shutdown
    print("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Travel Planner API - Plan your trips with ease",
    lifespan=lifespan,
    docs_url="/docs",  # Force enable for testing
    redoc_url="/redoc",  # Force enable for testing
)


# Debugging information
print("DEBUG:", settings.DEBUG)
print("ENVIRONMENT:", settings.ENVIRONMENT)
print("DOCS available at: http://localhost:8000/docs")
print("REDOC available at: http://localhost:8000/redoc")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "code": exc.status_code,
            "details": None,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "code": 422,
            "details": errors,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the exception with full context
    logger.error(
        f"[UNHANDLED EXCEPTION] {request.method} {request.url.path} - "
        f"Type: {type(exc).__name__} - Message: {str(exc)}",
        exc_info=True  # Include stack trace
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "code": 500,
            "details": str(exc) if settings.DEBUG else None,
        },
    )

# Add request logging middleware (before CORS so it captures everything)
app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(destination_router, prefix="/destinations", tags=["Destinations"])
app.include_router(review_router, prefix="/reviews", tags=["Reviews"])
app.include_router(itinerary_router, prefix="/itinerary", tags=["Itinerary"])
app.include_router(favorite_router, prefix="/favorites", tags=["Favorites"])
app.include_router(activity_router, prefix="/activities", tags=["Activities"])
app.include_router(budget_router, prefix="/budgets", tags=["Budget & Expenses"])
app.include_router(notification_router, prefix="/notifications", tags=["Notifications"])
app.include_router(ai_recommendation_router, prefix="/ai", tags=["AI Recommendations"])
app.include_router(weather_router, prefix="/weather", tags=["Weather"])
app.include_router(search_router, prefix="/search", tags=["Search & Analytics"])
app.include_router(transportation_router, prefix="/transportation", tags=["Transportation"])
app.include_router(accommodation_router, prefix="/accommodation", tags=["Accommodation"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Travel Planner API",
        "version": settings.APP_VERSION,
        "status": "healthy",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }

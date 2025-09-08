from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
from contextlib import asynccontextmanager

# Import routes
from routes import (
    auth_router,
    user_router,
    coach_router,
    branch_router,
    course_router,
    category_router,
    duration_router,
    location_router,
    branch_public_router,
    enrollment_router,
    payment_router,
    request_router,
    event_router
)
from routes.superadmin_routes import router as superadmin_router

# Import database utility
from utils.database import db

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    app.mongodb_client = AsyncIOMotorClient(mongo_url)
    db_name = os.getenv("DB_NAME", "student_management_db")
    app.mongodb = app.mongodb_client.get_database(db_name)
    
    # Initialize the database connection in utils
    from utils.database import init_db
    init_db(app.mongodb)
    
    yield
    
    # Shutdown
    app.mongodb_client.close()

# Create FastAPI app
app = FastAPI(
    title="Learning Management System API",
    description="A comprehensive LMS API for managing students, courses, and educational content",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(superadmin_router, prefix="/superadmin", tags=["Super Admin"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(coach_router, prefix="/coaches", tags=["Coaches"])
app.include_router(branch_router, prefix="/branches", tags=["Branches"])
app.include_router(course_router, prefix="/courses", tags=["Courses"])
app.include_router(category_router, prefix="/categories", tags=["Categories"])
app.include_router(duration_router, prefix="/durations", tags=["Durations"])
app.include_router(location_router, prefix="/locations", tags=["Locations"])
app.include_router(branch_public_router, prefix="/branches", tags=["Branches Public"])
app.include_router(enrollment_router, prefix="/enrollments", tags=["Enrollments"])
app.include_router(payment_router, prefix="/payments", tags=["Payments"])
app.include_router(request_router, prefix="/requests", tags=["Requests"])
app.include_router(event_router, prefix="/events", tags=["Events"])

@app.get("/")
async def root():
    return {"message": "Learning Management System API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)

# Routes package for Student Management System

from .auth_routes import router as auth_router
from .user_routes import router as user_router
from .coach_routes import router as coach_router
from .branch_routes import router as branch_router
from .course_routes import router as course_router
from .enrollment_routes import router as enrollment_router
from .payment_routes import router as payment_router
from .request_routes import router as request_router
from .event_routes import router as event_router

__all__ = [
    'auth_router',
    'user_router',
    'coach_router',
    'branch_router',
    'course_router',
    'enrollment_router',
    'payment_router',
    'request_router',
    'event_router'
]

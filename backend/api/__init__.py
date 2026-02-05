"""
Initialize API package
"""
# from .ingestion import router as ingestion_router  # Temporarily disabled
from .students import router as students_router
from .skills import router as skills_router
from .roles import router as roles_router
from .auth import router as auth_router
from .protected_examples import router as protected_router

__all__ = [
    # "ingestion_router",  # Temporarily disabled
    "students_router",
    "skills_router",
    "roles_router",
    "auth_router",
    "protected_router"
]

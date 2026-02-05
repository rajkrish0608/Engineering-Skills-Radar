"""
Initialize API package
"""
from .ingestion import router as ingestion_router
from .students import router as students_router
from .skills import router as skills_router
from .roles import router as roles_router

__all__ = [
    "ingestion_router",
    "students_router",
    "skills_router",
    "roles_router"
]

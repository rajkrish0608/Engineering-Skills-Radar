"""
Engineering Skills Radar - Main FastAPI Application
Entry point for the backend API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from api.ingestion import router as ingestion_router
from api.students import router as students_router
from api.skills import router as skills_router
from api.roles import router as roles_router

# Create FastAPI app
app = FastAPI(
    title="Engineering Skills Radar API",
    description="Academic to Industry Skill Intelligence Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingestion_router)
app.include_router(students_router)
app.include_router(skills_router)
app.include_router(roles_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return JSONResponse(content={
        'status': 'healthy',
        'service': 'Engineering Skills Radar API',
        'version': '1.0.0',
        'environment': os.getenv('ENVIRONMENT', 'development')
    })

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return JSONResponse(content={
        'message': 'Engineering Skills Radar API',
        'version': '1.0.0',
        'docs': '/api/docs',
        'health': '/health'
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv('DEBUG', 'True') == 'True'
    )

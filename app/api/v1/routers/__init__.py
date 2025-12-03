"""
Router principal de la API v1
"""
from fastapi import APIRouter
from app.api.v1.routers import messages, prompts, conversations, analytics

api_router = APIRouter()

# Incluir routers (sin webhooks, van directo en main.py)
api_router.include_router(
    messages.router, prefix="/messages", tags=["Messages"])
api_router.include_router(
    prompts.router, prefix="/prompts", tags=["Prompts"])
api_router.include_router(
    conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(
    analytics.router, prefix="/analytics", tags=["Analytics"])

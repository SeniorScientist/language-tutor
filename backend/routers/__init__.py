"""API Routers."""

from .chat import router as chat_router
from .correction import router as correction_router
from .exercises import router as exercises_router
from .training import router as training_router

__all__ = ["chat_router", "correction_router", "exercises_router", "training_router"]

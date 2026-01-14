"""Chat API endpoints."""

import logging
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from models import ChatRequest, ChatResponse
from services import TutorService, get_tutor_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    tutor: TutorService = Depends(get_tutor_service),
):
    """Send a message and get a response from the tutor.

    This is a non-streaming endpoint that returns the full response at once.
    """
    try:
        response, context = await tutor.chat(
            message=request.message,
            history=request.history,
            target_language=request.target_language,
            learner_level=request.learner_level,
        )

        return ChatResponse(
            response=response,
            context_used=context if context else None,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    tutor: TutorService = Depends(get_tutor_service),
):
    """Send a message and get a streaming response from the tutor.

    Uses Server-Sent Events (SSE) for real-time streaming.
    """

    async def event_generator() -> AsyncIterator[dict]:
        try:
            async for chunk in tutor.chat_stream(
                message=request.message,
                history=request.history,
                target_language=request.target_language,
                learner_level=request.learner_level,
            ):
                yield {
                    "event": "message",
                    "data": chunk,
                }

            # Send completion event
            yield {
                "event": "done",
                "data": "[DONE]",
            }

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield {
                "event": "error",
                "data": str(e),
            }

    return EventSourceResponse(event_generator())


@router.post("/explain")
async def explain_grammar(
    topic: str,
    target_language: str = "Spanish",
    learner_level: str = "beginner",
    tutor: TutorService = Depends(get_tutor_service),
):
    """Get an explanation of a grammar topic."""
    from models import LearnerLevel

    try:
        level = LearnerLevel(learner_level)
        explanation = await tutor.explain_grammar(
            topic=topic,
            target_language=target_language,
            learner_level=level,
        )

        return {"explanation": explanation}

    except Exception as e:
        logger.error(f"Explain error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

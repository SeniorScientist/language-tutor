"""Grammar correction API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException

from models import CorrectionRequest, CorrectionResponse
from services import TutorService, get_tutor_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/correct", tags=["correction"])


@router.post("/", response_model=CorrectionResponse)
async def correct_text(
    request: CorrectionRequest,
    tutor: TutorService = Depends(get_tutor_service),
):
    """Correct grammar and spelling errors in text.

    Returns the corrected text along with a list of errors found
    and explanations for each correction.
    """
    try:
        if not request.text.strip():
            return CorrectionResponse(
                original_text=request.text,
                corrected_text=request.text,
                errors=[],
                has_errors=False,
            )

        response = await tutor.correct_text(
            text=request.text,
            target_language=request.target_language,
        )

        return response

    except Exception as e:
        logger.error(f"Correction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

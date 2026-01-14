"""Exercise generation and checking API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from models import (
    ExerciseRequest,
    Exercise,
    ExerciseCheckRequest,
    ExerciseCheckResponse,
    ExerciseType,
    LearnerLevel,
)
from services import TutorService, get_tutor_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/exercises", tags=["exercises"])

# Available exercise topics
EXERCISE_TOPICS = {
    "English": [
        "Common Idioms and Expressions",
        "Phrasal Verbs",
        "Confusing Word Pairs (affect/effect, their/there)",
        "Irregular Verbs",
        "Tenses and Verb Forms",
        "Prepositions",
        "Articles (a, an, the)",
        "Conditionals (if clauses)",
        "Passive Voice",
        "Reported Speech",
        "Collocations",
        "Academic Vocabulary",
    ],
    "Chinese": [
        "Basic Greetings (你好, 谢谢)",
        "Numbers and Counting",
        "Measure Words (个, 只, 本)",
        "Basic Sentence Structure (SVO)",
        "Question Words (什么, 哪里, 为什么)",
        "Time Expressions",
        "Common Verbs (是, 有, 去, 来)",
        "Adjectives and Descriptions",
        "Family Members",
        "Food and Ordering",
        "Directions and Locations",
        "HSK Vocabulary Levels",
    ],
    "Russian": [
        "Cyrillic Alphabet Basics",
        "Basic Greetings (Привет, Спасибо)",
        "Noun Gender (masculine/feminine/neuter)",
        "Case System Introduction",
        "Nominative and Accusative Cases",
        "Common Verbs (быть, иметь, идти)",
        "Verb Conjugation Patterns",
        "Numbers and Counting",
        "Question Formation",
        "Adjective Agreement",
        "Time and Date Expressions",
        "Verb Aspects (perfective/imperfective)",
    ],
    "Japanese": [
        "Hiragana Reading Practice",
        "Katakana Reading Practice",
        "Basic Greetings (こんにちは, ありがとう)",
        "Sentence Particles (は, が, を, に)",
        "Verb Forms (masu form, te form)",
        "Adjective Types (i-adjectives, na-adjectives)",
        "Counting and Numbers",
        "Time Expressions",
        "Common Kanji (JLPT N5)",
        "Keigo (Polite Language) Basics",
        "Question Words (何, どこ, いつ)",
        "Giving and Receiving Verbs",
    ],
}


@router.get("/topics")
async def list_topics(
    target_language: str = Query(default="English", description="Target language"),
):
    """List available exercise topics for a language."""
    topics = EXERCISE_TOPICS.get(target_language, EXERCISE_TOPICS.get("English", []))
    return {
        "language": target_language,
        "topics": topics,
    }


@router.post("/generate", response_model=list[Exercise])
async def generate_exercises(
    request: ExerciseRequest,
    tutor: TutorService = Depends(get_tutor_service),
):
    """Generate practice exercises for a topic.

    Supports multiple choice, fill-in-the-blank, and translation exercises.
    """
    try:
        exercises = await tutor.generate_exercises(
            topic=request.topic,
            target_language=request.target_language,
            exercise_type=request.exercise_type,
            learner_level=request.learner_level,
            count=request.count,
        )

        if not exercises:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate exercises. Please try again.",
            )

        return exercises

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exercise generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check", response_model=ExerciseCheckResponse)
async def check_answer(
    request: ExerciseCheckRequest,
    target_language: str = Query(default="English"),
    tutor: TutorService = Depends(get_tutor_service),
):
    """Check if an exercise answer is correct.

    Returns whether the answer is correct and provides feedback.
    """
    try:
        is_correct, feedback = await tutor.check_answer(
            user_answer=request.user_answer,
            correct_answer=request.correct_answer,
            target_language=target_language,
        )

        return ExerciseCheckResponse(
            is_correct=is_correct,
            correct_answer=request.correct_answer,
            explanation="",  # Could be fetched from stored exercise
            feedback=feedback,
        )

    except Exception as e:
        logger.error(f"Answer check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def list_exercise_types():
    """List available exercise types."""
    return {
        "types": [
            {"value": t.value, "label": t.value.replace("_", " ").title()}
            for t in ExerciseType
        ]
    }


@router.get("/levels")
async def list_learner_levels():
    """List available learner levels."""
    return {
        "levels": [{"value": l.value, "label": l.value.title()} for l in LearnerLevel]
    }

"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class LearnerLevel(str, Enum):
    """Learner proficiency level."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ExerciseType(str, Enum):
    """Type of exercise."""

    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    TRANSLATION = "translation"


# Chat Models
class ChatMessage(BaseModel):
    """A single chat message."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request payload."""

    message: str = Field(..., description="User's message")
    history: list[ChatMessage] = Field(
        default_factory=list, description="Conversation history"
    )
    target_language: str = Field(
        default="English", description="Language being learned"
    )
    learner_level: LearnerLevel = Field(
        default=LearnerLevel.BEGINNER, description="Learner's level"
    )


class ChatResponse(BaseModel):
    """Chat response payload."""

    response: str = Field(..., description="Assistant's response")
    context_used: Optional[list[str]] = Field(
        default=None, description="RAG context if used"
    )


# Grammar Correction Models
class CorrectionError(BaseModel):
    """A single correction error."""

    original: str = Field(..., description="Original text with error")
    corrected: str = Field(..., description="Corrected text")
    error_type: str = Field(
        ..., description="Type of error: grammar/spelling/punctuation"
    )
    explanation: str = Field(..., description="Explanation of the error")
    position: Optional[int] = Field(default=None, description="Position in text")


class CorrectionRequest(BaseModel):
    """Correction request payload."""

    text: str = Field(..., description="Text to correct")
    target_language: str = Field(default="English", description="Language of the text")


class CorrectionResponse(BaseModel):
    """Correction response payload."""

    original_text: str = Field(..., description="Original input text")
    corrected_text: str = Field(..., description="Fully corrected text")
    errors: list[CorrectionError] = Field(
        default_factory=list, description="List of errors found"
    )
    has_errors: bool = Field(..., description="Whether any errors were found")


# Exercise Models
class ExerciseRequest(BaseModel):
    """Exercise generation request."""

    topic: str = Field(..., description="Topic for the exercise")
    target_language: str = Field(default="English", description="Target language")
    exercise_type: ExerciseType = Field(default=ExerciseType.MULTIPLE_CHOICE)
    learner_level: LearnerLevel = Field(default=LearnerLevel.BEGINNER)
    count: int = Field(default=5, ge=1, le=10, description="Number of questions")


class Exercise(BaseModel):
    """A single exercise question."""

    id: str = Field(..., description="Unique exercise ID")
    type: ExerciseType = Field(..., description="Exercise type")
    question: str = Field(..., description="The question or prompt")
    options: Optional[list[str]] = Field(
        default=None, description="Options for multiple choice"
    )
    correct_answer: str = Field(..., description="The correct answer")
    hint: Optional[str] = Field(default=None, description="Optional hint")
    explanation: str = Field(..., description="Explanation of the answer")


class ExerciseCheckRequest(BaseModel):
    """Request to check an exercise answer."""

    exercise_id: str = Field(..., description="Exercise ID")
    user_answer: str = Field(..., description="User's answer")
    correct_answer: str = Field(..., description="Correct answer for verification")


class ExerciseCheckResponse(BaseModel):
    """Response for exercise check."""

    is_correct: bool = Field(..., description="Whether the answer is correct")
    correct_answer: str = Field(..., description="The correct answer")
    explanation: str = Field(..., description="Explanation")
    feedback: str = Field(..., description="Personalized feedback")


# Health Check
class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    llm_provider: str = Field(..., description="Active LLM provider")
    llm_status: str = Field(..., description="LLM connection status")
    rag_status: str = Field(..., description="RAG service status")

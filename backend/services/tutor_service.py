"""Tutor service with core tutoring logic."""

import json
import logging
import uuid
from typing import AsyncIterator, Optional

from providers import BaseLLMProvider, get_llm_provider
from services.rag_service import RAGService, get_rag_service
from models import (
    ChatMessage,
    LearnerLevel,
    ExerciseType,
    CorrectionResponse,
    CorrectionError,
    Exercise,
)

logger = logging.getLogger(__name__)


class TutorService:
    """Language tutoring service.

    Handles chat, grammar correction, and exercise generation.
    """

    # System prompts for different modes
    TUTOR_SYSTEM_PROMPT = """You are a friendly and encouraging language tutor. 
Your goal is to help the learner improve their {language} skills at the {level} level.

Guidelines:
- Be patient and supportive
- Provide clear explanations
- Use examples from everyday situations
- Correct mistakes gently and explain why
- Encourage the learner to practice
- Adapt your language complexity to the learner's level

{language_specific_instructions}

{context}

Respond naturally and conversationally. If the learner makes mistakes, correct them kindly."""

    # English-specific instructions (E-E style)
    ENGLISH_INSTRUCTIONS = """For English learners:
- Explain complex English concepts using simple, easy-to-understand English
- Break down difficult vocabulary, idioms, and grammar into simple terms
- Provide simple synonyms or definitions for advanced words
- Use the format: "Complex phrase" → Simple explanation
- Focus on common mistakes, phrasal verbs, idioms, and confusing word pairs
- Give practical examples from daily life"""

    # Foreign language instructions
    FOREIGN_LANG_INSTRUCTIONS = """For {language} learners:
- Mix the target language with explanations in English for beginners
- Use more target language as the learner advances
- Include translations and pronunciation tips when helpful"""

    CORRECTION_SYSTEM_PROMPT = """You are an expert {language} language proofreader and grammar checker.
Analyze the given text and identify all errors including:
- Grammar errors
- Spelling mistakes  
- Punctuation errors
- Word choice issues
- Style improvements

You MUST respond with valid JSON in this exact format:
{{
    "corrected_text": "the fully corrected version of the text",
    "errors": [
        {{
            "original": "the incorrect word or phrase",
            "corrected": "the corrected version",
            "error_type": "grammar|spelling|punctuation|word_choice|style",
            "explanation": "brief explanation of why this is wrong and the correction",
            "position": 0
        }}
    ]
}}

If there are no errors, return:
{{
    "corrected_text": "original text unchanged",
    "errors": []
}}

Only output valid JSON, no other text."""

    EXERCISE_SYSTEM_PROMPT = """You are a language teacher creating exercises for {language} learners at the {level} level.
Topic: {topic}
Exercise type: {exercise_type}
Number of questions: {count}

Create engaging and educational exercises. You MUST respond with valid JSON in this exact format:
{{
    "exercises": [
        {{
            "question": "the question or prompt",
            "options": ["option1", "option2", "option3", "option4"],
            "correct_answer": "the correct answer",
            "hint": "optional hint for the learner",
            "explanation": "explanation of why this answer is correct"
        }}
    ]
}}

For fill_in_blank exercises, use ___ to mark the blank in the question.
For translation exercises, options should be null.
Make sure exercises are appropriate for the {level} level.

Only output valid JSON, no other text."""

    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        rag_service: Optional[RAGService] = None,
    ):
        """Initialize tutor service.

        Args:
            llm_provider: LLM provider instance (uses default if None).
            rag_service: RAG service instance (uses default if None).
        """
        self.llm = llm_provider or get_llm_provider()
        self.rag = rag_service or get_rag_service()
        logger.info("Tutor service initialized")

    async def chat(
        self,
        message: str,
        history: list[ChatMessage],
        target_language: str = "English",
        learner_level: LearnerLevel = LearnerLevel.BEGINNER,
        use_rag: bool = True,
    ) -> tuple[str, list[str]]:
        """Generate a chat response.

        Args:
            message: User's message.
            history: Conversation history.
            target_language: Language being learned.
            learner_level: Learner's proficiency level.
            use_rag: Whether to use RAG for context.

        Returns:
            Tuple of (response text, context used).
        """
        # Get relevant context from RAG
        context_items = []
        if use_rag:
            context_items = self.rag.search_all(message, target_language, n_results=3)

        context_str = ""
        if context_items:
            context_str = "\nRelevant information:\n" + "\n".join(
                f"- {c}" for c in context_items
            )

        # Get language-specific instructions
        if target_language.lower() == "english":
            lang_instructions = self.ENGLISH_INSTRUCTIONS
        else:
            lang_instructions = self.FOREIGN_LANG_INSTRUCTIONS.format(
                language=target_language
            )

        # Build system prompt
        system_prompt = self.TUTOR_SYSTEM_PROMPT.format(
            language=target_language,
            level=learner_level.value,
            language_specific_instructions=lang_instructions,
            context=context_str,
        )

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": message})

        # Generate response
        response = await self.llm.generate(
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )

        return response, context_items

    async def chat_stream(
        self,
        message: str,
        history: list[ChatMessage],
        target_language: str = "English",
        learner_level: LearnerLevel = LearnerLevel.BEGINNER,
        use_rag: bool = True,
    ) -> AsyncIterator[str]:
        """Generate a streaming chat response.

        Args:
            message: User's message.
            history: Conversation history.
            target_language: Language being learned.
            learner_level: Learner's proficiency level.
            use_rag: Whether to use RAG for context.

        Yields:
            Response text chunks.
        """
        # Get relevant context from RAG
        context_items = []
        if use_rag:
            context_items = self.rag.search_all(message, target_language, n_results=3)

        context_str = ""
        if context_items:
            context_str = "\nRelevant information:\n" + "\n".join(
                f"- {c}" for c in context_items
            )

        # Get language-specific instructions
        if target_language.lower() == "english":
            lang_instructions = self.ENGLISH_INSTRUCTIONS
        else:
            lang_instructions = self.FOREIGN_LANG_INSTRUCTIONS.format(
                language=target_language
            )

        # Build system prompt
        system_prompt = self.TUTOR_SYSTEM_PROMPT.format(
            language=target_language,
            level=learner_level.value,
            language_specific_instructions=lang_instructions,
            context=context_str,
        )

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": message})

        # Stream response
        async for chunk in self.llm.generate_stream(
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        ):
            yield chunk

    async def correct_text(
        self,
        text: str,
        target_language: str = "English",
    ) -> CorrectionResponse:
        """Correct grammar and spelling in text.

        Args:
            text: Text to correct.
            target_language: Language of the text.

        Returns:
            CorrectionResponse with corrections.
        """
        system_prompt = self.CORRECTION_SYSTEM_PROMPT.format(language=target_language)

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Please check and correct this {target_language} text:\n\n{text}",
            },
        ]

        # Generate with JSON mode
        response = await self.llm.generate(
            messages=messages,
            temperature=0.3,  # Lower temperature for consistent corrections
            max_tokens=2048,
            json_mode=True,
        )

        # Parse JSON response
        try:
            data = json.loads(response)
            errors = [
                CorrectionError(
                    original=e.get("original", ""),
                    corrected=e.get("corrected", ""),
                    error_type=e.get("error_type", "grammar"),
                    explanation=e.get("explanation", ""),
                    position=e.get("position"),
                )
                for e in data.get("errors", [])
            ]

            return CorrectionResponse(
                original_text=text,
                corrected_text=data.get("corrected_text", text),
                errors=errors,
                has_errors=len(errors) > 0,
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse correction response: {e}")
            # Return original text if parsing fails
            return CorrectionResponse(
                original_text=text,
                corrected_text=text,
                errors=[],
                has_errors=False,
            )

    async def generate_exercises(
        self,
        topic: str,
        target_language: str = "English",
        exercise_type: ExerciseType = ExerciseType.MULTIPLE_CHOICE,
        learner_level: LearnerLevel = LearnerLevel.BEGINNER,
        count: int = 5,
    ) -> list[Exercise]:
        """Generate practice exercises.

        Args:
            topic: Topic for exercises.
            target_language: Target language.
            exercise_type: Type of exercise.
            learner_level: Learner's level.
            count: Number of exercises.

        Returns:
            List of Exercise objects.
        """
        system_prompt = self.EXERCISE_SYSTEM_PROMPT.format(
            language=target_language,
            level=learner_level.value,
            topic=topic,
            exercise_type=exercise_type.value,
            count=count,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Generate {count} {exercise_type.value} exercises about '{topic}' for {target_language} learners at the {learner_level.value} level.",
            },
        ]

        response = await self.llm.generate(
            messages=messages,
            temperature=0.7,
            max_tokens=3000,
            json_mode=True,
        )

        try:
            data = json.loads(response)
            exercises = []

            for i, ex in enumerate(data.get("exercises", [])):
                exercises.append(
                    Exercise(
                        id=str(uuid.uuid4()),
                        type=exercise_type,
                        question=ex.get("question", ""),
                        options=ex.get("options"),
                        correct_answer=ex.get("correct_answer", ""),
                        hint=ex.get("hint"),
                        explanation=ex.get("explanation", ""),
                    )
                )

            return exercises

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse exercise response: {e}")
            return []

    async def check_answer(
        self,
        user_answer: str,
        correct_answer: str,
        target_language: str = "English",
    ) -> tuple[bool, str]:
        """Check if an answer is correct and provide feedback.

        Args:
            user_answer: User's answer.
            correct_answer: The correct answer.
            target_language: Target language.

        Returns:
            Tuple of (is_correct, feedback).
        """
        # Simple string comparison (case-insensitive, strip whitespace)
        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()

        if is_correct:
            feedback = "¡Excelente! That's correct! 🎉"
        else:
            # Generate helpful feedback using LLM
            messages = [
                {
                    "role": "system",
                    "content": f"You are a helpful {target_language} tutor. Give brief, encouraging feedback when a student gives an incorrect answer. Be positive and explain the correct answer.",
                },
                {
                    "role": "user",
                    "content": f"I answered '{user_answer}' but the correct answer was '{correct_answer}'. Can you explain why?",
                },
            ]

            feedback = await self.llm.generate(
                messages=messages,
                temperature=0.7,
                max_tokens=200,
            )

        return is_correct, feedback

    async def explain_grammar(
        self,
        topic: str,
        target_language: str = "English",
        learner_level: LearnerLevel = LearnerLevel.BEGINNER,
    ) -> str:
        """Explain a grammar topic.

        Args:
            topic: Grammar topic to explain.
            target_language: Target language.
            learner_level: Learner's level.

        Returns:
            Grammar explanation.
        """
        # Get relevant context
        context_items = self.rag.search_grammar(topic, target_language, n_results=3)
        context_str = "\n".join(c["content"] for c in context_items)

        messages = [
            {
                "role": "system",
                "content": f"""You are an expert {target_language} grammar teacher.
Explain grammar concepts clearly for {learner_level.value} learners.
Use examples and keep explanations appropriate for the level.

Reference information:
{context_str}""",
            },
            {"role": "user", "content": f"Please explain: {topic}"},
        ]

        return await self.llm.generate(
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
        )


# Cached instance
_tutor_service: Optional[TutorService] = None


def get_tutor_service() -> TutorService:
    """Get the tutor service instance.

    Returns:
        Tutor service singleton instance.
    """
    global _tutor_service

    if _tutor_service is None:
        _tutor_service = TutorService()

    return _tutor_service

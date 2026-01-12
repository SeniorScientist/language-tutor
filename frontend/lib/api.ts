/**
 * API client for the Foreign Language Tutor backend.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  message: string;
  history: ChatMessage[];
  target_language: string;
  learner_level: "beginner" | "intermediate" | "advanced";
}

export interface ChatResponse {
  response: string;
  context_used?: string[];
}

export interface CorrectionError {
  original: string;
  corrected: string;
  error_type: string;
  explanation: string;
  position?: number;
}

export interface CorrectionResponse {
  original_text: string;
  corrected_text: string;
  errors: CorrectionError[];
  has_errors: boolean;
}

export interface Exercise {
  id: string;
  type: "multiple_choice" | "fill_in_blank" | "translation";
  question: string;
  options?: string[];
  correct_answer: string;
  hint?: string;
  explanation: string;
}

export interface ExerciseCheckResponse {
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  feedback: string;
}

export interface HealthResponse {
  status: string;
  llm_provider: string;
  llm_status: string;
  rag_status: string;
}

// API Functions

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.statusText}`);
  }

  return response.json();
}

export async function streamChatMessage(
  request: ChatRequest,
  onChunk: (chunk: string) => void,
  onDone: () => void,
  onError: (error: Error) => void,
  abortSignal?: AbortSignal
): Promise<void> {
  try {
    const response = await fetch(`${API_URL}/api/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
      signal: abortSignal,
    });

    if (!response.ok) {
      throw new Error(`Stream request failed: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("No response body");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      // Check if aborted
      if (abortSignal?.aborted) {
        await reader.cancel();
        onDone();
        return;
      }

      const { done, value } = await reader.read();
      
      if (done) {
        onDone();
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") {
            onDone();
            return;
          }
          onChunk(data);
        }
      }
    }
  } catch (error) {
    // Don't report abort as an error
    if (error instanceof Error && error.name === "AbortError") {
      onDone();
      return;
    }
    onError(error instanceof Error ? error : new Error(String(error)));
  }
}

export async function correctText(
  text: string,
  targetLanguage: string
): Promise<CorrectionResponse> {
  const response = await fetch(`${API_URL}/api/correct/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text,
      target_language: targetLanguage,
    }),
  });

  if (!response.ok) {
    throw new Error(`Correction request failed: ${response.statusText}`);
  }

  return response.json();
}

export async function generateExercises(
  topic: string,
  targetLanguage: string,
  exerciseType: "multiple_choice" | "fill_in_blank" | "translation",
  learnerLevel: "beginner" | "intermediate" | "advanced",
  count: number = 5
): Promise<Exercise[]> {
  const response = await fetch(`${API_URL}/api/exercises/generate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      topic,
      target_language: targetLanguage,
      exercise_type: exerciseType,
      learner_level: learnerLevel,
      count,
    }),
  });

  if (!response.ok) {
    throw new Error(`Exercise generation failed: ${response.statusText}`);
  }

  return response.json();
}

export async function checkExerciseAnswer(
  exerciseId: string,
  userAnswer: string,
  correctAnswer: string,
  targetLanguage: string
): Promise<ExerciseCheckResponse> {
  const response = await fetch(
    `${API_URL}/api/exercises/check?target_language=${encodeURIComponent(targetLanguage)}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        exercise_id: exerciseId,
        user_answer: userAnswer,
        correct_answer: correctAnswer,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(`Answer check failed: ${response.statusText}`);
  }

  return response.json();
}

export async function getExerciseTopics(
  targetLanguage: string
): Promise<{ language: string; topics: string[] }> {
  const response = await fetch(
    `${API_URL}/api/exercises/topics?target_language=${encodeURIComponent(targetLanguage)}`
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch topics: ${response.statusText}`);
  }

  return response.json();
}

export async function healthCheck(): Promise<HealthResponse> {
  const response = await fetch(`${API_URL}/api/health`);

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }

  return response.json();
}


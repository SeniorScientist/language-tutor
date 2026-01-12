"use client";

import { useState, useEffect } from "react";
import {
  Loader2,
  RefreshCw,
  CheckCircle,
  XCircle,
  Lightbulb,
  Trophy,
  BookOpen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import {
  generateExercises,
  checkExerciseAnswer,
  getExerciseTopics,
  Exercise,
} from "@/lib/api";

const LANGUAGES = [
  { value: "English", label: "🇬🇧 English" },
  { value: "Chinese", label: "🇨🇳 Chinese" },
  { value: "Russian", label: "🇷🇺 Russian" },
  { value: "Japanese", label: "🇯🇵 Japanese" },
];

const EXERCISE_TYPES = [
  { value: "multiple_choice", label: "Multiple Choice" },
  { value: "fill_in_blank", label: "Fill in the Blank" },
  { value: "translation", label: "Translation" },
];

const LEVELS = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
];

interface ExerciseState extends Exercise {
  userAnswer?: string;
  isCorrect?: boolean;
  feedback?: string;
  showHint?: boolean;
  submitted?: boolean;
}

function MultipleChoiceExercise({
  exercise,
  onAnswer,
  disabled,
}: {
  exercise: ExerciseState;
  onAnswer: (answer: string) => void;
  disabled: boolean;
}) {
  return (
    <RadioGroup
      value={exercise.userAnswer || ""}
      onValueChange={onAnswer}
      disabled={disabled}
      className="space-y-3"
    >
      {exercise.options?.map((option, index) => (
        <div
          key={index}
          className={cn(
            "flex items-center space-x-3 rounded-lg border p-4 transition-all duration-200",
            exercise.submitted && option === exercise.correct_answer
              ? "border-green-500 bg-green-50 dark:bg-green-900/20"
              : exercise.submitted &&
                option === exercise.userAnswer &&
                !exercise.isCorrect
              ? "border-red-500 bg-red-50 dark:bg-red-900/20"
              : exercise.userAnswer === option
              ? "border-primary bg-primary/5"
              : "hover:border-muted-foreground/50"
          )}
        >
          <RadioGroupItem value={option} id={`option-${index}`} />
          <Label
            htmlFor={`option-${index}`}
            className="flex-1 cursor-pointer font-normal"
          >
            {option}
          </Label>
          {exercise.submitted && option === exercise.correct_answer && (
            <CheckCircle className="h-5 w-5 text-green-500" />
          )}
          {exercise.submitted &&
            option === exercise.userAnswer &&
            !exercise.isCorrect && (
              <XCircle className="h-5 w-5 text-red-500" />
            )}
        </div>
      ))}
    </RadioGroup>
  );
}

function FillInBlankExercise({
  exercise,
  onAnswer,
  disabled,
}: {
  exercise: ExerciseState;
  onAnswer: (answer: string) => void;
  disabled: boolean;
}) {
  const parts = exercise.question.split("___");

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2 text-lg">
        <span>{parts[0]}</span>
        <Input
          value={exercise.userAnswer || ""}
          onChange={(e) => onAnswer(e.target.value)}
          disabled={disabled}
          className={cn(
            "inline-block w-48",
            exercise.submitted &&
              (exercise.isCorrect
                ? "border-green-500 bg-green-50"
                : "border-red-500 bg-red-50")
          )}
          placeholder="Type your answer..."
        />
        <span>{parts[1]}</span>
      </div>
      {exercise.submitted && !exercise.isCorrect && (
        <p className="text-sm text-muted-foreground">
          Correct answer: <strong>{exercise.correct_answer}</strong>
        </p>
      )}
    </div>
  );
}

function TranslationExercise({
  exercise,
  onAnswer,
  disabled,
}: {
  exercise: ExerciseState;
  onAnswer: (answer: string) => void;
  disabled: boolean;
}) {
  return (
    <div className="space-y-4">
      <div className="rounded-lg bg-muted p-4">
        <p className="text-lg font-medium">{exercise.question}</p>
      </div>
      <Input
        value={exercise.userAnswer || ""}
        onChange={(e) => onAnswer(e.target.value)}
        disabled={disabled}
        className={cn(
          exercise.submitted &&
            (exercise.isCorrect
              ? "border-green-500 bg-green-50"
              : "border-red-500 bg-red-50")
        )}
        placeholder="Type your translation..."
      />
      {exercise.submitted && !exercise.isCorrect && (
        <p className="text-sm text-muted-foreground">
          Correct answer: <strong>{exercise.correct_answer}</strong>
        </p>
      )}
    </div>
  );
}

export function ExercisePanel() {
  const [language, setLanguage] = useState("English");
  const [exerciseType, setExerciseType] = useState<
    "multiple_choice" | "fill_in_blank" | "translation"
  >("multiple_choice");
  const [level, setLevel] = useState<"beginner" | "intermediate" | "advanced">(
    "beginner"
  );
  const [topic, setTopic] = useState("");
  const [topics, setTopics] = useState<string[]>([]);
  const [exercises, setExercises] = useState<ExerciseState[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isChecking, setIsChecking] = useState(false);
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [showResults, setShowResults] = useState(false);

  // Load topics when language changes
  useEffect(() => {
    const loadTopics = async () => {
      try {
        const response = await getExerciseTopics(language);
        setTopics(response.topics);
        if (response.topics.length > 0) {
          setTopic(response.topics[0]);
        }
      } catch (err) {
        console.error("Failed to load topics:", err);
      }
    };
    loadTopics();
  }, [language]);

  const handleGenerate = async () => {
    if (!topic) return;

    setIsLoading(true);
    setExercises([]);
    setCurrentIndex(0);
    setScore({ correct: 0, total: 0 });
    setShowResults(false);

    try {
      const response = await generateExercises(
        topic,
        language,
        exerciseType,
        level,
        5
      );
      setExercises(response.map((e) => ({ ...e, submitted: false })));
    } catch (err) {
      console.error("Failed to generate exercises:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswer = (answer: string) => {
    setExercises((prev) =>
      prev.map((e, i) =>
        i === currentIndex ? { ...e, userAnswer: answer } : e
      )
    );
  };

  const handleSubmit = async () => {
    const currentExercise = exercises[currentIndex];
    if (!currentExercise.userAnswer) return;

    setIsChecking(true);

    try {
      const response = await checkExerciseAnswer(
        currentExercise.id,
        currentExercise.userAnswer,
        currentExercise.correct_answer,
        language
      );

      setExercises((prev) =>
        prev.map((e, i) =>
          i === currentIndex
            ? {
                ...e,
                isCorrect: response.is_correct,
                feedback: response.feedback,
                submitted: true,
              }
            : e
        )
      );

      setScore((prev) => ({
        correct: prev.correct + (response.is_correct ? 1 : 0),
        total: prev.total + 1,
      }));
    } catch (err) {
      console.error("Failed to check answer:", err);
    } finally {
      setIsChecking(false);
    }
  };

  const handleNext = () => {
    if (currentIndex < exercises.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      setShowResults(true);
    }
  };

  const handleShowHint = () => {
    setExercises((prev) =>
      prev.map((e, i) =>
        i === currentIndex ? { ...e, showHint: true } : e
      )
    );
  };

  const currentExercise = exercises[currentIndex];
  const progress = exercises.length
    ? ((currentIndex + 1) / exercises.length) * 100
    : 0;

  return (
    <div className="space-y-6">
      {/* Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Generate Exercises</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-2">
              <Label>Language</Label>
              <Select value={language} onValueChange={setLanguage}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {LANGUAGES.map((lang) => (
                    <SelectItem key={lang.value} value={lang.value}>
                      {lang.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Type</Label>
              <Select
                value={exerciseType}
                onValueChange={(v: typeof exerciseType) => setExerciseType(v)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {EXERCISE_TYPES.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Level</Label>
              <Select value={level} onValueChange={(v: typeof level) => setLevel(v)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {LEVELS.map((lvl) => (
                    <SelectItem key={lvl.value} value={lvl.value}>
                      {lvl.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Topic</Label>
              <Select value={topic} onValueChange={setTopic}>
                <SelectTrigger>
                  <SelectValue placeholder="Select topic" />
                </SelectTrigger>
                <SelectContent>
                  {topics.map((t) => (
                    <SelectItem key={t} value={t}>
                      {t}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="mt-6 flex justify-end">
            <Button onClick={handleGenerate} disabled={!topic || isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <BookOpen className="mr-2 h-4 w-4" />
                  Start Practice
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Exercise display */}
      {exercises.length > 0 && !showResults && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">
                Question {currentIndex + 1} of {exercises.length}
              </CardTitle>
              <div className="text-sm text-muted-foreground">
                Score: {score.correct}/{score.total}
              </div>
            </div>
            <Progress value={progress} className="mt-2" />
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Question */}
            <div className="rounded-lg bg-muted/50 p-4">
              <p className="text-lg font-medium">{currentExercise.question}</p>
            </div>

            {/* Exercise type specific component */}
            {currentExercise.type === "multiple_choice" && (
              <MultipleChoiceExercise
                exercise={currentExercise}
                onAnswer={handleAnswer}
                disabled={currentExercise.submitted || false}
              />
            )}

            {currentExercise.type === "fill_in_blank" && (
              <FillInBlankExercise
                exercise={currentExercise}
                onAnswer={handleAnswer}
                disabled={currentExercise.submitted || false}
              />
            )}

            {currentExercise.type === "translation" && (
              <TranslationExercise
                exercise={currentExercise}
                onAnswer={handleAnswer}
                disabled={currentExercise.submitted || false}
              />
            )}

            {/* Hint */}
            {currentExercise.hint && !currentExercise.showHint && !currentExercise.submitted && (
              <Button variant="ghost" size="sm" onClick={handleShowHint}>
                <Lightbulb className="mr-2 h-4 w-4" />
                Show Hint
              </Button>
            )}

            {currentExercise.showHint && (
              <div className="flex items-start gap-3 rounded-lg bg-amber-50 p-4 dark:bg-amber-900/20">
                <Lightbulb className="h-5 w-5 text-amber-500" />
                <p className="text-sm text-amber-700 dark:text-amber-400">
                  {currentExercise.hint}
                </p>
              </div>
            )}

            {/* Feedback */}
            {currentExercise.submitted && (
              <div
                className={cn(
                  "rounded-lg p-4",
                  currentExercise.isCorrect
                    ? "bg-green-50 dark:bg-green-900/20"
                    : "bg-red-50 dark:bg-red-900/20"
                )}
              >
                <div className="flex items-center gap-2 mb-2">
                  {currentExercise.isCorrect ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                  <span
                    className={cn(
                      "font-medium",
                      currentExercise.isCorrect
                        ? "text-green-700 dark:text-green-400"
                        : "text-red-700 dark:text-red-400"
                    )}
                  >
                    {currentExercise.isCorrect ? "Correct!" : "Not quite right"}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground">
                  {currentExercise.feedback || currentExercise.explanation}
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-3">
              {!currentExercise.submitted ? (
                <Button
                  onClick={handleSubmit}
                  disabled={!currentExercise.userAnswer || isChecking}
                >
                  {isChecking ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Checking...
                    </>
                  ) : (
                    "Check Answer"
                  )}
                </Button>
              ) : (
                <Button onClick={handleNext}>
                  {currentIndex < exercises.length - 1
                    ? "Next Question"
                    : "See Results"}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {showResults && (
        <Card className="text-center">
          <CardContent className="py-12">
            <Trophy
              className={cn(
                "mx-auto mb-4 h-16 w-16",
                score.correct === score.total
                  ? "text-yellow-500"
                  : score.correct >= score.total / 2
                  ? "text-green-500"
                  : "text-orange-500"
              )}
            />
            <h2 className="font-display text-3xl font-bold mb-2">
              {score.correct === score.total
                ? "Perfect Score!"
                : score.correct >= score.total / 2
                ? "Great Job!"
                : "Keep Practicing!"}
            </h2>
            <p className="text-xl text-muted-foreground mb-6">
              You got {score.correct} out of {score.total} correct
            </p>
            <div className="flex justify-center gap-4">
              <Button variant="outline" onClick={() => setShowResults(false)}>
                Review Answers
              </Button>
              <Button onClick={handleGenerate}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Practice Again
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}


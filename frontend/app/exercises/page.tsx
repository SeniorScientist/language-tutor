import { ExercisePanel } from "@/components/ExercisePanel";

export const metadata = {
  title: "Exercises - LinguaAI",
  description: "Practice with interactive language exercises",
};

export default function ExercisesPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold mb-2">Practice Exercises</h1>
        <p className="text-muted-foreground">
          Test your knowledge with multiple choice, fill in the blank, and translation exercises.
        </p>
      </div>
      <ExercisePanel />
    </div>
  );
}


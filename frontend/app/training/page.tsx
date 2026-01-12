import { TrainingPanel } from "@/components/TrainingPanel";

export const metadata = {
  title: "Training - LinguaAI",
  description: "Train and fine-tune your own language model",
};

export default function TrainingPage() {
  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold mb-2">Model Training</h1>
        <p className="text-muted-foreground">
          Create training data from conversations and fine-tune your own custom language model
          for better performance tailored to your needs.
        </p>
      </div>
      <TrainingPanel />
    </div>
  );
}


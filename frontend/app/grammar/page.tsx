import { CorrectionTool } from "@/components/CorrectionTool";

export const metadata = {
  title: "Grammar Check - LinguaAI",
  description: "Check your writing for grammar, spelling, and punctuation errors",
};

export default function GrammarPage() {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold mb-2">Grammar Correction</h1>
        <p className="text-muted-foreground">
          Paste your text below and get instant feedback on grammar, spelling, and punctuation errors.
        </p>
      </div>
      <CorrectionTool />
    </div>
  );
}


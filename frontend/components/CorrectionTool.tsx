"use client";

import { useState } from "react";
import {
  Check,
  Copy,
  Loader2,
  AlertCircle,
  CheckCircle,
  ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { correctText, CorrectionResponse, CorrectionError } from "@/lib/api";

const LANGUAGES = [
  { value: "English", label: "🇬🇧 English" },
  { value: "Chinese", label: "🇨🇳 Chinese" },
  { value: "Russian", label: "🇷🇺 Russian" },
  { value: "Japanese", label: "🇯🇵 Japanese" },
];

const ERROR_TYPE_COLORS: Record<string, string> = {
  grammar: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  spelling: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400",
  punctuation: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  word_choice: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  style: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
};

function ErrorBadge({ type }: { type: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize",
        ERROR_TYPE_COLORS[type] || ERROR_TYPE_COLORS.grammar
      )}
    >
      {type.replace("_", " ")}
    </span>
  );
}

function CorrectionResult({
  result,
  onCopy,
}: {
  result: CorrectionResponse;
  onCopy: () => void;
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(result.corrected_text);
    setCopied(true);
    onCopy();
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Summary */}
      <div
        className={cn(
          "flex items-center gap-3 rounded-lg p-4",
          result.has_errors
            ? "bg-orange-50 dark:bg-orange-900/20"
            : "bg-green-50 dark:bg-green-900/20"
        )}
      >
        {result.has_errors ? (
          <>
            <AlertCircle className="h-5 w-5 text-orange-500" />
            <span className="font-medium text-orange-700 dark:text-orange-400">
              Found {result.errors.length} issue{result.errors.length !== 1 ? "s" : ""} in your text
            </span>
          </>
        ) : (
          <>
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="font-medium text-green-700 dark:text-green-400">
              Your text looks great! No errors found.
            </span>
          </>
        )}
      </div>

      {/* Corrected text */}
      <Card>
        <CardHeader className="flex-row items-center justify-between space-y-0">
          <CardTitle className="text-lg">Corrected Text</CardTitle>
          <Button variant="outline" size="sm" onClick={handleCopy}>
            {copied ? (
              <>
                <Check className="mr-2 h-4 w-4" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="mr-2 h-4 w-4" />
                Copy
              </>
            )}
          </Button>
        </CardHeader>
        <CardContent>
          <p className="leading-relaxed text-foreground">
            {result.corrected_text}
          </p>
        </CardContent>
      </Card>

      {/* Error details */}
      {result.has_errors && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Error Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {result.errors.map((error, index) => (
              <div
                key={index}
                className="rounded-lg border p-4 transition-colors hover:bg-muted/50"
              >
                <div className="mb-3 flex items-center gap-2">
                  <ErrorBadge type={error.error_type} />
                </div>

                <div className="mb-3 flex items-center gap-3 text-sm">
                  <span className="rounded bg-red-100 px-2 py-1 text-red-700 line-through dark:bg-red-900/30 dark:text-red-400">
                    {error.original}
                  </span>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  <span className="rounded bg-green-100 px-2 py-1 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                    {error.corrected}
                  </span>
                </div>

                <p className="text-sm text-muted-foreground">
                  {error.explanation}
                </p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export function CorrectionTool() {
  const [text, setText] = useState("");
  const [language, setLanguage] = useState("English");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<CorrectionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCorrect = async () => {
    if (!text.trim()) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await correctText(text, language);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setText("");
    setResult(null);
    setError(null);
  };

  return (
    <div className="space-y-6">
      {/* Input section */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Check Your Writing</CardTitle>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Language:</span>
              <Select value={language} onValueChange={setLanguage}>
                <SelectTrigger className="w-36">
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
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={`Enter your ${language} text here to check for grammar, spelling, and punctuation errors...`}
            className="min-h-[180px]"
          />

          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {text.length} characters
            </p>
            <div className="flex gap-3">
              <Button variant="outline" onClick={handleClear} disabled={!text && !result}>
                Clear
              </Button>
              <Button onClick={handleCorrect} disabled={!text.trim() || isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Checking...
                  </>
                ) : (
                  <>
                    <Check className="mr-2 h-4 w-4" />
                    Check Grammar
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error message */}
      {error && (
        <div className="flex items-center gap-3 rounded-lg bg-destructive/10 p-4 text-destructive">
          <AlertCircle className="h-5 w-5" />
          <span>{error}</span>
        </div>
      )}

      {/* Results */}
      {result && <CorrectionResult result={result} onCopy={() => {}} />}
    </div>
  );
}


"use client";

import { useEffect, useState } from "react";
import { Wifi, WifiOff, Loader2 } from "lucide-react";
import { healthCheck, HealthResponse } from "@/lib/api";

export function Header() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await healthCheck();
        setHealth(response);
        setError(false);
      } catch (err) {
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <header className="fixed top-0 right-0 left-64 z-30 h-16 border-b bg-background/80 backdrop-blur-lg">
      <div className="flex h-full items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <h2 className="font-display text-lg font-medium">
            Welcome to your language journey
          </h2>
        </div>

        <div className="flex items-center gap-4">
          {/* Status indicator */}
          <div className="flex items-center gap-2 rounded-full border px-4 py-1.5 text-sm">
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                <span className="text-muted-foreground">Connecting...</span>
              </>
            ) : error ? (
              <>
                <WifiOff className="h-4 w-4 text-destructive" />
                <span className="text-destructive">Offline</span>
              </>
            ) : (
              <>
                <Wifi className="h-4 w-4 text-success" />
                <span className="text-success">
                  {health?.llm_provider === "groq" ? "Groq API" : "Local LLM"}
                </span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}


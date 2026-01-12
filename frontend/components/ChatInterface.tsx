"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Loader2, RefreshCw, BookOpen, Square } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { ChatMessage, streamChatMessage } from "@/lib/api";

const LANGUAGES = [
  { value: "English", label: "🇬🇧 English" },
  { value: "Chinese", label: "🇨🇳 Chinese" },
  { value: "Russian", label: "🇷🇺 Russian" },
  { value: "Japanese", label: "🇯🇵 Japanese" },
];

const LEVELS = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
];

interface Message extends ChatMessage {
  id: string;
  isStreaming?: boolean;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [language, setLanguage] = useState("English");
  const [level, setLevel] = useState<"beginner" | "intermediate" | "advanced">("beginner");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
    };

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: "",
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setInput("");
    setIsLoading(true);

    // Create new AbortController for this request
    abortControllerRef.current = new AbortController();

    const history = messages.map((m) => ({ role: m.role, content: m.content }));

    await streamChatMessage(
      {
        message: userMessage.content,
        history,
        target_language: language,
        learner_level: level,
      },
      (chunk) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMessage.id
              ? { ...m, content: m.content + chunk }
              : m
          )
        );
      },
      () => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMessage.id ? { ...m, isStreaming: false } : m
          )
        );
        setIsLoading(false);
        abortControllerRef.current = null;
      },
      (error) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMessage.id
              ? {
                  ...m,
                  content: `Sorry, I encountered an error: ${error.message}. Please try again.`,
                  isStreaming: false,
                }
              : m
          )
        );
        setIsLoading(false);
        abortControllerRef.current = null;
      },
      abortControllerRef.current.signal
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    // Mark the streaming message as complete
    setMessages((prev) =>
      prev.map((m) =>
        m.isStreaming ? { ...m, isStreaming: false, content: m.content + " [Stopped]" } : m
      )
    );
    setIsLoading(false);
  }, []);

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      {/* Settings bar */}
      <div className="mb-4 flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-muted-foreground">Language:</span>
          <Select value={language} onValueChange={setLanguage}>
            <SelectTrigger className="w-40">
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

        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-muted-foreground">Level:</span>
          <Select value={level} onValueChange={(v: typeof level) => setLevel(v)}>
            <SelectTrigger className="w-36">
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

        <div className="flex-1" />

        <Button variant="outline" size="sm" onClick={clearChat}>
          <RefreshCw className="mr-2 h-4 w-4" />
          New Chat
        </Button>
      </div>

      {/* Messages area */}
      <Card className="flex-1 overflow-hidden p-0">
        <div className="flex h-full flex-col">
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center text-center">
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
                  <BookOpen className="h-8 w-8 text-primary" />
                </div>
                <h3 className="font-display text-xl font-semibold mb-2">
                  Start Learning {language}!
                </h3>
                <p className="max-w-md text-muted-foreground">
                  I'm your AI language tutor. Ask me anything about {language} - vocabulary,
                  grammar, pronunciation, or just practice conversation!
                </p>
                <div className="mt-6 grid gap-2">
                  <p className="text-sm text-muted-foreground">Try asking:</p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {[
                      `How do I say "hello" in ${language}?`,
                      `Teach me basic greetings`,
                      `What's the difference between formal and informal speech?`,
                    ].map((suggestion) => (
                      <button
                        key={suggestion}
                        onClick={() => setInput(suggestion)}
                        className="rounded-full border px-4 py-1.5 text-sm hover:bg-muted transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <>
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={cn(
                      "flex animate-slide-up",
                      message.role === "user" ? "justify-end" : "justify-start"
                    )}
                  >
                    <div
                      className={cn(
                        "max-w-[80%] rounded-2xl px-5 py-3",
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      )}
                    >
                      {message.role === "assistant" ? (
                        <div className="prose prose-sm dark:prose-invert">
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                          {message.isStreaming && (
                            <span className="typing-indicator ml-1">
                              <span></span>
                              <span></span>
                              <span></span>
                            </span>
                          )}
                        </div>
                      ) : (
                        <p>{message.content}</p>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Input area */}
          <div className="border-t p-4">
            <form onSubmit={handleSubmit} className="flex gap-3">
              <Textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={`Ask me anything about ${language}...`}
                className="min-h-[52px] max-h-[200px] resize-none"
                rows={1}
                disabled={isLoading}
              />
              {isLoading ? (
                <Button
                  type="button"
                  size="lg"
                  variant="destructive"
                  onClick={stopGeneration}
                  className="px-6"
                >
                  <Square className="h-5 w-5" />
                </Button>
              ) : (
                <Button
                  type="submit"
                  size="lg"
                  disabled={!input.trim()}
                  className="px-6"
                >
                  <Send className="h-5 w-5" />
                </Button>
              )}
            </form>
          </div>
        </div>
      </Card>
    </div>
  );
}


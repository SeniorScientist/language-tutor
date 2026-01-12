"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MessageSquare,
  SpellCheck,
  GraduationCap,
  Languages,
  Sparkles,
  Brain,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  {
    name: "Chat Tutor",
    href: "/",
    icon: MessageSquare,
    description: "Practice conversation",
  },
  {
    name: "Grammar Check",
    href: "/grammar",
    icon: SpellCheck,
    description: "Correct your writing",
  },
  {
    name: "Exercises",
    href: "/exercises",
    icon: GraduationCap,
    description: "Practice with quizzes",
  },
  {
    name: "Training",
    href: "/training",
    icon: Brain,
    description: "Fine-tune your model",
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r bg-card">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 border-b px-6">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <Languages className="h-5 w-5" />
        </div>
        <div>
          <h1 className="font-display text-lg font-semibold">LinguaAI</h1>
          <p className="text-xs text-muted-foreground">Language Tutor</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-primary text-primary-foreground shadow-md"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon className="h-5 w-5" />
              <div>
                <div>{item.name}</div>
                <div
                  className={cn(
                    "text-xs",
                    isActive ? "text-primary-foreground/80" : "text-muted-foreground"
                  )}
                >
                  {item.description}
                </div>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Pro tip */}
      <div className="absolute bottom-6 left-4 right-4">
        <div className="rounded-xl border bg-gradient-to-br from-primary/10 to-accent/10 p-4">
          <div className="mb-2 flex items-center gap-2 text-sm font-medium">
            <Sparkles className="h-4 w-4 text-primary" />
            <span>Pro Tip</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Practice daily for just 15 minutes to see significant improvement in
            your language skills!
          </p>
        </div>
      </div>
    </aside>
  );
}


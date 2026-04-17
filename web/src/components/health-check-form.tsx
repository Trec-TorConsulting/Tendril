"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { getGrowType } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface HealthCheckFormProps {
  growType: string;
  onSubmit: (answers: Record<string, string>) => void;
}

interface HealthQuestion {
  id: string;
  question: string;
  type: "boolean" | "text";
}

/* Heuristic: questions starting with these words expect a yes/no answer. */
const YES_NO_PATTERN = /^(is |are |any |do |does |did |can |have |has |using |pre-soaked |pre-buffered )/i;

function classifyQuestion(q: string): "boolean" | "text" {
  return YES_NO_PATTERN.test(q) ? "boolean" : "text";
}

export function HealthCheckForm({ growType, onSubmit }: HealthCheckFormProps) {
  const [questions, setQuestions] = useState<HealthQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  useEffect(() => {
    const load = async () => {
      const token = getAccessToken();
      if (!token) return;
      try {
        const profile = await getGrowType(token, growType);
        const qs = profile.health_check_questions;
        if (Array.isArray(qs)) {
          setQuestions(
            qs.map((q: unknown, i: number) => {
              if (typeof q === "string") {
                return { id: `q${i}`, question: q, type: classifyQuestion(q) };
              }
              const item = q as Record<string, unknown>;
              const text = (item.question as string) || "";
              return {
                id: (item.id as string) || `q${i}`,
                question: text,
                type: Array.isArray(item.options) ? "boolean" as const : classifyQuestion(text),
              };
            }),
          );
        }
      } catch {
        // No health check questions available
      }
    };
    load();
  }, [growType]);

  if (questions.length === 0) {
    return <p className="text-sm text-muted-foreground">No health check available for this grow type.</p>;
  }

  const allAnswered = questions.every((q) => answers[q.id]?.trim());

  return (
    <div className="space-y-4">
      {questions.map((q) => (
        <div key={q.id}>
          <p className="mb-2 text-sm font-medium">{q.question}</p>
          {q.type === "boolean" ? (
            <div className="flex flex-wrap gap-2">
              {["Yes", "No", "Not sure"].map((opt) => (
                <button
                  key={opt}
                  type="button"
                  className={`rounded border px-3 py-1 text-sm transition-colors ${
                    answers[q.id] === opt
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border bg-muted text-muted-foreground hover:border-primary/50"
                  }`}
                  onClick={() => setAnswers({ ...answers, [q.id]: opt })}
                >
                  {opt}
                </button>
              ))}
            </div>
          ) : (
            <Input
              placeholder="Describe…"
              value={answers[q.id] || ""}
              onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
              className="max-w-sm"
            />
          )}
        </div>
      ))}
      <Button
        size="sm"
        onClick={() => onSubmit(answers)}
        disabled={!allAnswered}
      >
        Submit Health Check
      </Button>
    </div>
  );
}

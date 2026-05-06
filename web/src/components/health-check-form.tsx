"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { getGrowType } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface HealthCheckFormProps {
  growType: string;
  onSubmit: (answers: Record<string, string>) => void;
}

interface HealthQuestion {
  id: string;
  question: string;
  type: "boolean" | "text" | "date" | "select";
  options?: string[];
}

/* Heuristic: questions starting with these words expect a yes/no answer. */
const YES_NO_PATTERN = /^(is |are |any |do |does |did |can |have |has |using |pre-soaked |pre-buffered )/i;

/* Pattern matching for special input types */
const DATE_PATTERN = /when did you last|last.*change|last.*replaced/i;
const WATER_COLOR_PATTERN = /water color|water.*clarity|color.*clarity/i;

const WATER_COLOR_OPTIONS = [
  "Clear",
  "Slightly tinted (light yellow/amber)",
  "Cloudy/murky",
  "Brown/dark",
  "Green (algae)",
  "Foamy/bubbly surface",
];

function classifyQuestion(q: string): { type: HealthQuestion["type"]; options?: string[] } {
  if (DATE_PATTERN.test(q)) return { type: "date" };
  if (WATER_COLOR_PATTERN.test(q)) return { type: "select", options: WATER_COLOR_OPTIONS };
  if (YES_NO_PATTERN.test(q)) return { type: "boolean" };
  return { type: "text" };
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
                const classified = classifyQuestion(q);
                return { id: `q${i}`, question: q, type: classified.type, options: classified.options };
              }
              const item = q as Record<string, unknown>;
              const text = (item.question as string) || "";
              const classified = classifyQuestion(text);
              return {
                id: (item.id as string) || `q${i}`,
                question: text,
                type: Array.isArray(item.options) ? "select" as const : classified.type,
                options: Array.isArray(item.options) ? (item.options as string[]) : classified.options,
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
          ) : q.type === "date" ? (
            <Input
              type="date"
              value={answers[q.id] || ""}
              onChange={(e) => setAnswers({ ...answers, [q.id]: e.target.value })}
              className="max-w-[200px]"
            />
          ) : q.type === "select" && q.options ? (
            <Select
              value={answers[q.id] || ""}
              onValueChange={(val) => setAnswers({ ...answers, [q.id]: val })}
            >
              <SelectTrigger className="max-w-sm">
                <SelectValue placeholder="Select…" />
              </SelectTrigger>
              <SelectContent>
                {q.options.map((opt) => (
                  <SelectItem key={opt} value={opt}>{opt}</SelectItem>
                ))}
              </SelectContent>
            </Select>
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

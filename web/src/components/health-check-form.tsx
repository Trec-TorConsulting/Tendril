"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { getGrowType } from "@/lib/api";
import { Button } from "@/components/ui/button";

interface HealthCheckFormProps {
  growType: string;
  onSubmit: (answers: Record<string, string>) => void;
}

interface HealthQuestion {
  id: string;
  question: string;
  options: string[];
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
              const item = q as Record<string, unknown>;
              return {
                id: (item.id as string) || `q${i}`,
                question: (item.question as string) || "",
                options: Array.isArray(item.options) ? (item.options as string[]) : ["Yes", "No"],
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
    return <p className="text-sm text-neutral-500">No health check available for this grow type.</p>;
  }

  return (
    <div className="space-y-4">
      {questions.map((q) => (
        <div key={q.id}>
          <p className="mb-2 text-sm text-white">{q.question}</p>
          <div className="flex flex-wrap gap-2">
            {q.options.map((opt) => (
              <button
                key={opt}
                type="button"
                className={`rounded border px-3 py-1 text-sm ${
                  answers[q.id] === opt
                    ? "border-green-600 bg-green-900/30 text-green-400"
                    : "border-neutral-700 bg-neutral-800 text-neutral-300 hover:border-neutral-600"
                }`}
                onClick={() => setAnswers({ ...answers, [q.id]: opt })}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      ))}
      <Button
        size="sm"
        onClick={() => onSubmit(answers)}
        disabled={Object.keys(answers).length < questions.length}
      >
        Submit Health Check
      </Button>
    </div>
  );
}

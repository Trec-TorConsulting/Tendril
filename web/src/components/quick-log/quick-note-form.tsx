"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useGrow } from "@/hooks/use-grow";
import { getAccessToken } from "@/lib/auth";
import { quickLogNote } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

interface QuickNoteFormProps {
  onSuccess: () => void;
}

const QUICK_TAGS = [
  "topped",
  "transplanted",
  "defoliated",
  "flush",
  "pest",
  "deficiency",
  "training",
  "harvest",
  "observation",
];

export function QuickNoteForm({ onSuccess }: QuickNoteFormProps) {
  const { selectedGrow } = useGrow();
  const [content, setContent] = useState("");
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag],
    );
  };

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim()) {
      toast.error("Enter a note");
      return;
    }

    const token = getAccessToken();
    if (!token) return;

    setSubmitting(true);
    try {
      await quickLogNote(token, {
        grow_cycle_id: selectedGrow?.id,
        tags: selectedTags.length > 0 ? selectedTags : undefined,
        content: content.trim(),
      });
      toast.success("Note saved");
      onSuccess();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to save note");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Quick tags */}
      <div className="space-y-2">
        <Label className="text-xs">Quick Tags</Label>
        <div className="flex flex-wrap gap-2">
          {QUICK_TAGS.map((tag) => (
            <button
              key={tag}
              type="button"
              onClick={() => toggleTag(tag)}
              className={cn(
                "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                selectedTags.includes(tag)
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border text-muted-foreground hover:border-primary/50",
              )}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* Note content */}
      <div className="space-y-1">
        <Label htmlFor="qn-content" className="text-xs">Note</Label>
        <Textarea
          id="qn-content"
          placeholder="What happened today..."
          rows={4}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          autoFocus
        />
      </div>

      <Button type="submit" className="w-full" disabled={submitting || !content.trim()}>
        {submitting ? <Loader2 className="size-4 animate-spin mr-2" /> : null}
        Save Note
      </Button>
    </form>
  );
}

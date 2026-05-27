"use client";

import { useState, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useGrow } from "@/hooks/use-grow";
import { getAccessToken } from "@/lib/auth";
import { uploadGrowPhoto, listBuckets, type BucketResponse } from "@/lib/api";
import { Camera, Upload, Loader2, Check, ImagePlus } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { useEffect } from "react";

interface QuickPhotoCaptureProps {
  onSuccess: () => void;
}

export function QuickPhotoCapture({ onSuccess }: QuickPhotoCaptureProps) {
  const { activeGrow } = useGrow();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [buckets, setBuckets] = useState<BucketResponse[]>([]);
  const [selectedBucket, setSelectedBucket] = useState<string>("");
  const [caption, setCaption] = useState("");
  const [preview, setPreview] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    async function loadBuckets() {
      const token = getAccessToken();
      if (!token || !activeGrow) return;
      try {
        const b = await listBuckets(token, activeGrow.id);
        setBuckets(b);
      } catch {
        // non-critical
      }
    }
    loadBuckets();
  }, [activeGrow]);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    setFile(selected);
    const reader = new FileReader();
    reader.onload = () => setPreview(reader.result as string);
    reader.readAsDataURL(selected);
  }, []);

  const handleCapture = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!file || !activeGrow) return;
    const token = getAccessToken();
    if (!token) return;

    setSubmitting(true);
    try {
      await uploadGrowPhoto(
        token,
        file,
        activeGrow.id,
        selectedBucket || undefined,
        caption || undefined,
      );
      setSubmitted(true);
      toast.success("Photo uploaded");
      setTimeout(onSuccess, 600);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setSubmitting(false);
    }
  }, [file, activeGrow, selectedBucket, caption, onSuccess]);

  if (submitted) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-12">
        <div className="rounded-full bg-green-100 p-3 dark:bg-green-900/30">
          <Check className="size-6 text-green-600 dark:text-green-400" />
        </div>
        <p className="text-sm text-muted-foreground">Photo uploaded</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Hidden file input with camera capture */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Preview / Capture area */}
      {preview ? (
        <div className="relative overflow-hidden rounded-lg border">
          <img
            src={preview}
            alt="Preview"
            className="aspect-video w-full object-cover"
          />
          <Button
            variant="secondary"
            size="sm"
            className="absolute bottom-2 right-2"
            onClick={handleCapture}
          >
            Retake
          </Button>
        </div>
      ) : (
        <button
          onClick={handleCapture}
          className={cn(
            "flex aspect-video w-full flex-col items-center justify-center gap-3",
            "rounded-lg border-2 border-dashed border-muted-foreground/25",
            "transition-colors hover:border-primary/50 hover:bg-muted/50",
          )}
        >
          <div className="rounded-full bg-muted p-4">
            <Camera className="size-8 text-muted-foreground" />
          </div>
          <div className="text-center">
            <p className="text-sm font-medium">Take a photo</p>
            <p className="text-xs text-muted-foreground">or choose from gallery</p>
          </div>
        </button>
      )}

      {/* Bucket selector */}
      {buckets.length > 0 && (
        <div className="space-y-1.5">
          <Label className="text-xs">Tag to bucket (optional)</Label>
          <Select value={selectedBucket} onValueChange={setSelectedBucket}>
            <SelectTrigger>
              <SelectValue placeholder="All / No specific bucket" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">None</SelectItem>
              {buckets.map((b) => (
                <SelectItem key={b.id} value={b.id}>
                  {b.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      {/* Caption */}
      <div className="space-y-1.5">
        <Label className="text-xs">Caption (optional)</Label>
        <Input
          placeholder="e.g. Day 21 flower, trichomes forming"
          value={caption}
          onChange={(e) => setCaption(e.target.value)}
        />
      </div>

      {/* Submit */}
      <Button
        onClick={handleSubmit}
        disabled={!file || !activeGrow || submitting}
        className="w-full gap-2"
      >
        {submitting ? (
          <Loader2 className="size-4 animate-spin" />
        ) : (
          <Upload className="size-4" />
        )}
        Upload Photo
      </Button>

      {!activeGrow && (
        <p className="text-xs text-center text-destructive">
          Select a grow first to upload photos
        </p>
      )}
    </div>
  );
}

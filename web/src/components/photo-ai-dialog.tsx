"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  diagnosePlant,
  identifyPlant,
  type DiagnoseResult,
  type IdentifyResult,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Camera, Upload, Loader2, Stethoscope, Search, AlertTriangle, CheckCircle2, XCircle, Info } from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface PhotoAIDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  growId?: string;
  initialMode?: "diagnose" | "identify";
  onPhotoSaved?: () => void;
}

const SEVERITY_CONFIG = {
  low: { color: "bg-blue-500/10 text-blue-500 border-blue-500/30", icon: Info },
  medium: { color: "bg-yellow-500/10 text-yellow-500 border-yellow-500/30", icon: AlertTriangle },
  high: { color: "bg-orange-500/10 text-orange-500 border-orange-500/30", icon: AlertTriangle },
  critical: { color: "bg-red-500/10 text-red-500 border-red-500/30", icon: XCircle },
};

export function PhotoAIDialog({ open, onOpenChange, growId, initialMode, onPhotoSaved }: PhotoAIDialogProps) {
  const [mode, setMode] = useState<"diagnose" | "identify">(initialMode ?? "diagnose");

  useEffect(() => {
    if (open && initialMode) setMode(initialMode);
  }, [open, initialMode]);
  const [imageBase64, setImageBase64] = useState<string>("");
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [observations, setObservations] = useState("");
  const [loading, setLoading] = useState(false);
  const [diagnosisResult, setDiagnosisResult] = useState<DiagnoseResult | null>(null);
  const [identifyResult, setIdentifyResult] = useState<IdentifyResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const streamRef = useRef<MediaStream | null>(null);

  const reset = useCallback(() => {
    setImageBase64("");
    setPreviewUrl("");
    setObservations("");
    setDiagnosisResult(null);
    setIdentifyResult(null);
    stopCamera();
  }, []);

  const handleOpenChange = (val: boolean) => {
    if (!val) reset();
    onOpenChange(val);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.match(/^image\/(jpeg|png|webp)$/)) {
      toast.error("Only JPEG, PNG, and WebP images are allowed");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      toast.error("Image must be under 10 MB");
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setPreviewUrl(dataUrl);
      // Extract base64 (remove data:image/...;base64, prefix)
      setImageBase64(dataUrl.split(",")[1]);
      setDiagnosisResult(null);
      setIdentifyResult(null);
    };
    reader.readAsDataURL(file);
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1920 }, height: { ideal: 1080 } },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setCameraActive(true);
    } catch {
      toast.error("Camera access denied or unavailable");
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.drawImage(videoRef.current, 0, 0);
    const dataUrl = canvas.toDataURL("image/jpeg", 0.9);
    setPreviewUrl(dataUrl);
    setImageBase64(dataUrl.split(",")[1]);
    setDiagnosisResult(null);
    setIdentifyResult(null);
    stopCamera();
  };

  const runDiagnosis = async () => {
    const token = getAccessToken();
    if (!token || !imageBase64) return;
    setLoading(true);
    try {
      const result = await diagnosePlant(token, {
        image_base64: imageBase64,
        grow_id: growId,
        observations: observations || undefined,
      });
      setDiagnosisResult(result);
      if (onPhotoSaved) onPhotoSaved();
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Diagnosis failed");
    }
    setLoading(false);
  };

  const runIdentification = async () => {
    const token = getAccessToken();
    if (!token || !imageBase64) return;
    setLoading(true);
    try {
      const result = await identifyPlant(token, { image_base64: imageBase64 });
      setIdentifyResult(result);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Identification failed");
    }
    setLoading(false);
  };

  const handleAnalyze = () => {
    if (mode === "diagnose") runDiagnosis();
    else runIdentification();
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90dvh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Stethoscope className="size-5 text-primary" />
            Plant AI Analysis
          </DialogTitle>
        </DialogHeader>

        <Tabs value={mode} onValueChange={(v) => { setMode(v as "diagnose" | "identify"); setDiagnosisResult(null); setIdentifyResult(null); }}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="diagnose" className="gap-1.5">
              <Stethoscope className="size-3.5" />
              Health Diagnosis
            </TabsTrigger>
            <TabsTrigger value="identify" className="gap-1.5">
              <Search className="size-3.5" />
              Identify Plant
            </TabsTrigger>
          </TabsList>

          <div className="mt-4 space-y-4">
            {/* Image Capture / Upload */}
            {!previewUrl && !cameraActive && (
              <div className="grid gap-3 sm:grid-cols-2">
                <Button variant="outline" className="h-24 flex-col gap-2" onClick={() => fileInputRef.current?.click()}>
                  <Upload className="size-6" />
                  <span className="text-sm">Upload Photo</span>
                </Button>
                <Button variant="outline" className="h-24 flex-col gap-2" onClick={startCamera}>
                  <Camera className="size-6" />
                  <span className="text-sm">Take Photo</span>
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  className="hidden"
                  onChange={handleFileSelect}
                />
              </div>
            )}

            {/* Camera Preview */}
            {cameraActive && (
              <div className="relative">
                <video ref={videoRef} className="w-full rounded-lg" autoPlay playsInline muted />
                <div className="mt-3 flex gap-2 justify-center">
                  <Button onClick={capturePhoto}>Capture</Button>
                  <Button variant="outline" onClick={stopCamera}>Cancel</Button>
                </div>
              </div>
            )}

            {/* Image Preview */}
            {previewUrl && !cameraActive && (
              <div className="relative">
                <img src={previewUrl} alt="Plant photo" className="w-full max-h-64 object-contain rounded-lg bg-muted" />
                <Button
                  variant="secondary"
                  size="sm"
                  className="absolute top-2 right-2"
                  onClick={() => { setPreviewUrl(""); setImageBase64(""); setDiagnosisResult(null); setIdentifyResult(null); }}
                >
                  Change
                </Button>
              </div>
            )}

            {/* Observations (diagnose mode only) */}
            <TabsContent value="diagnose" className="mt-0">
              {previewUrl && !diagnosisResult && (
                <Textarea
                  placeholder="Optional: Describe what you're seeing (yellowing leaves, spots, drooping, etc.)"
                  value={observations}
                  onChange={(e) => setObservations(e.target.value)}
                  rows={2}
                />
              )}
            </TabsContent>
            <TabsContent value="identify" className="mt-0" />

            {/* Analyze Button */}
            {previewUrl && !diagnosisResult && !identifyResult && (
              <Button
                className="w-full"
                onClick={handleAnalyze}
                disabled={loading || !imageBase64}
              >
                {loading ? (
                  <><Loader2 className="mr-2 size-4 animate-spin" /> Analyzing...</>
                ) : mode === "diagnose" ? (
                  <><Stethoscope className="mr-2 size-4" /> Diagnose Plant Health</>
                ) : (
                  <><Search className="mr-2 size-4" /> Identify Plant</>
                )}
              </Button>
            )}

            {/* Diagnosis Results */}
            {diagnosisResult && (
              <div className="space-y-4">
                {/* Score + Summary */}
                <Card>
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-4">
                      <div className={cn(
                        "flex size-14 items-center justify-center rounded-full text-lg font-bold",
                        diagnosisResult.overall_score >= 80 ? "bg-green-500/10 text-green-500" :
                        diagnosisResult.overall_score >= 60 ? "bg-yellow-500/10 text-yellow-500" :
                        diagnosisResult.overall_score >= 40 ? "bg-orange-500/10 text-orange-500" :
                        "bg-red-500/10 text-red-500",
                      )}>
                        {diagnosisResult.overall_score}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium">Health Score</p>
                        <p className="text-sm text-muted-foreground">{diagnosisResult.summary}</p>
                      </div>
                    </div>
                    {diagnosisResult.grow_stage_assessment && (
                      <p className="mt-3 text-xs text-muted-foreground border-t pt-2">
                        Stage: {diagnosisResult.grow_stage_assessment}
                      </p>
                    )}
                  </CardContent>
                </Card>

                {/* Issues */}
                {diagnosisResult.issues.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Issues Detected</h4>
                    {diagnosisResult.issues.map((issue, i) => {
                      const config = SEVERITY_CONFIG[issue.severity] || SEVERITY_CONFIG.low;
                      const Icon = config.icon;
                      return (
                        <Card key={i} className={cn("border", config.color.split(" ").find(c => c.startsWith("border-")))}>
                          <CardContent className="py-3 space-y-1">
                            <div className="flex items-center gap-2">
                              <Icon className="size-4 shrink-0" />
                              <span className="font-medium text-sm">{issue.name}</span>
                              <Badge variant="outline" className={cn("text-[10px] ml-auto", config.color)}>
                                {issue.severity} • {Math.round(issue.confidence * 100)}%
                              </Badge>
                            </div>
                            <p className="text-xs text-muted-foreground">{issue.description}</p>
                            <p className="text-xs font-medium text-primary">Treatment: {issue.treatment}</p>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                )}

                {/* Actions */}
                {diagnosisResult.actions.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Recommended Actions</h4>
                    <ul className="space-y-1">
                      {diagnosisResult.actions.map((action, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm">
                          <CheckCircle2 className="size-4 mt-0.5 shrink-0 text-primary" />
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* No issues */}
                {diagnosisResult.issues.length === 0 && diagnosisResult.overall_score >= 80 && (
                  <div className="text-center py-4">
                    <CheckCircle2 className="mx-auto size-8 text-green-500 mb-2" />
                    <p className="text-sm font-medium text-green-500">Plant looks healthy!</p>
                  </div>
                )}

                <Button variant="outline" className="w-full" onClick={reset}>
                  Analyze Another Photo
                </Button>
              </div>
            )}

            {/* Identification Results */}
            {identifyResult && (
              <div className="space-y-4">
                <Card>
                  <CardContent className="pt-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-bold text-lg">{identifyResult.plant_type}</p>
                        {identifyResult.species && <p className="text-sm text-muted-foreground italic">{identifyResult.species}</p>}
                      </div>
                      <Badge variant={identifyResult.confidence >= 0.8 ? "default" : "secondary"}>
                        {Math.round(identifyResult.confidence * 100)}% confident
                      </Badge>
                    </div>

                    {identifyResult.indica_sativa_ratio && (
                      <div className="border-t pt-2">
                        <p className="text-xs text-muted-foreground">Indica/Sativa</p>
                        <p className="text-sm font-medium">{identifyResult.indica_sativa_ratio}</p>
                      </div>
                    )}

                    {identifyResult.growth_stage && (
                      <div className="border-t pt-2">
                        <p className="text-xs text-muted-foreground">Growth Stage</p>
                        <p className="text-sm font-medium capitalize">{identifyResult.growth_stage.replace(/_/g, " ")}</p>
                      </div>
                    )}

                    {identifyResult.strain_guess && (
                      <div className="border-t pt-2">
                        <p className="text-xs text-muted-foreground">Possible Strain / Lineage</p>
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium">{identifyResult.strain_guess}</p>
                          {identifyResult.strain_confidence != null && (
                            <Badge variant="secondary" className="text-[10px]">
                              {Math.round(identifyResult.strain_confidence * 100)}% confidence
                            </Badge>
                          )}
                        </div>
                        <p className="text-[10px] text-muted-foreground mt-0.5">
                          Note: Visual strain identification is unreliable. Use this as a rough guide only.
                        </p>
                      </div>
                    )}

                    {identifyResult.characteristics.length > 0 && (
                      <div className="border-t pt-2">
                        <p className="text-xs text-muted-foreground mb-1">Observed Characteristics</p>
                        <div className="flex flex-wrap gap-1.5">
                          {identifyResult.characteristics.map((c, i) => (
                            <Badge key={i} variant="outline" className="text-xs">{c}</Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {identifyResult.notes && (
                      <div className="border-t pt-2">
                        <p className="text-xs text-muted-foreground">Notes</p>
                        <p className="text-sm">{identifyResult.notes}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Button variant="outline" className="w-full" onClick={reset}>
                  Analyze Another Photo
                </Button>
              </div>
            )}
          </div>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

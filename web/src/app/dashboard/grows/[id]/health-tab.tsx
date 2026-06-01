"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import {
  runHealthCheck,
  getHealthCheckHistory,
  deleteHealthCheck,
  updateGrow,
  getTent,
  getCoachTip,
  getGrowReportUrl,
  listTentCameras,
  type HealthCheckResult,
  type GrowResponse,
  type TentResponse,
} from "@/lib/api";
import { HealthCheckForm } from "@/components/health-check-form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { Heart, AlertTriangle, CheckCircle2, Loader2, History, Clock, Camera, Upload, X, Lightbulb, FileText, Download, RefreshCw, Calendar as CalendarIcon, Trash2 } from "lucide-react";
import { cn, formatDateTime } from "@/lib/utils";

function ScoreBadge({ score }: { score: number | null }) {
  if (score == null) return <span className="text-muted-foreground">N/A</span>;
  return (
    <span
      className={cn(
        "text-2xl font-bold",
        score >= 80 ? "text-primary" : score >= 50 ? "text-yellow-500" : "text-destructive",
      )}
    >
      {score}
    </span>
  );
}

function ResultCards({ result }: { result: HealthCheckResult }) {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Health Score</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-baseline gap-2">
            <span
              className={cn(
                "text-4xl font-bold",
                (result.score ?? 0) >= 80
                  ? "text-primary"
                  : (result.score ?? 0) >= 50
                    ? "text-yellow-500"
                    : "text-destructive",
              )}
            >
              {result.score ?? "N/A"}
            </span>
            <span className="text-muted-foreground">/ 100</span>
          </div>
          {result.photo_url && (
            <img
              src={result.photo_url}
              alt="Health check photo"
              className="mt-3 w-full rounded-lg object-cover"
            />
          )}
          {result.source === "scheduled" && (
            <p className="mt-1 text-xs text-muted-foreground">Auto check</p>
          )}
        </CardContent>
      </Card>

      {result.issues.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <AlertTriangle className="size-4 text-destructive" />
              Issues Found
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {result.issues.map((issue, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <Badge variant="destructive" className="mt-0.5 size-1.5 rounded-full p-0" />
                  {issue}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {result.actions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <CheckCircle2 className="size-4 text-primary" />
              Recommended Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {result.actions.map((action, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary" />
                  {action}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

interface HealthTabProps {
  grow: GrowResponse;
  onRefresh: () => void;
}

export function HealthTab({ grow, onRefresh }: HealthTabProps) {
  const [tent, setTent] = useState<TentResponse | null>(null);
  const [result, setResult] = useState<HealthCheckResult | null>(null);
  const [history, setHistory] = useState<HealthCheckResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [includeCamera, setIncludeCamera] = useState(true);
  const [hasCamera, setHasCamera] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [autoCheck, setAutoCheck] = useState(grow.auto_health_check);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // AI Coach
  const [coachTip, setCoachTip] = useState<string | null>(null);
  const [coachLoading, setCoachLoading] = useState(false);

  const COACH_CACHE_KEY = `tendril_coach_tip_${grow.id}`;
  const COACH_TTL = 60 * 60 * 1000; // 1 hour

  const fetchAndCacheCoachTip = useCallback(async () => {
    const token = getAccessToken();
    if (!token) return;
    setCoachLoading(true);
    try {
      const res = await getCoachTip(token, grow.id);
      const tip = typeof res.tip === "string" ? res.tip : String(res.tip ?? "");
      setCoachTip(tip);
      localStorage.setItem(COACH_CACHE_KEY, JSON.stringify({ tip, ts: Date.now() }));
    } catch (e) {
      setCoachTip(`⚠️ ${e instanceof Error ? e.message : "Unable to get tip. Try again."}`);
    } finally { setCoachLoading(false); }
  }, [grow.id, COACH_CACHE_KEY]);

  // Load cached tip on mount or fetch if stale/missing
  useEffect(() => {
    const cached = localStorage.getItem(COACH_CACHE_KEY);
    if (cached) {
      try {
        const { tip, ts } = JSON.parse(cached);
        if (typeof tip === "string" && Date.now() - ts < COACH_TTL) {
          setCoachTip(tip);
          return;
        }
      } catch { /* invalid cache, refetch */ }
      // Clear corrupt/stale cache
      localStorage.removeItem(COACH_CACHE_KEY);
    }
    fetchAndCacheCoachTip();
  }, [grow.id, COACH_CACHE_KEY, COACH_TTL, fetchAndCacheCoachTip]);

  // Auto-refresh every hour
  useEffect(() => {
    const interval = setInterval(() => { fetchAndCacheCoachTip(); }, COACH_TTL);
    return () => clearInterval(interval);
  }, [COACH_TTL, fetchAndCacheCoachTip]);

  useEffect(() => {
    setResult(null);
    setHistory([]);
    setTent(null);
    setAutoCheck(grow.auto_health_check);
    const load = async () => {
      const token = getAccessToken();
      if (!token) return;
      try {
        const [tentData, historyData] = await Promise.all([
          getTent(token, grow.tent_id),
          getHealthCheckHistory(token, grow.id, 10),
        ]);
        setTent(tentData);
        setHistory(historyData.items);
        // Check for cameras (new TentCamera records OR legacy camera_url)
        const cameras = await listTentCameras(token, grow.tent_id).catch(() => []);
        const cameraAvailable = cameras.length > 0 || !!tentData.camera_url;
        setHasCamera(cameraAvailable);
        setIncludeCamera(cameraAvailable);
      } catch {
        setTent(null);
        setHistory([]);
      }
    };
    load();
  }, [grow.id, grow.tent_id, grow.auto_health_check]);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setImagePreview(dataUrl);
      const base64 = dataUrl.split(",")[1];
      setUploadedImage(base64);
    };
    reader.readAsDataURL(file);
  };

  const clearImage = () => {
    setUploadedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = useCallback(
    async (observations: Record<string, string>) => {
      const token = getAccessToken();
      if (!token) return;

      setLoading(true);
      setError("");
      setResult(null);

      try {
        const res = await runHealthCheck(token, {
          grow_id: grow.id,
          observations,
          include_camera: includeCamera && hasCamera,
          image_base64: uploadedImage || undefined,
        });
        setResult(res);
        const hist = await getHealthCheckHistory(token, grow.id, 10);
        setHistory(hist.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Health check failed");
      } finally {
        setLoading(false);
      }
    },
    [grow.id, includeCamera, tent, uploadedImage],
  );

  const toggleAutoCheck = async () => {
    const token = getAccessToken();
    if (!token) return;
    const newVal = !autoCheck;
    try {
      await updateGrow(token, grow.id, { auto_health_check: newVal });
      setAutoCheck(newVal);
      onRefresh();
    } catch {
      // Ignore
    }
  };

  const loadCoachTip = () => { fetchAndCacheCoachTip(); };



  const downloadReport = () => {
    const token = getAccessToken();
    if (!token) return;
    const url = getGrowReportUrl(token, grow.id);
    window.open(url, "_blank");
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Auto-check toggle + Report download */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Switch checked={autoCheck} onCheckedChange={toggleAutoCheck} />
          <div>
            <Label className="text-sm">Auto Health Check</Label>
            <p className="text-xs text-muted-foreground">
              Run AI health checks every 12 hours automatically
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={downloadReport}>
          <Download className="mr-1 size-4" /> PDF Report
        </Button>
      </div>

      {/* AI Coach Tip */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-sm font-medium">
              <Lightbulb className="size-4 text-amber-500" /> Coach Tip
            </CardTitle>
            <Button variant="outline" size="sm" className="h-7 text-xs" onClick={loadCoachTip} disabled={coachLoading}>
              {coachLoading ? <Loader2 className="size-3 animate-spin" /> : <RefreshCw className="size-3" />}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {coachLoading ? (
            <p className="text-sm text-muted-foreground">Getting tip...</p>
          ) : coachTip ? (
            <p className="text-sm">{coachTip}</p>
          ) : (
            <p className="text-sm text-muted-foreground">Loading your personalized growing tip...</p>
          )}
        </CardContent>
      </Card>

      {/* Observations form + image options */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Observations</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Camera + image section */}
          <div className="flex flex-wrap items-start gap-4 rounded-lg border p-3">
            {hasCamera && (
              <div className="flex items-center gap-3">
                <Camera className="size-4 text-muted-foreground" />
                <div className="flex items-center gap-2">
                  <Switch
                    checked={includeCamera}
                    onCheckedChange={setIncludeCamera}
                  />
                  <div>
                    <Label className="text-sm">Include Camera Snapshot</Label>
                    <p className="text-xs text-muted-foreground">
                      Live image from {tent.name} camera
                    </p>
                  </div>
                </div>
              </div>
            )}
            <div className="flex items-start gap-3">
              <Upload className="mt-1 size-4 text-muted-foreground" />
              <div>
                <Label className="mb-1 block text-sm">Upload Photo</Label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="text-xs file:mr-2 file:rounded file:border-0 file:bg-primary/10 file:px-2 file:py-1 file:text-xs file:text-primary"
                />
                {imagePreview && (
                  <div className="mt-2 flex items-start gap-2">
                    <img
                      src={imagePreview}
                      alt="Upload preview"
                      className="size-16 rounded object-cover"
                    />
                    <button onClick={clearImage} className="text-muted-foreground hover:text-destructive">
                      <X className="size-4" />
                    </button>
                  </div>
                )}
              </div>
            </div>
            {!hasCamera && !uploadedImage && (
              <p className="text-xs text-muted-foreground">
                No camera configured. Upload a photo for visual analysis.
              </p>
            )}
          </div>

          <HealthCheckForm growType={grow.grow_type} onSubmit={handleSubmit} />
          {loading && (
            <div className="mt-3 flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="size-4 animate-spin" />
              Running health check…
              {(includeCamera && hasCamera) && (
                <Badge variant="secondary" className="text-xs">
                  <Camera className="mr-1 size-3" />
                  Camera
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Latest result */}
      {result && <ResultCards result={result} />}

      {/* History */}
      {history.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <History className="size-4" />
              Health Check History
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {history.map((eval_item, i) => (
                <details
                  key={eval_item.id || i}
                  className="rounded-lg border"
                  open={i === 0 && !result}
                >
                  <summary className="flex cursor-pointer items-center gap-3 p-3 hover:bg-muted/50">
                    <ScoreBadge score={eval_item.score} />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">/100</span>
                        {eval_item.source === "scheduled" && (
                          <Badge variant="secondary" className="text-xs">
                            <Clock className="mr-1 size-3" />
                            Auto
                          </Badge>
                        )}
                      </div>
                      {eval_item.created_at && (
                        <p className="text-xs text-muted-foreground">
                          {formatDateTime(eval_item.created_at)}
                        </p>
                      )}
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {eval_item.issues.length} issue{eval_item.issues.length !== 1 ? "s" : ""}
                    </span>
                    {eval_item.id && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 text-muted-foreground hover:text-destructive"
                        onClick={async (e) => {
                          e.stopPropagation();
                          const token = getAccessToken();
                          if (!token || !eval_item.id) return;
                          await deleteHealthCheck(token, eval_item.id);
                          setHistory((h) => h.filter((x) => x.id !== eval_item.id));
                        }}
                      >
                        <Trash2 className="size-3" />
                      </Button>
                    )}
                  </summary>
                  <div className="border-t p-3">
                    {eval_item.photo_url && (
                      <img
                        src={eval_item.photo_url}
                        alt="Health check photo"
                        className="mb-3 h-40 w-full rounded-lg object-cover"
                      />
                    )}
                    {eval_item.issues.length > 0 && (
                      <div className="mb-3">
                        <p className="mb-1 text-xs font-medium text-destructive">Issues</p>
                        <ul className="space-y-1">
                          {eval_item.issues.map((issue, j) => (
                            <li key={j} className="text-sm">• {issue}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {eval_item.actions.length > 0 && (
                      <div>
                        <p className="mb-1 text-xs font-medium text-primary">Actions</p>
                        <ul className="space-y-1">
                          {eval_item.actions.map((action, j) => (
                            <li key={j} className="text-sm">• {action}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </details>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

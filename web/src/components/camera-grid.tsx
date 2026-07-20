"use client";

import { useState, useEffect, useCallback } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { listTents, listTentCameras, getCameraSnapshot, type TentResponse, type CameraResponse } from "@/lib/api";
import { useApiSWR } from "@/lib/swr";
import { getAccessToken } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { VisionScanPanel } from "@/components/vision/vision-scan-panel";
import { RefreshCw, Maximize2, Camera, Loader2, ScanSearch } from "lucide-react";

interface CameraGridProps {
  tentId?: string;
  hideEmpty?: boolean;
}

interface CameraWithSnapshot {
  camera: CameraResponse;
  tent: TentResponse;
  imageBase64?: string;
  loading: boolean;
  error?: string;
}

export function CameraGrid({ tentId, hideEmpty }: CameraGridProps) {
  const [cameras, setCameras] = useState<CameraWithSnapshot[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<CameraWithSnapshot | null>(null);
  const [scanMode, setScanMode] = useState(false);
  const {
    data: cameraData,
    isLoading: loading,
  } = useApiSWR<CameraWithSnapshot[]>(
    ["camera-grid", tentId ?? "all"],
    async (token) => {
      const tents = tentId
        ? [{ id: tentId, name: "" } as TentResponse]
        : await listTents(token);

      const allCameras: CameraWithSnapshot[] = [];
      for (const tent of tents) {
        try {
          const tentCameras = await listTentCameras(token, tent.id);
          for (const cam of tentCameras) {
            allCameras.push({ camera: cam, tent, loading: false });
          }
        } catch {
          // tent may not have cameras
        }
      }
      return allCameras;
    },
  );

  useEffect(() => {
    setCameras(cameraData ?? []);
  }, [cameraData]);

  const refreshCamera = useCallback(async (index: number) => {
    const token = getAccessToken();
    if (!token) return;

    setCameras((prev) => prev.map((c, i) => i === index ? { ...c, loading: true, error: undefined } : c));
    try {
      const { image_base64 } = await getCameraSnapshot(token, cameras[index].camera.tent_id, cameras[index].camera.id);
      setCameras((prev) => prev.map((c, i) => i === index ? { ...c, imageBase64: image_base64, loading: false } : c));
    } catch {
      // API proxy failed (503 = camera unreachable from server).
      // Try fetching directly from the camera URL (works when user is on same LAN).
      try {
        const directUrl = cameras[index].camera.url;
        if (directUrl && cameras[index].camera.camera_type === "http_snapshot") {
          const resp = await fetch(directUrl, { mode: "cors", signal: AbortSignal.timeout(10_000) });
          if (resp.ok) {
            const blob = await resp.blob();
            const reader = new FileReader();
            const b64 = await new Promise<string>((resolve, reject) => {
              reader.onloadend = () => resolve((reader.result as string).split(",")[1]);
              reader.onerror = reject;
              reader.readAsDataURL(blob);
            });
            setCameras((prev) => prev.map((c, i) => i === index ? { ...c, imageBase64: b64, loading: false } : c));
            return;
          }
        }
      } catch {
        // Direct fetch also failed
      }
      setCameras((prev) => prev.map((c, i) => i === index ? { ...c, loading: false, error: "Camera unreachable" } : c));
    }
  }, [cameras]);

  // Load snapshots on mount and auto-retry every 30s for cameras without an image
  useEffect(() => {
    cameras.forEach((cam, i) => {
      if (!cam.imageBase64 && !cam.loading && !cam.error) {
        refreshCamera(i);
      }
    });
  }, [cameras.length]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (cameras.length === 0) return;
    const interval = setInterval(() => {
      cameras.forEach((cam, i) => {
        if (!cam.imageBase64 && !cam.loading) {
          refreshCamera(i);
        }
      });
    }, 30_000);
    return () => clearInterval(interval);
  }, [cameras.length, refreshCamera]);

  if (loading) {
    if (hideEmpty) return null;
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="size-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (cameras.length === 0) {
    if (hideEmpty) return null;
    return (
      <div className="flex flex-col items-center justify-center gap-3 p-8 text-center">
        <Camera className="size-10 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">No cameras configured</p>
        <p className="text-xs text-muted-foreground">Add cameras in Grow Space settings</p>
      </div>
    );
  }

  // Full-screen view
  if (selectedCamera) {
    const snapshotUri = selectedCamera.imageBase64
      ? `data:image/jpeg;base64,${selectedCamera.imageBase64}`
      : null;
    return (
      <div className="fixed inset-0 z-50 bg-black flex flex-col">
        <div className="flex items-center justify-between p-4">
          <div>
            <p className="text-white font-medium">{selectedCamera.camera.label}</p>
            <p className="text-white/60 text-sm">{selectedCamera.tent.name}</p>
          </div>
          <div className="flex items-center gap-2">
            {snapshotUri && (
              <Button
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/10"
                onClick={() => setScanMode((s) => !s)}
              >
                <ScanSearch className="size-4" />
                {scanMode ? "Hide scan" : "Scan"}
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="text-white hover:bg-white/10"
              onClick={() => {
                setSelectedCamera(null);
                setScanMode(false);
              }}
            >
              Close
            </Button>
          </div>
        </div>
        <div className="flex-1 overflow-auto flex items-start justify-center p-4">
          {snapshotUri ? (
            scanMode ? (
              <div className="w-full max-w-3xl rounded-lg bg-background p-4 text-foreground">
                <VisionScanPanel
                  source="tent"
                  sourceId={selectedCamera.camera.tent_id}
                  imageSrc={snapshotUri}
                />
              </div>
            ) : (
              <img
                src={snapshotUri}
                alt={selectedCamera.camera.label}
                className="max-w-full max-h-full object-contain rounded-lg"
              />
            )
          ) : (
            <div className="text-white/60">No image available</div>
          )}
        </div>
      </div>
    );
  }

  // Grid view
  const gridCols = cameras.length <= 2 ? "grid-cols-1 sm:grid-cols-2" :
                   cameras.length <= 4 ? "grid-cols-2" : "grid-cols-2 sm:grid-cols-3";

  return (
    <div className={cn("grid gap-3", gridCols)}>
      {cameras.map((cam, i) => (
        <Card key={cam.camera.id} className="overflow-hidden">
          <CardContent className="p-0">
            <div className="relative aspect-video bg-muted">
              {cam.loading ? (
                <div className="absolute inset-0 flex items-center justify-center">
                  <Loader2 className="size-5 animate-spin text-muted-foreground" />
                </div>
              ) : cam.imageBase64 ? (
                <img
                  src={`data:image/jpeg;base64,${cam.imageBase64}`}
                  alt={cam.camera.label}
                  className="w-full h-full object-cover"
                />
              ) : cam.error ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 p-3">
                  <Camera className="size-6 text-muted-foreground/50" />
                  <p className="text-[10px] text-muted-foreground text-center">{cam.error}</p>
                  <Button variant="ghost" size="sm" className="h-6 text-[10px] gap-1" onClick={() => refreshCamera(i)}>
                    <RefreshCw className="size-3" /> Retry
                  </Button>
                </div>
              ) : (
                <div className="absolute inset-0 flex items-center justify-center">
                  <Camera className="size-8 text-muted-foreground/30" />
                </div>
              )}
              {/* Overlay controls */}
              <div className="absolute top-2 right-2 flex gap-1">
                <button
                  onClick={() => refreshCamera(i)}
                  className="rounded-full bg-black/50 p-1.5 text-white hover:bg-black/70 transition-colors"
                >
                  <RefreshCw className="size-3" />
                </button>
                {cam.imageBase64 && (
                  <button
                    onClick={() => {
                      setSelectedCamera(cam);
                      setScanMode(true);
                    }}
                    aria-label="Scan for issues"
                    className="rounded-full bg-black/50 p-1.5 text-white hover:bg-black/70 transition-colors"
                  >
                    <ScanSearch className="size-3" />
                  </button>
                )}
                <button
                  onClick={() => setSelectedCamera(cam)}
                  className="rounded-full bg-black/50 p-1.5 text-white hover:bg-black/70 transition-colors"
                >
                  <Maximize2 className="size-3" />
                </button>
              </div>
              {cam.camera.is_primary && (
                <Badge className="absolute top-2 left-2 text-[9px]" variant="secondary">Primary</Badge>
              )}
            </div>
            <div className="px-3 py-2">
              <p className="text-xs font-medium truncate">{cam.camera.label}</p>
              <p className="text-[10px] text-muted-foreground truncate">{cam.tent.name}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

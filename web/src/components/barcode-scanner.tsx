"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";

interface BarcodeScannerProps {
  onScan: (barcode: string) => void;
  onClose: () => void;
}

/**
 * Simple barcode scanner using the device camera.
 * Falls back to manual entry if camera is unavailable.
 */
export function BarcodeScanner({ onScan, onClose }: BarcodeScannerProps) {
  const [manual, setManual] = useState("");
  const [cameraAvailable, setCameraAvailable] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    // Check if BarcodeDetector is available (Chrome/Edge)
    if ("BarcodeDetector" in window) {
      navigator.mediaDevices
        .getUserMedia({ video: { facingMode: "environment" } })
        .then((stream) => {
          setCameraAvailable(true);
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        })
        .catch(() => setCameraAvailable(false));
    }

    return () => {
      // Cleanup camera stream
      if (videoRef.current?.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getTracks().forEach((t) => t.stop());
      }
    };
  }, []);

  useEffect(() => {
    if (!cameraAvailable || !videoRef.current) return;

    // Use BarcodeDetector API if available
    if (!("BarcodeDetector" in window)) return;

    const detector = new (window as unknown as { BarcodeDetector: new (opts: { formats: string[] }) => { detect: (source: HTMLVideoElement) => Promise<{ rawValue: string }[]> } }).BarcodeDetector({
      formats: ["ean_13", "ean_8", "upc_a", "upc_e", "code_128"],
    });

    let cancelled = false;
    const scan = async () => {
      if (cancelled || !videoRef.current) return;
      try {
        const barcodes = await detector.detect(videoRef.current);
        if (barcodes.length > 0) {
          onScan(barcodes[0].rawValue);
          return;
        }
      } catch {
        // Detection failed, retry
      }
      requestAnimationFrame(scan);
    };

    videoRef.current.addEventListener("loadeddata", () => scan());
    return () => {
      cancelled = true;
    };
  }, [cameraAvailable, onScan]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="w-full max-w-md rounded-lg border border-neutral-800 bg-neutral-900 p-6">
        <h2 className="mb-4 text-lg font-semibold text-white">Scan Barcode</h2>

        {cameraAvailable ? (
          <div className="mb-4 overflow-hidden rounded-lg">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full"
            />
          </div>
        ) : (
          <p className="mb-4 text-sm text-neutral-400">
            Camera unavailable. Enter barcode manually.
          </p>
        )}

        <div className="flex gap-2">
          <input
            className="flex-1 rounded border border-neutral-700 bg-neutral-800 px-3 py-2 text-white focus:border-green-600 focus:outline-none"
            placeholder="Enter barcode"
            value={manual}
            onChange={(e) => setManual(e.target.value)}
          />
          <Button
            onClick={() => {
              if (manual) onScan(manual);
            }}
          >
            Look Up
          </Button>
        </div>

        <Button variant="outline" className="mt-3 w-full" onClick={onClose}>
          Cancel
        </Button>
      </div>
    </div>
  );
}

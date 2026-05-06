"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

export function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
    };
    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  if (!deferredPrompt || dismissed) return null;

  async function handleInstall() {
    if (!deferredPrompt) return;
    await deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === "accepted") {
      setDeferredPrompt(null);
    }
    setDismissed(true);
  }

  return (
    <div className="fixed bottom-20 left-4 right-4 z-50 flex items-center justify-between rounded-lg border border-green-800 bg-green-950/90 px-4 py-3 shadow-lg backdrop-blur sm:bottom-4 sm:left-auto sm:right-4 sm:w-80">
      <div>
        <p className="text-sm font-medium text-white">Install Tendril</p>
        <p className="text-xs text-green-300">Add to your home screen</p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => setDismissed(true)}
          className="text-xs text-green-400 hover:text-green-300"
        >
          Later
        </button>
        <Button size="sm" onClick={handleInstall}>
          Install
        </Button>
      </div>
    </div>
  );
}

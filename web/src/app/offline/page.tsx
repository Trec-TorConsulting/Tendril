import { WifiOff } from "lucide-react";

export default function OfflinePage() {
  return (
    <div className="flex min-h-dvh flex-col items-center justify-center px-4 text-center">
      <WifiOff className="size-16 text-muted-foreground mb-4" />
      <h1 className="text-2xl font-bold mb-2">You&apos;re Offline</h1>
      <p className="text-muted-foreground max-w-md">
        Tendril requires an internet connection for most features.
        Any changes you made while offline will sync automatically when you reconnect.
      </p>
      <p className="text-sm text-muted-foreground mt-4">
        Check your Wi-Fi or cellular connection and try again.
      </p>
    </div>
  );
}

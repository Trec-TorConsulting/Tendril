import { Leaf } from "lucide-react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-dvh flex-col items-center justify-center bg-background px-4 py-8">
      <div className="mb-8 flex items-center gap-2">
        <div className="flex size-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <Leaf className="size-5" />
        </div>
        <span className="text-xl font-bold tracking-tight">Tendril</span>
      </div>
      <div className="w-full max-w-sm">{children}</div>
    </div>
  );
}

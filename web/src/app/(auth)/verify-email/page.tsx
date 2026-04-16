"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Suspense } from "react";
import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/v1";

function VerifyEmailInner() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("No verification token provided");
      return;
    }

    fetch(`${API_BASE}/auth/verify-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
    })
      .then(async (res) => {
        const data = await res.json();
        if (res.ok) {
          setStatus("success");
          setMessage(data.message);
        } else {
          setStatus("error");
          setMessage(data.detail || "Verification failed");
        }
      })
      .catch(() => {
        setStatus("error");
        setMessage("Network error");
      });
  }, [token]);

  return (
    <Card className="text-center">
      {status === "loading" && (
        <CardHeader>
          <div className="mx-auto mb-2">
            <Loader2 className="size-8 animate-spin text-primary" />
          </div>
          <CardTitle>Verifying your email…</CardTitle>
        </CardHeader>
      )}
      {status === "success" && (
        <>
          <CardHeader>
            <div className="mx-auto mb-2 flex size-12 items-center justify-center rounded-full bg-primary/10">
              <CheckCircle2 className="size-6 text-primary" />
            </div>
            <CardTitle className="text-xl">Email Verified!</CardTitle>
            <CardDescription>{message}</CardDescription>
          </CardHeader>
          <CardFooter className="justify-center">
            <Button render={<Link href="/dashboard" />}>Go to dashboard</Button>
          </CardFooter>
        </>
      )}
      {status === "error" && (
        <>
          <CardHeader>
            <div className="mx-auto mb-2 flex size-12 items-center justify-center rounded-full bg-destructive/10">
              <XCircle className="size-6 text-destructive" />
            </div>
            <CardTitle className="text-xl">Verification Failed</CardTitle>
            <CardDescription>{message}</CardDescription>
          </CardHeader>
          <CardFooter className="justify-center">
            <Button variant="outline" render={<Link href="/login" />}>Back to sign in</Button>
          </CardFooter>
        </>
      )}
    </Card>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense
      fallback={
        <Card className="flex items-center justify-center py-12">
          <Loader2 className="size-6 animate-spin text-muted-foreground" />
        </Card>
      }
    >
      <VerifyEmailInner />
    </Suspense>
  );
}

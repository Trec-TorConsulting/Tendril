"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { register, createCheckout } from "@/lib/api";
import { setTokens } from "@/lib/auth";
import { Loader2 } from "lucide-react";

const PLAN_NAMES: Record<string, string> = {
  hobby: "Hobby",
  pro: "Pro",
  commercial: "Commercial",
  enterprise: "Enterprise",
};

export default function RegisterPage() {
  return (
    <Suspense>
      <RegisterForm />
    </Suspense>
  );
}

function RegisterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const selectedPlan = searchParams.get("plan");
  const [form, setForm] = useState({
    email: "",
    password: "",
    display_name: "",
    tenant_name: "",
  });
  const [tosAccepted, setTosAccepted] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function update(field: string, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!tosAccepted) {
      setError("You must agree to the Terms of Service and Privacy Policy to create an account.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const tokens = await register(form);
      setTokens(tokens.access_token, tokens.refresh_token);

      // If user selected a paid plan, redirect to Stripe checkout
      if (selectedPlan && selectedPlan !== "free" && PLAN_NAMES[selectedPlan]) {
        try {
          const { checkout_url } = await createCheckout(tokens.access_token, selectedPlan);
          window.location.href = checkout_url;
          return;
        } catch {
          // If checkout fails, fall through to dashboard (they can upgrade later)
        }
      }

      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader className="text-center">
        <CardTitle className="text-xl">Create your account</CardTitle>
        <CardDescription>Get started with Tendril in seconds</CardDescription>
        {selectedPlan && PLAN_NAMES[selectedPlan] && (
          <Badge variant="secondary" className="mx-auto mt-2 bg-green-900/50 text-green-300">
            {PLAN_NAMES[selectedPlan]} plan selected — you&apos;ll complete payment after signup
          </Badge>
        )}
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="tenant_name">Organization name</Label>
            <Input
              id="tenant_name"
              type="text"
              required
              value={form.tenant_name}
              onChange={(e) => update("tenant_name", e.target.value)}
              placeholder="My Grow Op"
              autoFocus
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="display_name">Your name</Label>
            <Input
              id="display_name"
              type="text"
              required
              value={form.display_name}
              onChange={(e) => update("display_name", e.target.value)}
              placeholder="Jane Doe"
              autoComplete="name"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              required
              value={form.email}
              onChange={(e) => update("email", e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={(e) => update("password", e.target.value)}
              placeholder="••••••••"
              autoComplete="new-password"
            />
            <p className="text-xs text-muted-foreground">At least 8 characters</p>
          </div>
          <div className="flex items-start space-x-2">
            <input
              id="tos_accepted"
              type="checkbox"
              checked={tosAccepted}
              onChange={(e) => setTosAccepted(e.target.checked)}
              className="mt-1 size-4 rounded border-input accent-primary"
              required
            />
            <label htmlFor="tos_accepted" className="text-xs text-muted-foreground leading-tight">
              I have read and agree to the{" "}
              <Link href="/terms" target="_blank" className="font-medium text-primary hover:underline">
                Terms of Service
              </Link>{" "}
              and{" "}
              <Link href="/privacy" target="_blank" className="font-medium text-primary hover:underline">
                Privacy Policy
              </Link>
              . I understand that I am solely responsible for compliance with all applicable laws in my jurisdiction.
            </label>
          </div>
          <Button type="submit" className="w-full" disabled={loading || !tosAccepted}>
            {loading && <Loader2 className="mr-2 size-4 animate-spin" />}
            {loading ? "Creating account…" : "Create account"}
          </Button>
        </form>
      </CardContent>
      <CardFooter className="justify-center">
        <p className="text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </CardFooter>
    </Card>
  );
}

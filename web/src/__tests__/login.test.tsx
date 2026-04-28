import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/login",
  useSearchParams: () => new URLSearchParams(),
}));

// Mock next/link
vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

describe("LoginPage", () => {
  it("renders login form with email and password fields", async () => {
    const { default: LoginPage } = await import(
      "@/app/(auth)/login/page"
    );
    render(<LoginPage />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("has link to registration page", async () => {
    const { default: LoginPage } = await import(
      "@/app/(auth)/login/page"
    );
    render(<LoginPage />);

    expect(screen.getByText(/sign up/i)).toHaveAttribute("href", "/register");
  });

  it("renders heading", async () => {
    const { default: LoginPage } = await import(
      "@/app/(auth)/login/page"
    );
    render(<LoginPage />);

    expect(screen.getByText(/sign in.*tendril/i)).toBeInTheDocument();
  });
});

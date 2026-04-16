import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/",
  useParams: () => ({}),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

import LandingPage from "@/app/(marketing)/page";

describe("LandingPage", () => {
  it("renders hero section", () => {
    render(<LandingPage />);
    expect(screen.getByText(/AI-Powered/)).toBeDefined();
    expect(screen.getByText("Start Growing Free")).toBeDefined();
  });

  it("renders features section", () => {
    render(<LandingPage />);
    expect(screen.getByText("Everything You Need to Grow")).toBeDefined();
    expect(screen.getByText("12 Grow Types")).toBeDefined();
    expect(screen.getByText("AI-Powered Insights")).toBeDefined();
  });

  it("renders pricing section", () => {
    render(<LandingPage />);
    expect(screen.getByText("Simple, Transparent Pricing")).toBeDefined();
    expect(screen.getByText("Seedling")).toBeDefined();
    expect(screen.getByText("$14.99")).toBeDefined();
    expect(screen.getByText("$29.99")).toBeDefined();
    expect(screen.getByText("$79.99")).toBeDefined();
  });

  it("renders navigation with login/signup", () => {
    render(<LandingPage />);
    expect(screen.getByText("Log In")).toBeDefined();
    expect(screen.getByText("Sign Up Free")).toBeDefined();
  });

  it("renders footer", () => {
    render(<LandingPage />);
    expect(screen.getByText(/Built for growers/)).toBeDefined();
  });
});

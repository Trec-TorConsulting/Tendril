import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/register",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

describe("RegisterPage", () => {
  it("renders registration form with all fields", async () => {
    const { default: RegisterPage } = await import(
      "@/app/(auth)/register/page"
    );
    render(<RegisterPage />);

    expect(screen.getByLabelText(/organization name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/your name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /create account/i })).toBeInTheDocument();
  });

  it("has link to login page", async () => {
    const { default: RegisterPage } = await import(
      "@/app/(auth)/register/page"
    );
    render(<RegisterPage />);

    expect(screen.getByText(/sign in/i)).toHaveAttribute("href", "/login");
  });
});

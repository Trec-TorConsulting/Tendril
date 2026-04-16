import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard",
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

describe("DashboardLayout", () => {
  it("renders sidebar with navigation items", async () => {
    const { default: DashboardLayout } = await import(
      "@/app/dashboard/layout"
    );
    render(
      <DashboardLayout>
        <div>Test content</div>
      </DashboardLayout>,
    );

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Grows")).toBeInTheDocument();
    expect(screen.getByText("Analytics")).toBeInTheDocument();
    expect(screen.getByText("Devices")).toBeInTheDocument();
    expect(screen.getByText("AI Chat")).toBeInTheDocument();
    expect(screen.getByText("Strains")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
  });

  it("renders children in main content area", async () => {
    const { default: DashboardLayout } = await import(
      "@/app/dashboard/layout"
    );
    render(
      <DashboardLayout>
        <div data-testid="child">Hello</div>
      </DashboardLayout>,
    );

    expect(screen.getByTestId("child")).toBeInTheDocument();
  });

  it("renders Tendril branding", async () => {
    const { default: DashboardLayout } = await import(
      "@/app/dashboard/layout"
    );
    render(
      <DashboardLayout>
        <div />
      </DashboardLayout>,
    );

    const brandLinks = screen.getAllByText(/tendril/i);
    expect(brandLinks.length).toBeGreaterThanOrEqual(1);
  });
});

describe("DashboardPage", () => {
  it("renders dashboard with placeholder cards", async () => {
    const { default: DashboardPage } = await import(
      "@/app/dashboard/page"
    );
    render(<DashboardPage />);

    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Active Grows")).toBeInTheDocument();
    expect(screen.getByText("Devices Online")).toBeInTheDocument();
    expect(screen.getByText("Health Score")).toBeInTheDocument();
  });
});

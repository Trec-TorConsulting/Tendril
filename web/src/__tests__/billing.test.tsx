import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/billing",
  useParams: () => ({}),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/lib/auth", () => ({
  getAccessToken: () => "test-token",
}));

vi.mock("@/lib/api", () => ({
  getBillingStatus: vi.fn().mockResolvedValue({
    plan: "free",
    plan_name: "Seedling (Free)",
    stripe_customer_id: null,
    stripe_subscription_id: null,
    portal_url: null,
  }),
  createCheckout: vi.fn().mockResolvedValue({ checkout_url: "https://checkout.stripe.com/test" }),
  createPortalSession: vi.fn().mockResolvedValue({ portal_url: "https://billing.stripe.com/test" }),
}));

import BillingPage from "@/app/dashboard/billing/page";

describe("BillingPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders billing heading", async () => {
    render(<BillingPage />);
    await waitFor(() => {
      expect(screen.getByText("Billing & Plan")).toBeDefined();
    });
  });

  it("shows current plan", async () => {
    render(<BillingPage />);
    await waitFor(() => {
      expect(screen.getByText("Seedling (Free)")).toBeDefined();
    });
  });

  it("shows plan options", async () => {
    render(<BillingPage />);
    await waitFor(() => {
      expect(screen.getByText("Grower")).toBeDefined();
      expect(screen.getByText("Pro")).toBeDefined();
      expect(screen.getByText("Commercial")).toBeDefined();
    });
  });

  it("shows current plan indicator", async () => {
    render(<BillingPage />);
    await waitFor(() => {
      expect(screen.getByText("Current Plan")).toBeDefined();
    });
  });
});

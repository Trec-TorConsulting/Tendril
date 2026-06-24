import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/billing",
  useParams: () => ({}),
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("next/link", () => ({
  default: ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  ),
}));

vi.mock("@/lib/auth", () => ({
  getAccessToken: () => "test-token",
  getRefreshToken: () => "test-refresh",
  isAuthenticated: () => true,
  setTokens: vi.fn(),
  clearTokens: vi.fn(),
}));

vi.mock("@/components/confirm-dialog", () => ({
  useConfirm: () => vi.fn().mockResolvedValue(true),
  ConfirmProvider: ({ children }: { children: React.ReactNode }) => children,
}));

vi.mock("@/components/ui/sidebar", async () =>
  (await import("./helpers/sidebar-mock")).sidebarModuleMock());

const { mockPublicPlans } = vi.hoisted(() => {
  const mockPublicPlans = [
    {
      id: "p-free",
      slug: "free",
      name: "Seedling",
      description: "Hobbyist tier",
      is_public: true,
      sort_order: 0,
      billing_model: "flat",
      base_price_cents: 0,
      annual_price_cents: 0,
      currency: "USD",
      max_grows: 1,
      max_devices: 2,
      max_team_members: 1,
      max_ai_analyses_month: 5,
      max_storage_gb: 1,
      max_automations: 1,
      max_integrations: 1,
      max_journal_entries_month: 50,
      included_support_tier: "community",
      features_json: {},
    },
    {
      id: "p-hobby",
      slug: "hobby",
      name: "Hobby",
      description: "For dedicated home growers",
      is_public: true,
      sort_order: 1,
      billing_model: "flat",
      base_price_cents: 1900,
      annual_price_cents: 19000,
      currency: "USD",
      max_grows: 5,
      max_devices: 10,
      max_team_members: 2,
      max_ai_analyses_month: 50,
      max_storage_gb: 10,
      max_automations: 10,
      max_integrations: 5,
      max_journal_entries_month: 500,
      included_support_tier: "email",
      features_json: {},
    },
    {
      id: "p-pro",
      slug: "pro",
      name: "Pro",
      description: "For serious operations",
      is_public: true,
      sort_order: 2,
      billing_model: "flat",
      base_price_cents: 4900,
      annual_price_cents: 49000,
      currency: "USD",
      max_grows: 25,
      max_devices: 50,
      max_team_members: 5,
      max_ai_analyses_month: 250,
      max_storage_gb: 50,
      max_automations: 50,
      max_integrations: 20,
      max_journal_entries_month: 2500,
      included_support_tier: "priority",
      features_json: {},
    },
    {
      id: "p-commercial",
      slug: "commercial",
      name: "Commercial",
      description: "For licensed cultivators",
      is_public: true,
      sort_order: 3,
      billing_model: "usage",
      base_price_cents: 19900,
      annual_price_cents: 199000,
      currency: "USD",
      max_grows: null,
      max_devices: null,
      max_team_members: null,
      max_ai_analyses_month: null,
      max_storage_gb: null,
      max_automations: null,
      max_integrations: null,
      max_journal_entries_month: null,
      included_support_tier: "dedicated",
      features_json: {},
    },
  ];
  return { mockPublicPlans };
});

vi.mock("@/lib/api", () => ({
  getBillingStatus: vi.fn().mockResolvedValue({
    plan: "free",
    plan_name: "Seedling (Free)",
    stripe_customer_id: null,
    stripe_subscription_id: null,
    portal_url: null,
  }),
  getPublicPlans: vi.fn().mockResolvedValue(mockPublicPlans),
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
      expect(screen.getByText("Billing")).toBeDefined();
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
      expect(screen.getByText("Hobby")).toBeDefined();
      expect(screen.getByText("Pro")).toBeDefined();
      expect(screen.getByText("Commercial")).toBeDefined();
    });
  });

  it("shows current plan indicator", async () => {
    render(<BillingPage />);
    await waitFor(() => {
      expect(screen.getAllByText("Current Plan").length).toBeGreaterThan(0);
    });
  });
});

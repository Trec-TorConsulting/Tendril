import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/tasks",
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

const { mockTasks } = vi.hoisted(() => {
  const mockTasks = [
    {
      id: "t1",
      title: "Water the plants",
      description: "Check reservoir levels",
      status: "pending",
      priority: "high",
      assigned_to: null,
      created_by: "u1",
      due_date: "2025-06-15T10:00:00Z",
      completed_at: null,
      recurring: "weekly",
      created_at: "2025-06-01T10:00:00Z",
    },
    {
      id: "t2",
      title: "Completed task",
      description: null,
      status: "completed",
      priority: "low",
      assigned_to: null,
      created_by: "u1",
      due_date: null,
      completed_at: "2025-06-10T10:00:00Z",
      recurring: null,
      created_at: "2025-06-01T10:00:00Z",
    },
  ];
  return { mockTasks };
});

vi.mock("@/lib/api", () => ({
  listTasks: vi.fn().mockResolvedValue(mockTasks),
  listGrows: vi.fn().mockResolvedValue([]),
  listTenantMembers: vi.fn().mockResolvedValue([]),
  getCalendarTasks: vi.fn().mockResolvedValue([]),
  createTask: vi.fn().mockResolvedValue({ id: "t3", title: "New", status: "pending" }),
  updateTask: vi.fn().mockResolvedValue({ ...mockTasks[0] }),
  completeTask: vi.fn().mockResolvedValue({ ...mockTasks[0], status: "completed" }),
  deleteTask: vi.fn().mockResolvedValue(undefined),
}));

vi.mock("@/hooks/use-user", () => ({
  useUser: () => ({
    user: {
      id: "u1",
      email: "test@example.com",
      display_name: "Test User",
      role: "owner",
      tenant_id: "t1",
      is_platform_admin: false,
      is_support: false,
      layout_mode: "compact",
    },
    loading: false,
    logout: vi.fn(),
    refresh: vi.fn(),
  }),
}));

vi.mock("@/lib/confetti", () => ({
  fireRain: vi.fn(),
}));

import TasksPage from "@/app/dashboard/tasks/page";

describe("TasksPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders task list", async () => {
    render(<TasksPage />);
    await waitFor(() => {
      expect(screen.getByText("Water the plants")).toBeInTheDocument();
    });
  });

  it("shows page title", async () => {
    render(<TasksPage />);
    await waitFor(() => {
      expect(screen.getByText("Tasks")).toBeInTheDocument();
    });
  });

  it("opens create modal", async () => {
    render(<TasksPage />);
    await waitFor(() => {
      expect(screen.getAllByText("New Task").length).toBeGreaterThanOrEqual(1);
    });
  });

  it("shows priority indicator", async () => {
    render(<TasksPage />);
    await waitFor(() => {
      expect(screen.getByText(/high/i)).toBeInTheDocument();
    });
  });

  it("shows recurring indicator", async () => {
    render(<TasksPage />);
    await waitFor(() => {
      expect(screen.getByText(/weekly/i)).toBeInTheDocument();
    });
  });

  it("shows completed section", async () => {
    render(<TasksPage />);
    await waitFor(() => {
      expect(screen.getByText(/Completed \(1\)/)).toBeInTheDocument();
    });
  });

  it("shows filter buttons", async () => {
    render(<TasksPage />);
    await waitFor(() => {
      expect(screen.getByText("All")).toBeInTheDocument();
      expect(screen.getByText("Pending")).toBeInTheDocument();
      expect(screen.getByText("Completed", { selector: "button" })).toBeInTheDocument();
    });
  });
});

import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/dashboard/tasks",
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

vi.mock("@/lib/api", () => ({
  listTasks: vi.fn().mockResolvedValue(mockTasks),
  createTask: vi.fn().mockResolvedValue({ id: "t3", title: "New", status: "pending" }),
  completeTask: vi.fn().mockResolvedValue({ ...mockTasks[0], status: "completed" }),
  deleteTask: vi.fn().mockResolvedValue(undefined),
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

  it("shows page title", () => {
    render(<TasksPage />);
    expect(screen.getByText("Tasks")).toBeInTheDocument();
  });

  it("opens create modal", async () => {
    render(<TasksPage />);
    fireEvent.click(screen.getByText("+ New Task"));
    await waitFor(() => {
      expect(screen.getByText("New Task")).toBeInTheDocument();
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

  it("shows filter buttons", () => {
    render(<TasksPage />);
    expect(screen.getByText("All")).toBeInTheDocument();
    expect(screen.getByText("pending")).toBeInTheDocument();
    expect(screen.getByText("completed")).toBeInTheDocument();
  });
});

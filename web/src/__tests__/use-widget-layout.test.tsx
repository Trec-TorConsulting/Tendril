import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { useWidgetLayout } from "@/hooks/use-widget-layout";

const STORAGE_KEY = "tendril-dashboard-layout";
const DEFAULT_ORDER = ["stats", "hero", "countdown", "active-grows"];

type PersistedWidget = { id: string; visible: boolean };

function persisted(): PersistedWidget[] {
  return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]");
}

describe("useWidgetLayout", () => {
  beforeEach(() => localStorage.clear());

  it("starts with the full default layout, all visible", () => {
    const { result } = renderHook(() => useWidgetLayout());
    expect(result.current.widgets.map((w) => w.id)).toEqual(DEFAULT_ORDER);
    expect(result.current.widgets.every((w) => w.visible)).toBe(true);
  });

  it("toggles a widget's visibility and persists the change", () => {
    const { result } = renderHook(() => useWidgetLayout());
    act(() => result.current.toggle("stats"));
    expect(result.current.isVisible("stats")).toBe(false);
    expect(persisted().find((w) => w.id === "stats")?.visible).toBe(false);
  });

  it("moves a widget down then back up", () => {
    const { result } = renderHook(() => useWidgetLayout());
    act(() => result.current.moveDown("stats"));
    expect(result.current.widgets.map((w) => w.id).slice(0, 2)).toEqual(["hero", "stats"]);
    act(() => result.current.moveUp("stats"));
    expect(result.current.widgets[0].id).toBe("stats");
  });

  it("clamps moves at the edges", () => {
    const { result } = renderHook(() => useWidgetLayout());
    act(() => result.current.moveUp("stats")); // already first
    expect(result.current.widgets[0].id).toBe("stats");
    act(() => result.current.moveDown("active-grows")); // already last
    expect(result.current.widgets.at(-1)?.id).toBe("active-grows");
  });

  it("restores a persisted layout and merges in newly added defaults", () => {
    // Simulate an older saved layout missing the 'active-grows' widget.
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify([
        { id: "hero", label: "Primary Grow Card", visible: false },
        { id: "stats", label: "Stats Overview", visible: true },
        { id: "countdown", label: "Harvest Countdown", visible: true },
      ]),
    );
    const { result } = renderHook(() => useWidgetLayout());
    expect(result.current.widgets[0].id).toBe("hero");
    expect(result.current.isVisible("hero")).toBe(false);
    // The missing default is appended so the new widget still appears.
    expect(result.current.widgets.map((w) => w.id)).toContain("active-grows");
  });

  it("reset() returns to the default layout", () => {
    const { result } = renderHook(() => useWidgetLayout());
    act(() => result.current.toggle("hero"));
    act(() => result.current.reset());
    expect(result.current.widgets.map((w) => w.id)).toEqual(DEFAULT_ORDER);
    expect(result.current.widgets.every((w) => w.visible)).toBe(true);
  });
});

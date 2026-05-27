import { describe, it, expect, vi, beforeEach } from "vitest";
import { LAYOUT_CONFIGS, type LayoutMode } from "@/lib/layout-config";

describe("Layout Config", () => {
  it("defines all 5 layout modes", () => {
    const modes: LayoutMode[] = ["beginner", "home", "standard", "pro", "commercial"];
    for (const mode of modes) {
      expect(LAYOUT_CONFIGS[mode]).toBeDefined();
      expect(LAYOUT_CONFIGS[mode].mode).toBe(mode);
    }
  });

  it("each mode has required fields", () => {
    for (const config of Object.values(LAYOUT_CONFIGS)) {
      expect(config.label).toBeTruthy();
      expect(config.description).toBeTruthy();
      expect(["relaxed", "normal", "compact"]).toContain(config.density);
      expect(config.tabs.length).toBeGreaterThanOrEqual(3);
      expect(["slow", "normal", "instant"]).toContain(config.animationSpeed);
    }
  });

  it("all modes have a home tab", () => {
    for (const config of Object.values(LAYOUT_CONFIGS)) {
      const homeTab = config.tabs.find((t) => t.id === "home");
      expect(homeTab).toBeDefined();
      expect(homeTab!.href).toBe("/dashboard");
    }
  });

  it("all modes have a log tab pointing to quick-log", () => {
    for (const config of Object.values(LAYOUT_CONFIGS)) {
      const logTab = config.tabs.find((t) => t.id === "log");
      expect(logTab).toBeDefined();
      expect(logTab!.href).toBe("/dashboard/quick-log");
    }
  });

  it("beginner mode uses relaxed density", () => {
    expect(LAYOUT_CONFIGS.beginner.density).toBe("relaxed");
    expect(LAYOUT_CONFIGS.beginner.sidebarCollapsed).toBe(true);
  });

  it("pro and commercial use compact density", () => {
    expect(LAYOUT_CONFIGS.pro.density).toBe("compact");
    expect(LAYOUT_CONFIGS.commercial.density).toBe("compact");
  });

  it("beginner has 4 tabs, others have 5", () => {
    expect(LAYOUT_CONFIGS.beginner.tabs).toHaveLength(4);
    expect(LAYOUT_CONFIGS.home.tabs).toHaveLength(5);
    expect(LAYOUT_CONFIGS.standard.tabs).toHaveLength(5);
    expect(LAYOUT_CONFIGS.pro.tabs).toHaveLength(5);
    expect(LAYOUT_CONFIGS.commercial.tabs).toHaveLength(5);
  });
});

describe("Onboarding mode determination", () => {
  // Mirror the logic from onboarding-wizard.tsx
  function determineMode(growCount: string, experience: string): LayoutMode {
    if (experience === "first") return "beginner";
    if (experience === "commercial") return "commercial";
    if (experience === "professional") return "pro";
    if (experience === "experienced") {
      return growCount === "1" || growCount === "2-5" ? "standard" : "pro";
    }
    return growCount === "1" || growCount === "2-5" ? "home" : "standard";
  }

  it("first-time grower gets beginner mode", () => {
    expect(determineMode("1", "first")).toBe("beginner");
    expect(determineMode("20+", "first")).toBe("beginner");
  });

  it("commercial user gets commercial mode", () => {
    expect(determineMode("20+", "commercial")).toBe("commercial");
    expect(determineMode("1", "commercial")).toBe("commercial");
  });

  it("professional gets pro mode", () => {
    expect(determineMode("6-20", "professional")).toBe("pro");
  });

  it("experienced with few grows gets standard", () => {
    expect(determineMode("2-5", "experienced")).toBe("standard");
  });

  it("experienced with many grows gets pro", () => {
    expect(determineMode("6-20", "experienced")).toBe("pro");
    expect(determineMode("20+", "experienced")).toBe("pro");
  });

  it("hobbyist with few grows gets home", () => {
    expect(determineMode("1", "hobbyist")).toBe("home");
    expect(determineMode("2-5", "hobbyist")).toBe("home");
  });

  it("hobbyist with many grows gets standard", () => {
    expect(determineMode("6-20", "hobbyist")).toBe("standard");
  });
});

describe("Quick-Log offline queue", () => {
  beforeEach(() => {
    vi.stubGlobal("localStorage", {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
      length: 0,
      key: vi.fn(),
    });
  });

  it("offline queue module exports expected functions", async () => {
    const mod = await import("@/lib/offline-queue");
    expect(mod.getQueueCount).toBeDefined();
    expect(mod.triggerSync).toBeDefined();
  });
});

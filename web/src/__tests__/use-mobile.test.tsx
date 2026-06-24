import { renderHook } from "@testing-library/react";
import { describe, it, expect, afterEach } from "vitest";
import { useIsMobile } from "@/hooks/use-mobile";

function setWidth(width: number) {
  Object.defineProperty(window, "innerWidth", {
    writable: true,
    configurable: true,
    value: width,
  });
}

describe("useIsMobile", () => {
  const original = window.innerWidth;
  afterEach(() => setWidth(original));

  it("returns false on a desktop-width viewport", () => {
    setWidth(1280);
    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(false);
  });

  it("returns true on a narrow (mobile) viewport", () => {
    setWidth(500);
    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(true);
  });

  it("treats the 768px breakpoint as the exclusive boundary", () => {
    setWidth(768);
    expect(renderHook(() => useIsMobile()).result.current).toBe(false); // 768 is NOT < 768
    setWidth(767);
    expect(renderHook(() => useIsMobile()).result.current).toBe(true);
  });
});

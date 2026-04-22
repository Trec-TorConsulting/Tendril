import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/* ── Timezone-aware date formatting ─────────────────────────── */

const userTz =
  typeof Intl !== "undefined"
    ? Intl.DateTimeFormat().resolvedOptions().timeZone
    : "UTC";

/** Full date + time: "Apr 22, 2026, 3:45 PM" */
export function formatDateTime(iso: string | Date): string {
  return new Date(iso).toLocaleString("en-US", {
    timeZone: userTz,
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

/** Date only: "Apr 22, 2026" (timezone-aware — for timestamps with time component) */
export function formatDate(iso: string | Date): string {
  return new Date(iso).toLocaleDateString("en-US", {
    timeZone: userTz,
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/** Calendar date only: "Apr 22, 2026" (UTC — for date-only values that should not shift days) */
export function formatCalendarDate(iso: string | Date): string {
  return new Date(iso).toLocaleDateString("en-US", {
    timeZone: "UTC",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/** Short date + time (no year): "Apr 22, 3:45 PM" */
export function formatShortDateTime(iso: string | Date): string {
  return new Date(iso).toLocaleString("en-US", {
    timeZone: userTz,
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

/** Time only: "3:45 PM" */
export function formatTime(iso: string | Date): string {
  return new Date(iso).toLocaleTimeString("en-US", {
    timeZone: userTz,
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Weekday short: "Tue" */
export function formatWeekday(iso: string | Date): string {
  return new Date(iso).toLocaleDateString("en-US", {
    timeZone: userTz,
    weekday: "short",
  });
}

/** Month + year: "April 2026" */
export function formatMonthYear(year: number, month: number): string {
  return new Date(year, month).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
  });
}

/**
 * Unit formatting utilities that respect user preferences.
 *
 * All functions accept raw metric values (the DB canonical format)
 * and convert + format based on the user's preferences.
 */

/** Convert Celsius to Fahrenheit */
export function cToF(c: number): number {
  return c * 9 / 5 + 32;
}

/** Convert Fahrenheit to Celsius */
export function fToC(f: number): number {
  return (f - 32) * 5 / 9;
}

/**
 * Format a temperature value with unit suffix.
 * @param value   — temperature in the source unit
 * @param source  — "c" or "f" (what unit the value is in)
 * @param target  — "fahrenheit" or "celsius" (user preference)
 * @param decimals — decimal places (default 1)
 */
export function formatTemp(
  value: number | null | undefined,
  source: "c" | "f",
  target: "fahrenheit" | "celsius",
  decimals = 1,
): string {
  if (value == null) return "—";

  let converted: number;
  let unit: string;

  if (target === "celsius") {
    converted = source === "f" ? fToC(value) : value;
    unit = "°C";
  } else {
    converted = source === "c" ? cToF(value) : value;
    unit = "°F";
  }

  return `${converted.toFixed(decimals)}${unit}`;
}

/**
 * Format a temperature value — number only (for charts / sparklines).
 */
export function convertTemp(
  value: number | null | undefined,
  source: "c" | "f",
  target: "fahrenheit" | "celsius",
): number | null {
  if (value == null) return null;
  if (target === "celsius") return source === "f" ? fToC(value) : value;
  return source === "c" ? cToF(value) : value;
}

/** Get the temperature unit label */
export function tempUnitLabel(target: "fahrenheit" | "celsius"): string {
  return target === "celsius" ? "°C" : "°F";
}

/** Format wind speed */
export function formatWind(
  kmh: number | null | undefined,
  unit: "kmh" | "mph" | "ms",
): string {
  if (kmh == null) return "—";
  switch (unit) {
    case "mph": return `${(kmh * 0.621371).toFixed(1)} mph`;
    case "ms": return `${(kmh / 3.6).toFixed(1)} m/s`;
    default: return `${kmh.toFixed(1)} km/h`;
  }
}

/** Format pressure */
export function formatPressure(
  hpa: number | null | undefined,
  unit: "hpa" | "inhg",
): string {
  if (hpa == null) return "—";
  if (unit === "inhg") return `${(hpa * 0.02953).toFixed(2)} inHg`;
  return `${hpa.toFixed(0)} hPa`;
}

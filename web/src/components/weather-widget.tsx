"use client";

import { useMemo } from "react";
import { getCurrentWeather } from "@/lib/api";
import { usePreferences } from "@/hooks/use-preferences";
import { formatTemp, formatWind } from "@/lib/units";
import { useApiSWR } from "@/lib/swr";

interface WeatherWidgetProps {
  tentId: string;
}

interface WeatherData {
  temperature_c: number | null;
  humidity_pct: number | null;
  precipitation_mm: number | null;
  wind_speed_kmh: number | null;
  uv_index: number | null;
}

interface WeatherAlert {
  type: string;
  severity: string;
  message: string;
}

export function WeatherWidget({ tentId }: WeatherWidgetProps) {
  const { prefs } = usePreferences();
  const { data, error } = useApiSWR(
    ["weather-widget", tentId],
    (token) => getCurrentWeather(token, tentId),
  );
  const weather = useMemo(() => (data?.current as unknown as WeatherData) ?? null, [data]);
  const alerts = useMemo(() => (data?.alerts as unknown as WeatherAlert[]) ?? [], [data]);

  if (error) {
    return (
      <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-4">
        <p className="text-sm text-neutral-500">Weather unavailable</p>
      </div>
    );
  }

  if (!weather) return null;

  const severityColor: Record<string, string> = {
    critical: "border-red-600 bg-red-900/20 text-red-400",
    warning: "border-yellow-600 bg-yellow-900/20 text-yellow-400",
    info: "border-blue-600 bg-blue-900/20 text-blue-400",
  };

  return (
    <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-4">
      <h3 className="mb-3 text-sm font-medium text-neutral-400">Weather</h3>

      {alerts.length > 0 && (
        <div className="mb-3 space-y-2">
          {alerts.map((a, i) => (
            <div
              key={i}
              className={`rounded border px-3 py-2 text-xs ${severityColor[a.severity] || ""}`}
            >
              {a.message}
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
        {weather.temperature_c != null && (
          <div>
            <span className="text-neutral-500">Temp</span>
            <p className="text-white">{formatTemp(weather.temperature_c, "c", prefs.temp_unit)}</p>
          </div>
        )}
        {weather.humidity_pct != null && (
          <div>
            <span className="text-neutral-500">Humidity</span>
            <p className="text-white">{weather.humidity_pct}%</p>
          </div>
        )}
        {weather.wind_speed_kmh != null && (
          <div>
            <span className="text-neutral-500">Wind</span>
            <p className="text-white">{formatWind(weather.wind_speed_kmh, prefs.wind_unit)}</p>
          </div>
        )}
        {weather.uv_index != null && (
          <div>
            <span className="text-neutral-500">UV</span>
            <p className="text-white">{weather.uv_index}</p>
          </div>
        )}
      </div>
    </div>
  );
}

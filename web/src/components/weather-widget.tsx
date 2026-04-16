"use client";

import { useEffect, useState } from "react";
import { getAccessToken } from "@/lib/auth";
import { getCurrentWeather } from "@/lib/api";

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
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [alerts, setAlerts] = useState<WeatherAlert[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      const token = getAccessToken();
      if (!token) return;
      try {
        const data = await getCurrentWeather(token, tentId);
        setWeather(data.current as unknown as WeatherData);
        setAlerts(data.alerts as unknown as WeatherAlert[]);
      } catch {
        setError("Weather unavailable");
      }
    };
    load();
  }, [tentId]);

  if (error) {
    return (
      <div className="rounded-lg border border-neutral-800 bg-neutral-900 p-4">
        <p className="text-sm text-neutral-500">{error}</p>
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
            <p className="text-white">{weather.temperature_c}°C</p>
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
            <p className="text-white">{weather.wind_speed_kmh} km/h</p>
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

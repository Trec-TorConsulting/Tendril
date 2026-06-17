"use client";

import { useEffect, useState } from "react";
import { formatWeekday } from "@/lib/utils";
import { getCurrentWeather, getWeatherForecast, getWeatherHistory } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Cloud, Sun, Droplets, Wind, Thermometer, AlertTriangle } from "lucide-react";
import { usePreferences } from "@/hooks/use-preferences";
import { formatTemp, formatWind } from "@/lib/units";
import { useApiSWR } from "@/lib/swr";

interface WeatherCardProps {
  tentId: string;
  tentName: string;
  environmentType: string;
}

export function WeatherCard({ tentId, tentName, environmentType }: WeatherCardProps) {
  const { prefs } = usePreferences();
  const [error, setError] = useState<string | null>(null);
  const {
    data,
    isLoading: loading,
    error: loadError,
  } = useApiSWR(
    environmentType === "outdoor" || environmentType === "greenhouse"
      ? ["grow", "weather", tentId, environmentType]
      : null,
    async (token) => {
      const [cur, fc] = await Promise.all([
        getCurrentWeather(token, tentId),
        getWeatherForecast(token, tentId),
      ]);
      return {
        current: cur.current,
        alerts: cur.alerts || [],
        forecast: fc.forecast || [],
      };
    },
  );
  const current = data?.current ?? null;
  const alerts = data?.alerts ?? [];
  const forecast = data?.forecast ?? [];

  useEffect(() => {
    if (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load weather");
    } else {
      setError(null);
    }
  }, [loadError]);

  // Only show for outdoor/greenhouse
  if (environmentType !== "outdoor" && environmentType !== "greenhouse") return null;

  if (loading) {
    return (
      <Card>
        <CardHeader className="pb-3"><CardTitle className="text-sm font-medium flex items-center gap-2"><Cloud className="size-4" />Weather</CardTitle></CardHeader>
        <CardContent><p className="text-sm text-muted-foreground">Loading weather data...</p></CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader className="pb-3"><CardTitle className="text-sm font-medium flex items-center gap-2"><Cloud className="size-4" />Weather</CardTitle></CardHeader>
        <CardContent><p className="text-sm text-muted-foreground">{error}</p></CardContent>
      </Card>
    );
  }

  if (!current) return null;

  const temp = current.temperature_c != null ? current.temperature_c : current.temp_c;
  const humidity = current.humidity_pct ?? current.humidity;
  const windSpeed = current.wind_speed_kmh ?? current.wind_speed;
  const uvIndex = current.uv_index;
  const description = current.description as string || current.condition as string || "";
  const precipitation = current.precipitation_mm;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Cloud className="size-4" />
            Weather — {tentName}
          </CardTitle>
          <Badge variant="outline" className="text-xs capitalize">{environmentType}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="mb-3 space-y-1">
            {alerts.map((a, i) => (
              <div key={i} className="flex items-center gap-2 rounded-md bg-destructive/10 p-2 text-sm text-destructive">
                <AlertTriangle className="size-4" />
                <span>{typeof a === "string" ? a : String((a as Record<string, unknown>)?.event || (a as Record<string, unknown>)?.headline || "Weather alert")}</span>
              </div>
            ))}
          </div>
        )}

        {/* Current conditions */}
        <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-5">
          {temp != null && (
            <div className="flex items-center gap-2">
              <Thermometer className="size-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Temperature</p>
                <p className="font-medium">{formatTemp(Number(temp), "c", prefs.temp_unit)}</p>
              </div>
            </div>
          )}
          {humidity != null && (
            <div className="flex items-center gap-2">
              <Droplets className="size-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Humidity</p>
                <p className="font-medium">{Number(humidity).toFixed(0)}%</p>
              </div>
            </div>
          )}
          {windSpeed != null && (
            <div className="flex items-center gap-2">
              <Wind className="size-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Wind</p>
                <p className="font-medium">{formatWind(Number(windSpeed), prefs.wind_unit)}</p>
              </div>
            </div>
          )}
          {uvIndex != null && (
            <div className="flex items-center gap-2">
              <Sun className="size-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">UV Index</p>
                <p className="font-medium">{Number(uvIndex)}</p>
              </div>
            </div>
          )}
          {precipitation != null && (
            <div className="flex items-center gap-2">
              <Droplets className="size-4 text-muted-foreground" />
              <div>
                <p className="text-xs text-muted-foreground">Precipitation</p>
                <p className="font-medium">{Number(precipitation).toFixed(1)} mm</p>
              </div>
            </div>
          )}
        </div>
        {description && <p className="mt-2 text-sm capitalize text-muted-foreground">{description}</p>}

        {/* Forecast */}
        {forecast.length > 0 && (
          <div className="mt-4 border-t pt-3">
            <p className="mb-2 text-xs font-medium text-muted-foreground">Forecast</p>
            <div className="flex gap-3 overflow-x-auto pb-1">
              {forecast.slice(0, 5).map((f, i) => {
                const fc = f as Record<string, unknown>;
                return (
                  <div key={i} className="flex-shrink-0 rounded-md border p-2 text-center min-w-[5rem]">
                    <p className="text-xs text-muted-foreground">{fc.date ? formatWeekday(fc.date as string) : `Day ${i + 1}`}</p>
                    <p className="text-sm font-medium">{fc.temp_max_c != null ? formatTemp(Number(fc.temp_max_c), "c", prefs.temp_unit, 0) : fc.temperature_c != null ? formatTemp(Number(fc.temperature_c), "c", prefs.temp_unit, 0) : "—"}</p>
                    {fc.condition ? <p className="text-xs text-muted-foreground capitalize">{String(fc.condition)}</p> : null}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

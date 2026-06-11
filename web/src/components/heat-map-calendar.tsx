"use client";

import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface DayData {
  date: string; // YYYY-MM-DD
  count: number;
}

interface HeatMapCalendarProps {
  data: DayData[];
  className?: string;
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function getIntensity(count: number, max: number): string {
  if (count === 0) return "bg-muted";
  const ratio = count / max;
  if (ratio <= 0.25) return "bg-emerald-200 dark:bg-emerald-900";
  if (ratio <= 0.5) return "bg-emerald-400 dark:bg-emerald-700";
  if (ratio <= 0.75) return "bg-emerald-500 dark:bg-emerald-500";
  return "bg-emerald-600 dark:bg-emerald-400";
}

export function HeatMapCalendar({ data, className }: HeatMapCalendarProps) {
  // Build a map for quick lookup
  const dataMap = new Map(data.map((d) => [d.date, d.count]));
  const maxCount = Math.max(1, ...data.map((d) => d.count));

  // Generate 52 weeks ending today
  const today = new Date();
  const startDate = new Date(today);
  startDate.setDate(startDate.getDate() - 364); // ~52 weeks back
  // Align to Sunday
  startDate.setDate(startDate.getDate() - startDate.getDay());

  const weeks: { date: Date; count: number }[][] = [];
  let currentWeek: { date: Date; count: number }[] = [];
  const cursor = new Date(startDate);

  while (cursor <= today) {
    const key = cursor.toISOString().slice(0, 10);
    currentWeek.push({ date: new Date(cursor), count: dataMap.get(key) || 0 });
    if (currentWeek.length === 7) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
    cursor.setDate(cursor.getDate() + 1);
  }
  if (currentWeek.length > 0) {
    weeks.push(currentWeek);
  }

  // Month labels
  const monthLabels: { label: string; col: number }[] = [];
  let lastMonth = -1;
  weeks.forEach((week, i) => {
    const firstDay = week[0];
    const month = firstDay.date.getMonth();
    if (month !== lastMonth) {
      monthLabels.push({ label: MONTHS[month], col: i });
      lastMonth = month;
    }
  });

  return (
    <div className={cn("overflow-x-auto", className)}>
      {/* Month labels */}
      <div className="flex text-[10px] text-muted-foreground mb-1 ml-7">
        {monthLabels.map((m, i) => (
          <span
            key={i}
            className="absolute"
            style={{ left: `${m.col * 14 + 28}px` }}
          >
            {m.label}
          </span>
        ))}
      </div>
      <div className="relative mt-4">
        <div className="flex gap-[2px]">
          {/* Day labels */}
          <div className="flex flex-col gap-[2px] text-[10px] text-muted-foreground mr-1 shrink-0">
            {DAYS.map((d, i) => (
              <div key={d} className={cn("h-[12px] leading-[12px]", i % 2 === 0 ? "invisible" : "")}>
                {d}
              </div>
            ))}
          </div>
          {/* Grid */}
          <TooltipProvider delayDuration={100}>
            <div className="flex gap-[2px]">
              {weeks.map((week, wi) => (
                <div key={wi} className="flex flex-col gap-[2px]">
                  {week.map((day, di) => {
                    const dateStr = day.date.toISOString().slice(0, 10);
                    const isToday = dateStr === today.toISOString().slice(0, 10);
                    return (
                      <Tooltip key={di}>
                        <TooltipTrigger asChild>
                          <div
                            className={cn(
                              "h-[12px] w-[12px] rounded-[2px] transition-colors",
                              getIntensity(day.count, maxCount),
                              isToday && "ring-1 ring-foreground/50",
                            )}
                          />
                        </TooltipTrigger>
                        <TooltipContent side="top" className="text-xs">
                          <span className="font-medium">{day.count} activities</span>
                          <span className="text-muted-foreground ml-1.5">{dateStr}</span>
                        </TooltipContent>
                      </Tooltip>
                    );
                  })}
                </div>
              ))}
            </div>
          </TooltipProvider>
        </div>
        {/* Legend */}
        <div className="flex items-center gap-1.5 mt-3 text-[10px] text-muted-foreground">
          <span>Less</span>
          <div className="h-[10px] w-[10px] rounded-[2px] bg-muted" />
          <div className="h-[10px] w-[10px] rounded-[2px] bg-emerald-200 dark:bg-emerald-900" />
          <div className="h-[10px] w-[10px] rounded-[2px] bg-emerald-400 dark:bg-emerald-700" />
          <div className="h-[10px] w-[10px] rounded-[2px] bg-emerald-500 dark:bg-emerald-500" />
          <div className="h-[10px] w-[10px] rounded-[2px] bg-emerald-600 dark:bg-emerald-400" />
          <span>More</span>
        </div>
      </div>
    </div>
  );
}

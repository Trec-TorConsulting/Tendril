"""PDF report generation for grow cycles.

Uses WeasyPrint to generate HTML → PDF reports with grow data summary,
sensor charts (text-based), health evaluations, and journal entries.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("tendril.data.reports")


async def generate_grow_report_pdf(session: AsyncSession, grow_id: UUID) -> bytes:
    """Generate a comprehensive PDF report for a grow cycle.

    Includes: grow summary, sensor stats, health evaluations, tasks, journal entries.
    Returns PDF bytes.
    """
    from app.grows.models import (
        Bucket,
        BucketSensorReading,
        GrowCycle,
        HealthEval,
        JournalEntry,
    )

    # Fetch grow
    grow = await session.get(GrowCycle, grow_id)
    if not grow:
        raise ValueError(f"Grow cycle {grow_id} not found")

    # Fetch buckets
    buckets = (await session.execute(select(Bucket).where(Bucket.grow_cycle_id == grow_id))).scalars().all()

    # Fetch sensor stats per bucket
    bucket_stats = {}
    for bucket in buckets:
        stats = (
            await session.execute(
                select(
                    func.avg(BucketSensorReading.ph).label("avg_ph"),
                    func.avg(BucketSensorReading.ec).label("avg_ec"),
                    func.avg(BucketSensorReading.water_temp_f).label("avg_temp"),
                    func.min(BucketSensorReading.ph).label("min_ph"),
                    func.max(BucketSensorReading.ph).label("max_ph"),
                    func.min(BucketSensorReading.ec).label("min_ec"),
                    func.max(BucketSensorReading.ec).label("max_ec"),
                    func.count(BucketSensorReading.id).label("reading_count"),
                ).where(BucketSensorReading.bucket_id == bucket.id)
            )
        ).one()
        bucket_stats[bucket.id] = stats

    # Fetch health evaluations
    health_evals = (
        (
            await session.execute(
                select(HealthEval)
                .where(HealthEval.grow_cycle_id == grow_id)
                .order_by(desc(HealthEval.created_at))
                .limit(20)
            )
        )
        .scalars()
        .all()
    )

    # Fetch journal entries
    journals = (
        (
            await session.execute(
                select(JournalEntry)
                .where(JournalEntry.grow_cycle_id == grow_id)
                .order_by(desc(JournalEntry.created_at))
                .limit(50)
            )
        )
        .scalars()
        .all()
    )

    # Build HTML
    html = _build_report_html(grow, buckets, bucket_stats, health_evals, journals)

    # Convert to PDF
    import weasyprint

    pdf_bytes = weasyprint.HTML(string=html).write_pdf()
    return pdf_bytes


def _build_report_html(grow, buckets, bucket_stats, health_evals, journals) -> str:
    """Build the HTML template for the PDF report."""
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    started = grow.started_at.strftime("%Y-%m-%d") if grow.started_at else "N/A"

    # Duration
    duration = ""
    if grow.started_at:
        end = grow.completed_at or datetime.now(UTC)
        days = (end - grow.started_at).days
        duration = f"{days} days"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; color: #1a1a1a; font-size: 11pt; }}
    h1 {{ color: #16a34a; border-bottom: 2px solid #16a34a; padding-bottom: 8px; }}
    h2 {{ color: #15803d; margin-top: 30px; border-bottom: 1px solid #d4d4d4; padding-bottom: 4px; }}
    h3 {{ color: #166534; margin-top: 20px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
    th, td {{ border: 1px solid #e5e5e5; padding: 6px 10px; text-align: left; font-size: 10pt; }}
    th {{ background: #f0fdf4; font-weight: 600; }}
    .stat-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 10px 0; }}
    .stat-box {{ background: #f9fafb; border: 1px solid #e5e5e5; border-radius: 6px; padding: 12px; text-align: center; }}
    .stat-value {{ font-size: 18pt; font-weight: 700; color: #16a34a; }}
    .stat-label {{ font-size: 8pt; color: #6b7280; text-transform: uppercase; }}
    .issue-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 9pt; font-weight: 500; }}
    .severity-low {{ background: #dbeafe; color: #1d4ed8; }}
    .severity-medium {{ background: #fef3c7; color: #92400e; }}
    .severity-high {{ background: #fed7aa; color: #9a3412; }}
    .severity-critical {{ background: #fecaca; color: #991b1b; }}
    .journal-entry {{ margin: 8px 0; padding: 8px 12px; border-left: 3px solid #16a34a; background: #f9fafb; }}
    .journal-date {{ font-size: 9pt; color: #6b7280; }}
    .footer {{ margin-top: 40px; padding-top: 10px; border-top: 1px solid #d4d4d4; font-size: 9pt; color: #9ca3af; text-align: center; }}
    @page {{ margin: 20mm; }}
</style>
</head>
<body>
<h1>🌱 Grow Report: {_escape(grow.name or "Untitled Grow")}</h1>
<p style="color: #6b7280; font-size: 10pt;">Generated {now} by Tendril</p>

<h2>Overview</h2>
<div class="stat-grid">
    <div class="stat-box"><div class="stat-value">{grow.grow_type or "N/A"}</div><div class="stat-label">Grow Type</div></div>
    <div class="stat-box"><div class="stat-value">{grow.current_stage or "N/A"}</div><div class="stat-label">Current Stage</div></div>
    <div class="stat-box"><div class="stat-value">{duration or "N/A"}</div><div class="stat-label">Duration</div></div>
</div>
<table>
<tr><th>Started</th><td>{started}</td><th>Status</th><td>{grow.status or "active"}</td></tr>
<tr><th>Buckets</th><td>{len(buckets)}</td><th>Health Checks</th><td>{len(health_evals)}</td></tr>
</table>
"""

    # Bucket sensor stats
    if buckets:
        html += "<h2>Sensor Summary</h2>"
        html += "<table><tr><th>Bucket</th><th>Readings</th><th>pH (avg)</th><th>pH (range)</th><th>EC (avg)</th><th>EC (range)</th><th>Temp °F (avg)</th></tr>"
        for bucket in buckets:
            stats = bucket_stats.get(bucket.id)
            label = _escape(bucket.label or str(bucket.id)[:8])
            if stats and stats.reading_count:
                html += (
                    f"<tr><td>{label}</td>"
                    f"<td>{stats.reading_count}</td>"
                    f"<td>{stats.avg_ph:.2f}</td>"
                    f"<td>{stats.min_ph:.2f} – {stats.max_ph:.2f}</td>"
                    f"<td>{stats.avg_ec:.2f}</td>"
                    f"<td>{stats.min_ec:.2f} – {stats.max_ec:.2f}</td>"
                    f"<td>{stats.avg_temp:.1f}</td></tr>"
                )
            else:
                html += f"<tr><td>{label}</td><td colspan='6'>No readings</td></tr>"
        html += "</table>"

    # Health evaluations
    if health_evals:
        html += "<h2>Health Evaluations</h2>"
        html += "<table><tr><th>Date</th><th>Score</th><th>Issues</th><th>Severity</th></tr>"
        for ev in health_evals[:10]:
            date = ev.created_at.strftime("%Y-%m-%d %H:%M") if ev.created_at else ""
            score = str(ev.score) if ev.score is not None else "—"
            issues_str = ", ".join(ev.issues[:3]) if ev.issues else "None"
            sev = ev.severity or "—"
            sev_class = f"severity-{sev}" if sev in ("low", "medium", "high", "critical") else ""
            html += (
                f"<tr><td>{date}</td><td>{score}</td>"
                f"<td>{_escape(issues_str)}</td>"
                f'<td><span class="issue-badge {sev_class}">{sev}</span></td></tr>'
            )
        html += "</table>"

    # Journal entries
    if journals:
        html += "<h2>Journal Entries</h2>"
        for entry in journals[:20]:
            date = entry.created_at.strftime("%Y-%m-%d") if entry.created_at else ""
            content = _escape(entry.content[:300]) if entry.content else ""
            html += f'<div class="journal-entry"><div class="journal-date">{date}</div><div>{content}</div></div>'

    html += f'<div class="footer">Tendril Grow Management • Report generated {now}</div>'
    html += "</body></html>"
    return html


def _escape(text: str) -> str:
    """HTML escape."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

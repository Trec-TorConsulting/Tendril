"""PDF grow report generation — sensor trends, photos, milestones, yields."""
from __future__ import annotations

import io
import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("tendril.ai.reports")


async def generate_grow_report(session: AsyncSession, grow_cycle_id: UUID) -> bytes:
    """Generate a PDF report for a grow cycle.

    Returns the PDF as bytes.
    """
    from app.grows.models import (
        GrowCycle, Bucket, BucketSensorReading,
        JournalEntry, BucketPhoto, Yield, Tent,
    )

    grow = await session.get(GrowCycle, grow_cycle_id)
    if not grow:
        raise ValueError("Grow cycle not found")

    tent = await session.get(Tent, grow.tent_id)

    # Gather data
    buckets = (await session.execute(
        select(Bucket).where(Bucket.grow_cycle_id == grow.id).order_by(Bucket.position)
    )).scalars().all()

    journal = (await session.execute(
        select(JournalEntry)
        .where(JournalEntry.bucket_id.in_([b.id for b in buckets]) if buckets else False)
        .order_by(JournalEntry.created_at)
    )).scalars().all() if buckets else []

    photos = (await session.execute(
        select(BucketPhoto)
        .where(BucketPhoto.bucket_id.in_([b.id for b in buckets]) if buckets else False)
        .order_by(BucketPhoto.created_at)
    )).scalars().all() if buckets else []

    yields = (await session.execute(
        select(Yield)
        .where(Yield.bucket_id.in_([b.id for b in buckets]) if buckets else False)
    )).scalars().all() if buckets else []

    # Build report as simple text-based PDF using reportlab-style approach
    # Using a lightweight approach without heavy PDF libs
    report_lines = _build_report_text(grow, tent, buckets, journal, photos, yields)

    # Generate PDF using minimal approach
    pdf_bytes = _text_to_pdf(report_lines)
    return pdf_bytes


def _build_report_text(grow, tent, buckets, journal, photos, yields) -> list[str]:
    """Build report content lines."""
    lines = [
        f"TENDRIL GROW REPORT",
        f"{'=' * 50}",
        f"",
        f"Grow: {grow.name}",
        f"Type: {grow.grow_type}",
        f"Status: {grow.status}",
        f"Stage: {grow.stage}",
        f"Tent: {tent.name if tent else 'N/A'}",
        f"Started: {grow.started_at.strftime('%Y-%m-%d') if grow.started_at else 'N/A'}",
        f"Ended: {grow.ended_at.strftime('%Y-%m-%d') if grow.ended_at else 'Ongoing'}",
        f"",
        f"BUCKETS ({len(buckets)})",
        f"{'-' * 30}",
    ]

    for b in buckets:
        lines.append(f"  #{b.position} {b.label or 'Unnamed'} — {b.strain_name or 'No strain'} ({b.growth_stage})")

    lines.extend([f"", f"JOURNAL ENTRIES ({len(journal)})", f"{'-' * 30}"])
    for j in journal[:20]:  # Cap at 20 entries
        date_str = j.created_at.strftime("%m/%d") if j.created_at else ""
        lines.append(f"  [{date_str}] {j.event_type}: {j.content or ''}")

    lines.extend([f"", f"PHOTOS ({len(photos)})", f"{'-' * 30}"])
    for p in photos[:10]:
        lines.append(f"  {p.caption or 'No caption'} — {p.url}")

    lines.extend([f"", f"HARVEST DATA ({len(yields)})", f"{'-' * 30}"])
    total_wet = 0.0
    total_dry = 0.0
    for y in yields:
        wet = y.wet_weight_g or 0
        dry = y.dry_weight_g or 0
        total_wet += wet
        total_dry += dry
        quality = f" (Quality: {y.quality_rating}/10)" if y.quality_rating else ""
        lines.append(f"  Wet: {wet}g / Dry: {dry}g{quality}")

    if yields:
        lines.extend([
            f"",
            f"  Total Wet: {total_wet}g",
            f"  Total Dry: {total_dry}g",
            f"  Dry/Wet Ratio: {(total_dry / total_wet * 100):.1f}%" if total_wet > 0 else "  N/A",
        ])

    lines.extend([f"", f"{'=' * 50}", f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"])
    return lines


def _text_to_pdf(lines: list[str]) -> bytes:
    """Convert text lines to a minimal PDF.

    Uses a simple PDF structure without external dependencies.
    """
    # Minimal valid PDF generation
    buf = io.BytesIO()

    # PDF header
    buf.write(b"%PDF-1.4\n")

    # Objects
    objects: list[bytes] = []
    offsets: list[int] = []

    # Catalog (obj 1)
    offsets.append(buf.tell())
    cat = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    buf.write(cat)
    objects.append(cat)

    # Pages (obj 2)
    offsets.append(buf.tell())
    pages = b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    buf.write(pages)
    objects.append(pages)

    # Build content stream
    content_lines = []
    y_pos = 750
    for line in lines:
        # Escape special PDF chars
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_lines.append(f"BT /F1 10 Tf 50 {y_pos} Td ({safe}) Tj ET")
        y_pos -= 14
        if y_pos < 50:
            break  # Single page for now

    stream_content = "\n".join(content_lines).encode()

    # Content stream (obj 4)
    offsets.append(buf.tell())
    stream = f"4 0 obj\n<< /Length {len(stream_content)} >>\nstream\n".encode()
    stream += stream_content
    stream += b"\nendstream\nendobj\n"
    buf.write(stream)
    objects.append(stream)

    # Page (obj 3)
    offsets.append(buf.tell())
    page = b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
    buf.write(page)
    objects.append(page)

    # Font (obj 5)
    offsets.append(buf.tell())
    font = b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\nendobj\n"
    buf.write(font)
    objects.append(font)

    # Xref table
    xref_pos = buf.tell()
    buf.write(b"xref\n")
    buf.write(f"0 {len(offsets) + 1}\n".encode())
    buf.write(b"0000000000 65535 f \n")
    for offset in offsets:
        buf.write(f"{offset:010d} 00000 n \n".encode())

    # Trailer
    buf.write(f"trailer\n<< /Size {len(offsets) + 1} /Root 1 0 R >>\n".encode())
    buf.write(f"startxref\n{xref_pos}\n%%EOF\n".encode())

    return buf.getvalue()

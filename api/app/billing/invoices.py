"""Invoice history API — list past invoices from payment provider."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser, get_tenant_session, require_role
from app.billing.service import get_primary_provider
from app.tenants.models import Account, Tenant

router = APIRouter()


class Invoice(BaseModel):
    id: str
    date: str
    amount: str
    status: str  # paid, open, void, draft, uncollectible
    pdf_url: str | None = None
    hosted_url: str | None = None
    description: str | None = None


@router.get("/invoices", response_model=list[Invoice])
async def list_invoices(
    user: Annotated[CurrentUser, Depends(require_role("owner"))],
    session: Annotated[AsyncSession, Depends(get_tenant_session)],
    limit: int = 24,
):
    """List past invoices/receipts from the payment provider.

    Returns up to 24 most recent invoices with PDF download links.
    """
    tenant = await session.get(Tenant, user.tenant_id)
    if not tenant or not tenant.account_id:
        return []

    account = await session.get(Account, tenant.account_id)
    if not account or not account.stripe_customer_id:
        return []

    provider_result = await get_primary_provider(session)
    if not provider_result:
        return []

    provider_row, adapter = provider_result

    # Stripe-specific invoice fetching (most common case)
    if provider_row.provider_type == "stripe":
        try:
            import stripe

            stripe.api_key = adapter.config.get("secret_key", adapter._api_key)

            invoices = stripe.Invoice.list(
                customer=account.stripe_customer_id,
                limit=min(limit, 100),
            )

            return [
                Invoice(
                    id=inv.id,
                    date=_format_timestamp(inv.created),
                    amount=_format_amount(inv.amount_paid, inv.currency),
                    status=inv.status or "unknown",
                    pdf_url=inv.invoice_pdf,
                    hosted_url=inv.hosted_invoice_url,
                    description=inv.description or f"Invoice {inv.number or inv.id[:8]}",
                )
                for inv in invoices.data
                if inv.amount_paid > 0  # Skip $0 invoices
            ]
        except Exception as exc:
            raise HTTPException(status_code=502, detail="Failed to retrieve invoices from payment provider") from exc

    # For other providers, return empty (they handle invoices differently)
    return []


def _format_timestamp(ts: int) -> str:
    """Convert Unix timestamp to ISO date string."""
    from datetime import UTC, datetime

    return datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%d")


def _format_amount(amount_cents: int, currency: str) -> str:
    """Format cents to currency string."""
    symbols = {"usd": "$", "eur": "€", "gbp": "£"}
    symbol = symbols.get(currency, currency.upper() + " ")
    return f"{symbol}{amount_cents / 100:.2f}"

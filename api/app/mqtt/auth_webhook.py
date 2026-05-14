"""EMQX Auth/ACL webhook handlers.

EMQX sends HTTP requests to verify device credentials (auth) and
check topic permissions (ACL). These run inside the mqtt-worker pod.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import bcrypt
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, update

from app.database import async_session_factory
from app.tenants.models import Device

logger = logging.getLogger("tendril.mqtt.auth")

webhook_app = FastAPI(title="EMQX Auth Webhook")


@webhook_app.post("/auth")
async def emqx_auth(request: Request) -> JSONResponse:
    """Verify device credentials. EMQX sends {clientid, username, password}.

    clientid = device_id, password = PSK.
    """
    body = await request.json()
    client_id = body.get("clientid", "")
    password = body.get("password", "")

    if not client_id or not password:
        return JSONResponse({"result": "deny"})

    async with async_session_factory() as session:
        result = await session.execute(select(Device).where(Device.device_id == client_id))
        device = result.scalar_one_or_none()

    if device is None:
        logger.warning("Auth denied: unknown device %s", client_id)
        return JSONResponse({"result": "deny"})

    if device.status == "revoked":
        logger.warning("Auth denied: revoked device %s", client_id)
        return JSONResponse({"result": "deny"})

    if device.status == "unpaired":
        logger.warning("Auth denied: unpaired device %s", client_id)
        return JSONResponse({"result": "deny"})

    if not bcrypt.checkpw(password.encode(), device.psk_hash.encode()):
        logger.warning("Auth denied: bad PSK for device %s", client_id)
        return JSONResponse({"result": "deny"})

    # Update last_seen and status on successful auth
    async with async_session_factory() as session:
        await session.execute(
            update(Device).where(Device.device_id == client_id).values(last_seen=datetime.now(UTC), status="online")
        )
        await session.commit()

    logger.info("Auth allowed: device %s", client_id)
    return JSONResponse({"result": "allow"})


@webhook_app.post("/acl")
async def emqx_acl(request: Request) -> JSONResponse:
    """Check topic permissions. EMQX sends {clientid, username, topic, action}.

    Devices may only publish/subscribe to `t/{their_tenant_id}/d/{their_device_id}/...`
    """
    body = await request.json()
    client_id = body.get("clientid", "")
    topic = body.get("topic", "")

    if not client_id or not topic:
        return JSONResponse({"result": "deny"})

    # Look up the device to get its tenant
    async with async_session_factory() as session:
        result = await session.execute(select(Device).where(Device.device_id == client_id))
        device = result.scalar_one_or_none()

    if device is None or device.status == "revoked":
        return JSONResponse({"result": "deny"})

    # Parse topic: t/{tenant_id}/d/{device_id}/...
    parts = topic.split("/")
    if len(parts) < 4 or parts[0] != "t" or parts[2] != "d":
        logger.warning("ACL denied: malformed topic %s from %s", topic, client_id)
        return JSONResponse({"result": "deny"})

    topic_tenant_id = parts[1]
    topic_device_id = parts[3]

    # Device must match its own tenant and device_id
    if topic_tenant_id != str(device.tenant_id) or topic_device_id != device.device_id:
        logger.warning(
            "ACL denied: device %s tried topic %s (tenant=%s)",
            client_id,
            topic,
            device.tenant_id,
        )
        return JSONResponse({"result": "deny"})

    logger.debug("ACL allowed: device %s topic %s", client_id, topic)
    return JSONResponse({"result": "allow"})


@webhook_app.post("/status")
async def emqx_status(request: Request) -> JSONResponse:
    """Handle device connect/disconnect events from EMQX webhooks.

    Updates device status to 'online' or 'offline'.
    """
    body = await request.json()
    client_id = body.get("clientid", "")
    event = body.get("event", "")

    if not client_id:
        return JSONResponse({"result": "ok"})

    if event in ("client.connected", "client_connected"):
        new_status = "online"
    elif event in ("client.disconnected", "client_disconnected"):
        new_status = "offline"
    else:
        return JSONResponse({"result": "ok"})

    async with async_session_factory() as session:
        await session.execute(
            update(Device).where(Device.device_id == client_id).values(status=new_status, last_seen=datetime.now(UTC))
        )
        await session.commit()

    logger.info("Device %s status → %s", client_id, new_status)
    return JSONResponse({"result": "ok"})


async def start_webhook_server() -> None:
    """Run the auth webhook server on port 8081."""
    config = uvicorn.Config(webhook_app, host="0.0.0.0", port=8081, log_level="info")  # nosec B104 — runs in container
    server = uvicorn.Server(config)
    await server.serve()

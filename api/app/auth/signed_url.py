"""Short-lived HMAC-signed URLs for media endpoints (camera, QR, photos).

Replaces the insecure pattern of passing JWTs as query parameters.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from fastapi import HTTPException

from app.config import get_settings

_SIGNED_URL_MAX_AGE = 300  # 5 minutes


def sign_url(url: str, tenant_id: str) -> str:
    """Append ?sig=...&exp=...&tid=... to a URL for short-lived access."""
    secret = get_settings().jwt_secret.encode()
    exp = str(int(time.time()) + _SIGNED_URL_MAX_AGE)

    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    qs["tid"] = [tenant_id]
    qs["exp"] = [exp]

    # Build the message: path + tid + exp
    message = f"{parsed.path}:{tenant_id}:{exp}"
    sig = hmac.new(secret, message.encode(), hashlib.sha256).hexdigest()
    qs["sig"] = [sig]

    new_query = urlencode(qs, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def verify_signed_url(path: str, sig: str, exp: str, tid: str) -> str:
    """Verify the HMAC signature and expiry. Returns tenant_id on success."""
    secret = get_settings().jwt_secret.encode()

    # Check expiry
    try:
        if int(exp) < int(time.time()):
            raise HTTPException(status_code=401, detail="Signed URL has expired")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid expiry") from None

    # Verify signature
    message = f"{path}:{tid}:{exp}"
    expected = hmac.new(secret, message.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        raise HTTPException(status_code=401, detail="Invalid signature")

    return tid

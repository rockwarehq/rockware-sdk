"""Checking webhook deliveries. SPEC.md section 7."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
from typing import Any, TypedDict

from ._errors import RockwareError

SIGNATURE_HEADER = "Rockware-Signature"
EVENT_ID_HEADER = "Rockware-Event-Id"
EVENT_TYPE_HEADER = "Rockware-Event-Type"

_HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


class WebhookEventData(TypedDict):
    object: str
    id: str


class WebhookEvent(TypedDict):
    """What Rockware sends: ids only. Fetch the record to see what changed."""

    id: str
    """Skip an id you've already handled: the same event can arrive twice."""
    type: str
    """Like "order.updated"."""
    occurredAt: str
    siteId: str
    data: WebhookEventData


def verify_webhook(
    secret: str,
    raw_body: str | bytes,
    header: str | None,
    *,
    tolerance: int = 300,
    now: int | None = None,
) -> bool:
    """True when the Rockware-Signature header signs this body, and its time is
    within ``tolerance`` seconds of now. Pass the raw body as it arrived."""
    if not secret or not header:
        return False
    parts: dict[str, str] = {}
    for part in header.split(","):
        key, sep, value = part.partition("=")
        if sep and key.strip():
            parts[key.strip()] = value.strip()
    t = parts.get("t", "")
    v1 = parts.get("v1", "")
    if not t.isdigit() or not t.isascii() or not _HEX64.match(v1):
        return False
    current = int(time.time()) if now is None else now
    if abs(current - int(t)) > tolerance:
        return False
    body = raw_body.encode() if isinstance(raw_body, str) else raw_body
    expected = hmac.new(secret.encode(), f"{t}.".encode() + body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, v1.lower())


def parse_webhook(
    secret: str,
    raw_body: str | bytes,
    header: str | None,
    *,
    tolerance: int = 300,
    now: int | None = None,
) -> WebhookEvent:
    """Check the signature, then read the event. Raises RockwareError with code
    "forbidden" if the signature is wrong or too old."""
    if not verify_webhook(secret, raw_body, header, tolerance=tolerance, now=now):
        raise RockwareError("forbidden", "The webhook's signature is wrong or too old")
    try:
        event: Any = json.loads(raw_body)
    except ValueError as error:
        raise RockwareError("validation", "The webhook's body isn't JSON") from error
    return event  # type: ignore[no-any-return]

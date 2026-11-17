"""Shapes shared by the generated methods and the clients that send them."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_MAX_PAGES = 10_000


@dataclass(frozen=True)
class Operation:
    """One operation from operations/, ready to send."""

    name: str
    root: str
    """The one field it asks for. Its value is what the method returns."""
    mutation: bool
    safe_to_repeat: bool
    """Sending it twice gives the same result as once, so it can be retried."""
    document: str
    """The operation and the fragments it uses."""

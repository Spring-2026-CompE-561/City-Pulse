"""Backend verification exceptions.

All code that calls or raises exceptions for API/backend validation
lives here. Import helpers from this package:

    from app.exceptions import not_found, unauthorized, bad_request, ...
"""

from app.exceptions.http import (
    bad_request,
    conflict,
    forbidden,
    not_found,
    unauthorized,
)

__all__ = [
    "bad_request",
    "conflict",
    "forbidden",
    "not_found",
    "unauthorized",
]

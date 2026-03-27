"""HTTP exception helpers for API responses.

Routers and services raise these instead of constructing HTTPException
inline, keeping verification logic in one place.
"""

from fastapi import HTTPException, status


def bad_request(detail: str = "Invalid request") -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def unauthorized(detail: str = "Not authenticated") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden(detail: str = "Forbidden") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def not_found(detail: str = "Not found") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def conflict(detail: str = "Conflict") -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)

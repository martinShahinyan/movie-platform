import uuid
from fastapi import Request, Response

COOKIE_NAME = "anonymous_id"
COOKIE_MAX_AGE = 315360000  # 10 years in seconds


def get_anonymous_id(request: Request) -> uuid.UUID:
    """Get the anonymous user UUID from cookies or state."""
    if hasattr(request.state, "anonymous_id") and request.state.anonymous_id:
        return request.state.anonymous_id

    cookie_val = request.cookies.get(COOKIE_NAME)
    if cookie_val:
        try:
            val = uuid.UUID(cookie_val)
            request.state.anonymous_id = val
            return val
        except ValueError:
            pass

    # Generate new UUID if not present or invalid
    val = uuid.uuid4()
    request.state.anonymous_id = val
    return val


def set_anonymous_id_cookie(response: Response, anonymous_id: uuid.UUID) -> None:
    """Ensure the anonymous_id cookie is attached to the response."""
    response.set_cookie(
        key=COOKIE_NAME,
        value=str(anonymous_id),
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=False,  # Set to True in HTTPS production environments
    )

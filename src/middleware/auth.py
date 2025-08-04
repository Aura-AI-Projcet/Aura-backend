"""
Authentication Middleware
"""
import re
from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..config.supabase import supabase_client


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for Supabase JWT tokens"""

    # Routes that don't require authentication
    PUBLIC_ROUTES = [
        r"^/health$",
        r"^/docs.*",
        r"^/redoc.*",
        r"^/openapi\.json$",
        r"^/api/v1/auth/.*",
        r"^/api/v1/avatars$",  # Public avatars list
    ]

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request through authentication middleware"""

        # Check if route is public
        if self._is_public_route(request.url.path):
            return await call_next(request)

        try:
            # Extract Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid authorization header",
                )

            # Extract token
            token = auth_header.split(" ")[1]

            # Verify token with Supabase
            try:
                user_response = supabase_client.auth.get_user(token)
                if not user_response.user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                    )

                user = user_response.user

                # Add user info to request state
                request.state.user_id = user.id
                request.state.user_email = user.email
                request.state.user = user

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token verification failed: {str(e)}",
                )

            # Continue to next middleware/endpoint
            response = await call_next(request)
            return response

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Handle unexpected errors
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"Authentication error: {str(e)}"},
            )

    def _is_public_route(self, path: str) -> bool:
        """Check if the given path is a public route"""
        for pattern in self.PUBLIC_ROUTES:
            if re.match(pattern, path):
                return True
        return False


def get_current_user_id(request: Request) -> str:
    """Get current user ID from request state"""
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated"
        )
    user_id = request.state.user_id
    if not isinstance(user_id, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID type"
        )
    return user_id


def get_current_user(request: Request) -> str:
    """Get current user from request state"""
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated"
        )
    user = request.state.user
    if not hasattr(user, "id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user object"
        )
    return str(user.id)

"""
Rate Limiting Utility.

Provides centralized rate limiter instance and configuration helpers.
Prevents circular imports between app.py and api_routes.py.
"""

import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Limiter with key func
# We don't attach to app here; app.py will do that.
# storage_uri="memory://" is default, suitable for single-instance/dev.
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    strategy="fixed-window"
)

def get_run_limit():
    """
    Get rate limit for the expensive /run endpoint.
    Strict in production, relaxed in development.
    """
    env = os.environ.get("ENV", "development")
    if env == "production":
        return "5 per minute"
    return "60 per minute"

def get_global_limit():
    """
    Get default global rate limit.
    """
    env = os.environ.get("ENV", "development")
    if env == "production":
        return "60 per minute"
    return "200 per minute"

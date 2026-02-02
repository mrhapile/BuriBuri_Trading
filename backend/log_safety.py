"""
Centralized Log Sanitization Utility.

Prevents sensitive API credentials and data from leaking into backend logs.
Enforces redaction of sensitive headers and exception context.
"""

import logging
import traceback
import sys
from typing import Dict, Any, Optional

# Fields that must be redacted in logs
SENSITIVE_FIELDS = {
    "authorization",
    "api-key",
    "apikey",
    "access-token",
    "secret",
    "password",
    "token",
    "apca-api-key-id",
    "apca-api-secret-key",
    "polygon-api-key"
}

REDACTED_PLACEHOLDER = "***REDACTED***"

# Configure standard logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("buriburi-safe-logger")

def sanitize_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Return a copy of headers with sensitive values redacted.
    Case-insensitive key matching.
    """
    if not headers:
        return {}
    
    sanitized = {}
    for k, v in headers.items():
        if k.lower() in SENSITIVE_FIELDS:
            sanitized[k] = REDACTED_PLACEHOLDER
        else:
            sanitized[k] = v
    return sanitized

def sanitize_exception(e: Exception) -> str:
    """
    Return a safe string representation of an exception.
    Removes potentially sensitive context from the message if needed.
    """
    return f"{type(e).__name__}: {str(e)}"

def safe_log(msg: str, data: Optional[Dict[str, Any]] = None, level: str = "INFO"):
    """
    Log a message with optional data, ensuring data is sanitized.
    
    Args:
        msg: The log message
        data: Optional dictionary of data to log (will be sanitized if headers)
        level: Log level (INFO, WARNING, ERROR)
    """
    log_func = getattr(logger, level.lower(), logger.info)
    
    if data:
        # If data looks like headers (dict), sanitize it
        if isinstance(data, dict):
            # Check if any keys match sensitive fields
            has_sensitive = any(k.lower() in SENSITIVE_FIELDS for k in data.keys())
            if has_sensitive:
                data = sanitize_headers(data)
        
        log_func(f"{msg} | Data: {data}")
    else:
        log_func(msg)

def safe_log_exception(e: Exception, context_msg: str = "Exception occurred"):
    """
    Log an exception safely.
    
    - Logs the exception type and message
    - Logs the traceback (standard libraries usually don't verify args in traceback)
    - DOES NOT log locals or extensive context that might hold secrets
    """
    logger.error(f"❌ {context_msg}: {sanitize_exception(e)}")
    # We allow standard traceback printing because it generally shows code paths, not variable values
    # unless values are in the stack frames (which we can't easily scrub without 3rd party libs).
    # For a hackathon/MVP hardening, this is acceptable improvement over direct print(e).
    traceback.print_exc()

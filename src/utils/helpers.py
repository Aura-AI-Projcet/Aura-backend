"""
Utility Helper Functions

Common helper functions used across the application.
"""

from datetime import datetime
from typing import Any


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)


def safe_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary"""
    return data.get(key, default)


def validate_birth_info(birth_info: dict[str, Any]) -> bool:
    """Validate birth information data"""
    required_fields = ["year", "month", "day"]
    return all(field in birth_info and birth_info[field] is not None for field in required_fields)


def generate_session_id() -> str:
    """Generate unique session ID"""
    import uuid
    return str(uuid.uuid4())


def normalize_phone_number(phone: str) -> str:
    """Normalize phone number format"""
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))

    # Add country code if not present
    if len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    elif len(digits) == 10:
        return f"+1{digits}"
    else:
        return f"+{digits}"


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """Mask sensitive data like email or phone"""
    if len(data) <= visible_chars:
        return mask_char * len(data)

    return data[:visible_chars] + mask_char * (len(data) - visible_chars)

"""General utility helpers."""
import re
import secrets
import string
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID


def generate_slug(text: str, max_length: int = 100) -> str:
    """
    Generate a URL-friendly slug from text.
    
    Args:
        text: Input text
        max_length: Maximum slug length
    
    Returns:
        Slugified text
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Truncate to max length
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit('-', 1)[0]
    
    return slug


def generate_code(prefix: str = "", length: int = 8) -> str:
    """
    Generate a unique code.
    
    Args:
        prefix: Optional prefix
        length: Code length (excluding prefix)
    
    Returns:
        Generated code
    """
    chars = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(chars) for _ in range(length))
    
    if prefix:
        return f"{prefix}_{code}"
    return code


def generate_reference_number(prefix: str = "REF") -> str:
    """
    Generate a reference number with timestamp.
    Format: PREFIX-YYYYMMDD-RANDOM
    """
    date_part = datetime.utcnow().strftime("%Y%m%d")
    random_part = ''.join(secrets.choice(string.digits) for _ in range(6))
    return f"{prefix}-{date_part}-{random_part}"


def mask_email(email: str) -> str:
    """
    Mask email address for privacy.
    Example: john.doe@example.com -> j***.d**@example.com
    """
    if not email or '@' not in email:
        return email
    
    local, domain = email.split('@', 1)
    
    if len(local) <= 2:
        masked_local = local[0] + '*' * (len(local) - 1)
    else:
        # Show first char, mask middle, show last char before domain
        parts = local.split('.')
        masked_parts = []
        for part in parts:
            if len(part) <= 2:
                masked_parts.append(part[0] + '*' * (len(part) - 1))
            else:
                masked_parts.append(part[0] + '*' * (len(part) - 2) + part[-1])
        masked_local = '.'.join(masked_parts)
    
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Mask phone number for privacy.
    Example: +1234567890 -> +1***67890
    """
    if not phone:
        return phone
    
    # Remove non-digits except leading +
    has_plus = phone.startswith('+')
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) <= 4:
        return '*' * len(phone)
    
    # Show last 4 digits, mask the rest
    masked = '*' * (len(digits) - 4) + digits[-4:]
    
    if has_plus:
        # Show country code (first 1-3 digits)
        if len(digits) > 7:
            masked = digits[:2] + '*' * (len(digits) - 6) + digits[-4:]
    
    return ('+' if has_plus else '') + masked


def diff_dicts(old: Dict, new: Dict) -> tuple[Dict, Dict, List[str]]:
    """
    Compare two dictionaries and return changes.
    
    Args:
        old: Original dictionary
        new: Updated dictionary
    
    Returns:
        Tuple of (old_values, new_values, changed_fields)
    """
    changed_fields = []
    old_values = {}
    new_values = {}
    
    all_keys = set(old.keys()) | set(new.keys())
    
    for key in all_keys:
        old_val = old.get(key)
        new_val = new.get(key)
        
        if old_val != new_val:
            changed_fields.append(key)
            old_values[key] = old_val
            new_values[key] = new_val
    
    return old_values, new_values, changed_fields


def sanitize_dict(data: Dict, exclude_keys: List[str] = None) -> Dict:
    """
    Sanitize dictionary by removing sensitive keys.
    
    Args:
        data: Input dictionary
        exclude_keys: Keys to exclude
    
    Returns:
        Sanitized dictionary
    """
    exclude_keys = exclude_keys or [
        'password', 'password_hash', 'secret', 'token',
        'api_key', 'private_key', 'mfa_secret', 'backup_codes'
    ]
    
    return {
        k: v for k, v in data.items()
        if k.lower() not in [ek.lower() for ek in exclude_keys]
    }


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to max length with suffix.
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_bool(value: Any) -> bool:
    """
    Parse a value to boolean.
    Handles strings like 'true', 'yes', '1', etc.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ('true', 'yes', '1', 'on', 'enabled')
    if isinstance(value, (int, float)):
        return bool(value)
    return False


def safe_uuid(value: Any) -> Optional[UUID]:
    """
    Safely convert value to UUID or return None.
    """
    if isinstance(value, UUID):
        return value
    if isinstance(value, str):
        try:
            return UUID(value)
        except ValueError:
            return None
    return None


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    if not dt:
        return ""
    return dt.strftime(format_str)


def calculate_percentage(value: int, total: int) -> float:
    """Calculate percentage safely."""
    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)

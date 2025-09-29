from datetime import datetime
from typing import Optional

def parse_datetime(datetime_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO datetime string to Python datetime object."""
    if not datetime_str:
        return None
    
    try:
        # Handle various ISO formats
        if datetime_str.endswith('Z'):
            # Remove 'Z' and parse as UTC
            datetime_str = datetime_str[:-1] + '+00:00'
        
        # Parse ISO format with timezone
        if '+' in datetime_str or datetime_str.endswith('+00:00'):
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        else:
            # Parse as naive datetime
            return datetime.fromisoformat(datetime_str)
    except ValueError as e:
        raise ValueError(f"Invalid datetime format: {datetime_str}. Expected ISO format like '2025-09-26T09:00:00Z' or '2025-09-26T09:00:00'") from e
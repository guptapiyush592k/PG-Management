import re
from urllib.parse import quote


def safe_content_disposition(filename: str, *, inline: bool = True) -> str:
    """Build a safe Content-Disposition header value."""
    safe_name = re.sub(r'[\r\n"\\]', "_", filename.strip()) or "download"
    disposition = "inline" if inline else "attachment"
    ascii_name = safe_name.encode("ascii", "ignore").decode("ascii") or "download"
    encoded = quote(safe_name)
    return f"{disposition}; filename=\"{ascii_name}\"; filename*=UTF-8''{encoded}"

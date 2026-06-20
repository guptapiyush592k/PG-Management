def mask_aadhaar(aadhaar: str | None) -> str | None:
    """Return last four digits only; never expose full Aadhaar in API responses."""
    if not aadhaar:
        return None
    digits = "".join(ch for ch in aadhaar if ch.isdigit())
    if len(digits) != 12:
        return "****"
    return f"XXXX-XXXX-{digits[-4:]}"

def clean_text(value: str | None, max_len: int = 500) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return None
    return cleaned[:max_len]

import unicodedata


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").lower()
    replacements = {
        "’": "'",
        "‘": "'",
        "ʻ": "'",
        "`": "'",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return " ".join(text.split())

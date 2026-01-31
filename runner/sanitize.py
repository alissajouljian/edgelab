import re

def sanitize_logs(text: str, max_kb: int) -> str:
    if not text:
        return ""
    # Remove references to hidden tests/classes
    patterns = [
        r"hidden_tests\.py",
        r"HiddenTests\.java",
        r"/work/[^\s]+",
        r"\b/tmp/[^\s]+",
    ]
    for pat in patterns:
        text = re.sub(pat, "[redacted]", text, flags=re.IGNORECASE)
    # Limit size
    max_bytes = max_kb * 1024
    b = text.encode("utf-8", errors="ignore")
    if len(b) > max_bytes:
        b = b[:max_bytes]
        text = b.decode("utf-8", errors="ignore") + "\n[log truncated]"
    return text

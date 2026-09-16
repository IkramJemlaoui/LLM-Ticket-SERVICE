import re
from .models import GuardrailResult

EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d\s().-]{5,}\d)(?!\w)")
SUSPICIOUS_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+((the|your)\s+)?system\s+prompt",
    r"developer\s+mode",
    r"jailbreak",
    r"do\s+not\s+follow\s+policy",
    r"act\s+as\s+the\s+system",
    r"exfiltrate",
    r"print\s+all\s+hidden\s+instructions",
    r"bypass\s+(mfa|security|authentication)",
]

def redact_pii(text: str) -> tuple[str, bool]:
    original = text
    text = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    text = PHONE_RE.sub(lambda m: "[REDACTED_PHONE]" if len(re.sub(r"\D", "", m.group(0))) >= 7 else m.group(0), text)
    return text, text != original

def detect_injection(text: str) -> list[str]:
    lowered = text.lower()
    reasons = []
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, lowered):
            reasons.append(pattern)
    return reasons

def apply_input_guardrails(text: str, max_chars: int) -> GuardrailResult:
    truncated = False
    if len(text) > max_chars:
        text = text[:max_chars]
        truncated = True
    redacted_text, pii_found = redact_pii(text)
    reasons = detect_injection(text)
    return GuardrailResult(
        pii_found=pii_found,
        redacted_text=redacted_text,
        injection_flag=bool(reasons),
        injection_reasons=reasons,
        truncation_applied=truncated,
    )

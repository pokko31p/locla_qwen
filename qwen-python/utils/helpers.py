import re

def clean_role_dump(text: str) -> str:
    try:
        lines = text.splitlines()
        last_assistant = None
        for i, line in enumerate(lines):
            if re.match(r"^\s*assistant\s*:?\s*$", line, flags=re.I):
                last_assistant = i
        if last_assistant is not None and last_assistant + 1 < len(lines):
            body = "\n".join(lines[last_assistant + 1:])
            if body.strip() and len(body) < len(text):
                return body
    except Exception:
        pass
    return text

def clean_stream_text(text: str) -> str:
    low = text.lower()
    if ("system:" in low or "user:" in low or "\nsystem" in low or "\nuser" in low) and ("assistant" not in low):
        return ""
    if "assistant" in low:
        text = clean_role_dump(text)
    text = re.sub(r"^\s*(system|user|assistant)\s*:\s*", "", text, flags=re.I)
    text = re.sub(r"^\s*(system|user|assistant)\s*\n+", "", text, flags=re.I)
    return text.lstrip()
from __future__ import annotations
import tiktoken
import re
from typing import List

try:
    _enc = tiktoken.get_encoding("cl100k_base")
    def _tok_count(s: str) -> int:
        return len(_enc.encode(s))
except Exception:
    def _tok_count(s: str) -> int:
        return max(1, len((s or "").split()))

def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())

def chunk_text(text: str, max_tokens: int, overlap: int) -> List[str]:
    text = _clean(text)
    if not text:
        return []
    
    words = text.split(" ")
    chunks: List[str] = []
    buf: List[str] = []
    buf_tokens = 0

    for w in words:
        w_tokens = _tok_count(w + " ")
        if buf and buf_tokens + w_tokens > max_tokens:
            chunk = _clean(" ".join(buf))
            if chunk:
                chunks.append(chunk)

            if overlap > 0:
                tail: List[str] = []
                tail_tokens = 0

                for ww in reversed(chunk.split(" ")):
                    tail.append(ww)
                    tail_tokens += _tok_count(ww + " ")
                    if tail_tokens >= overlap:
                        break
                buf = list(reversed(tail))
                buf_tokens = sum(_tok_count(ww + " ") for ww in buf)
            else:
                buf, buf_tokens = [], 0

        buf.append(w)
        buf_tokens += w_tokens

    if buf:
        chunk = _clean(" ".join(buf))
        if chunk:
            chunks.append(chunk)

    return chunks
    

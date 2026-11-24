"""Core Jailbreak Signature Scanner implementation."""
import re
import base64
from typing import Dict, Any, List

class ScanReport:
    def __init__(self, is_jailbreak: bool, confidence: float, matched_signatures: List[str]):
        self.is_jailbreak = is_jailbreak
        self.confidence = confidence
        self.matched_signatures = matched_signatures

class JailbreakScanner:
    SIGNATURES = {
        "DAN_OVERRIDE": r"(?i)(do\s+anything\s+now|jailbreak\s+mode|unfiltered\s+assistant)",
        "INSTRUCTION_BYPASS": r"(?i)(disregard\s+all|ignore\s+prior|forget\s+all\s+rules)",
        "HYPOTHETICAL_EXCUSE": r"(?i)(for\s+educational\s+purposes\s+only|in\s+a\s+fictional\s+world\s+where\s+laws\s+don't\s+apply)",
        "ROLEPLAY_HIJACK": r"(?i)(you\s+are\s+no\s+longer\s+an\s+ai|act\s+as\s+my\s+deceased\s+grandmother)"
    }

    def __init__(self):
        self.compiled = {name: re.compile(pat) for name, pat in self.SIGNATURES.items()}

    def _decode_if_base64(self, text: str) -> str:
        words = text.split()
        for w in words:
            if len(w) > 20 and len(w) % 4 == 0:
                try:
                    decoded = base64.b64decode(w).decode("utf-8", errors="ignore")
                    if len(decoded) > 10 and decoded.isprintable():
                        return decoded
                except Exception:
                    pass
        return ""

    def scan(self, prompt: str) -> ScanReport:
        matches = []
        score = 0.0

        # Scan raw
        for sig_name, pat in self.compiled.items():
            if pat.search(prompt):
                matches.append(sig_name)
                score += 0.4

        # Scan decoded base64 payload if present
        decoded = self._decode_if_base64(prompt)
        if decoded:
            for sig_name, pat in self.compiled.items():
                if pat.search(decoded):
                    matches.append(f"OBFUSCATED_{sig_name}")
                    score += 0.6

        confidence = min(1.0, score)
        return ScanReport(confidence >= 0.4, confidence, matches)

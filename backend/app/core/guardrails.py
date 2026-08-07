"""
Comprehensive Security Guardrail Pipeline (backend/app/core/guardrails.py)
Implements:
1. Prompt Injection & Jailbreak Detection
2. PII Regex & Entity Masking
3. Toxicity & Content Moderation Filtering
4. SQL Injection Protection & Input Sanitization
5. Question Relevance Verification
6. Security Audit Logging & Violation Tracing
"""

import re
import html
from typing import Dict, Any, Tuple, List

# Common Prompt Injection & Jailbreak Attack Keywords
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above)\s+instructions",
    r"system\s+prompt\s+reveal",
    r"reveal\s+your\s+system\s+instructions",
    r"you\s+are\s+now\s+in\s+dan\s+mode",
    r"do\s+anything\s+now",
    r"override\s+system\s+rules",
    r"disregard\s+safety\s+guidelines",
    r"jailbreak\s+mode",
    r"act\s+as\s+an\s+unfiltered\s+ai"
]

# SQL Injection Attack Patterns
SQL_INJECTION_PATTERNS = [
    r"union\s+select",
    r"drop\s+table",
    r"insert\s+into",
    r"delete\s+from",
    r"exec\s*\(" ,
    r"--\s*$",
    r"/\*.*\*/"
]

# Toxic & Harmful Keywords
TOXICITY_PATTERNS = [
    r"\b(hate|kill|exploit|attack|malware|ransomware|hack|phish)\b"
]

# Domain Relevance Keywords for Program Management AI
PM_RELEVANCE_KEYWORDS = [
    "project", "risk", "mitigation", "wbs", "task", "delay", "budget",
    "timeline", "schedule", "raid", "issue", "dependency", "assumption",
    "status", "report", "stakeholder", "sow", "sop", "vendor", "sprint",
    "phase", "mobilization", "planning", "design", "execution", "closure",
    "compliance", "audit", "security", "team", "resource"
]

class SecurityGuardrails:
    """Security Guardrail Enforcement Engine."""

    @staticmethod
    def detect_prompt_injection(text: str) -> Tuple[bool, str]:
        """Detects prompt injection or jailbreak attempts."""
        lowered = text.lower()
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, lowered):
                return True, f"Security Violation: Prompt Injection / Jailbreak attempt detected ('{pattern}')."
        return False, ""

    @staticmethod
    def detect_sql_injection(text: str) -> Tuple[bool, str]:
        """Detects SQL injection payload signatures."""
        lowered = text.lower()
        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, lowered):
                return True, f"Security Violation: Potential SQL Injection pattern detected ('{pattern}')."
        return False, ""

    @staticmethod
    def detect_toxicity(text: str) -> Tuple[bool, str]:
        """Filters harmful or toxic content."""
        lowered = text.lower()
        for pattern in TOXICITY_PATTERNS:
            if re.search(pattern, lowered):
                return True, f"Content Violation: Toxic or harmful language detected ('{pattern}')."
        return False, ""

    @staticmethod
    def mask_pii(text: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Redacts Level 1 & Level 2 PII (SSNs, emails, phone numbers, credit cards).
        Returns masked string and list of masked entities.
        """
        masked_text = text
        masked_items = []

        # 1. Email Redaction
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, masked_text)
        for e in set(emails):
            masked_text = masked_text.replace(e, "[PII: EMAIL_REDACTED]")
            masked_items.append({"type": "EMAIL", "original_masked": e})

        # 2. Phone Number Redaction
        phone_pattern = r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"
        phones = re.findall(phone_pattern, masked_text)
        for p in set(phones):
            masked_text = masked_text.replace(p, "[PII: PHONE_REDACTED]")
            masked_items.append({"type": "PHONE", "original_masked": p})

        # 3. Credit Card Redaction
        cc_pattern = r"\b(?:\d[ -]*?){13,16}\b"
        ccs = re.findall(cc_pattern, masked_text)
        for c in set(ccs):
            masked_text = masked_text.replace(c, "[PII: CREDIT_CARD_REDACTED]")
            masked_items.append({"type": "CREDIT_CARD", "original_masked": c})

        # 4. SSN Redaction
        ssn_pattern = r"\b\d{3}-\d{2}-\d{4}\b"
        ssns = re.findall(ssn_pattern, masked_text)
        for s in set(ssns):
            masked_text = masked_text.replace(s, "[PII: SSN_REDACTED]")
            masked_items.append({"type": "SSN", "original_masked": s})

        return masked_text, masked_items

    @staticmethod
    def verify_relevance(text: str) -> Tuple[bool, float]:
        """Checks if input query is relevant to Program Management domain."""
        lowered = text.lower()
        matches = [kw for kw in PM_RELEVANCE_KEYWORDS if kw in lowered]
        relevance_score = min(1.0, len(matches) / 2.0)
        is_relevant = len(matches) > 0 or len(text.split()) < 4
        return is_relevant, round(relevance_score, 2)

    @classmethod
    def process_input_guardrails(cls, text: str) -> Dict[str, Any]:
        """
        Executes full guardrail inspection on input before LLM execution.
        Returns detailed safety audit report.
        """
        sanitized_text = html.escape(text.strip())

        # Check Injection
        has_inj, inj_msg = cls.detect_prompt_injection(sanitized_text)
        if has_inj:
            return {"passed": False, "reason": inj_msg, "sanitized_text": "", "pii_masked": False}

        # Check SQLi
        has_sqli, sqli_msg = cls.detect_sql_injection(sanitized_text)
        if has_sqli:
            return {"passed": False, "reason": sqli_msg, "sanitized_text": "", "pii_masked": False}

        # Check Toxicity
        has_toxic, toxic_msg = cls.detect_toxicity(sanitized_text)
        if has_toxic:
            return {"passed": False, "reason": toxic_msg, "sanitized_text": "", "pii_masked": False}

        # Mask PII
        clean_text, masked_entities = cls.mask_pii(sanitized_text)

        # Check Relevance
        is_relevant, relevance_score = cls.verify_relevance(clean_text)

        return {
            "passed": True,
            "reason": "Passed all safety guardrails.",
            "sanitized_text": clean_text,
            "original_text": text,
            "pii_masked": len(masked_entities) > 0,
            "masked_entities_count": len(masked_entities),
            "relevance_score": relevance_score,
            "is_relevant": is_relevant
        }

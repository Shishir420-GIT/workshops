"""Deterministic security validators for Clean Air Investigator.

Follows Lab 5 specifications:
- Lab 5A: Prompt Injection defense and untrusted external data boundary.
- Lab 5B: Secret Protection (never expose API keys or tokens).
- Lab 5C: Output Validation (station references, numeric claims, causality checks).
"""

import os
import re
from typing import Any, Dict, List, Optional, Set, Union
from clean_air_agent.schemas import ValidationResult

# Injection attack indicator phrases (case-insensitive)
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"disregard\s+(all\s+)?(previous|prior)\s+directions?",
    r"reveal\s+(the\s+)?(openaq|google|gemini)?\s*(api[_\s]?key|secret|token|credentials)",
    r"show\s+(me\s+)?(the\s+)?(openaq|google|gemini)?\s*(api[_\s]?key|secret|token|credentials)",
    r"what\s+is\s+(your|the)\s+(openaq|google|gemini)?\s*(api[_\s]?key|secret|token|credentials)",
    r"print\s+(os\.environ|env|secrets|credentials)",
    r"system\s*prompt\s*override",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"bypass\s+security\s+rules?",
]

# Definitive causal assertion patterns that lack evidence
UNSUPPORTED_CAUSALITY_PATTERNS = [
    r"\b([A-Za-z\s]+)\s+caused\s+the\s+(pm2\.?5|pm10|pollution|spike|increase)\b",
    r"\b(pollution|pm2\.?5|pm10)\s+is\s+caused\s+by\b",
    r"\bwas\s+caused\s+solely\s+by\b",
    r"\bproves\s+that\s+([A-Za-z\s]+)\s+caused\b",
    r"\bdirect\s+cause\s+of\b",
]

# Causal qualifiers that convert a claim into an acceptable hypothesis
HYPOTHESIS_QUALIFIERS = [
    "may", "might", "could", "possible", "hypothesis", "potentially",
    "suggests", "associated", "coincided", "correlated", "further investigation"
]


def detect_prompt_injection(text: str) -> Dict[str, Any]:
    """Detect prompt injection attempts in input text or external data."""
    if not text:
        return {"is_injection": False, "matched_patterns": []}

    matched = []
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            matched.append(pattern)

    return {
        "is_injection": len(matched) > 0,
        "matched_patterns": matched,
    }


def detect_secret_leakage(text: str, custom_secrets: Optional[List[str]] = None) -> Dict[str, Any]:
    """Verify that no API keys or sensitive credentials appear in text.

    Args:
        text: Text to inspect (e.g. prompt, LLM output, or log string).
        custom_secrets: Optional list of secret strings to explicitly test.

    Returns:
        Dict with "has_leakage" bool and "leaked_items" list.
    """
    if not text:
        return {"has_leakage": False, "leaked_items": []}

    leaked = []

    # 1. Check known active environment variables
    env_keys = ["OPENAQ_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY"]
    for env_var in env_keys:
        val = os.getenv(env_var, "").strip()
        if val and len(val) >= 8 and val in text:
            leaked.append(f"Environment secret ({env_var})")

    # 2. Check custom test fixture secrets
    if custom_secrets:
        for sec in custom_secrets:
            if sec and len(sec) >= 6 and sec in text:
                leaked.append(f"Secret match: {sec[:4]}***")

    # 3. Generic token patterns (e.g. Google AI Studio keys 'AIzaSy...')
    generic_patterns = [
        (r"AIza[0-9A-Za-z_\-]{30,45}", "Google API Key pattern"),
        (r"(?:bearer\s+|key=)[A-Za-z0-9_\-\.]{20,}", "Bearer/Key token pattern"),
    ]
    for pattern, desc in generic_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            leaked.append(desc)

    return {
        "has_leakage": len(leaked) > 0,
        "leaked_items": leaked,
    }


def validate_station_references(
    response_text: str,
    valid_stations: List[Union[str, Dict[str, Any]]],
) -> Dict[str, Any]:
    """Verify that stations mentioned in the response exist in the valid stations list.

    Args:
        response_text: Text produced by Gemini.
        valid_stations: List of station names or station dicts from retrieved evidence.

    Returns:
        Dict with "all_valid" bool, "mentioned_stations", "unsupported_stations".
    """
    # Extract station names from list
    names: Set[str] = set()
    for s in valid_stations:
        if isinstance(s, dict):
            st_name = s.get("station") or s.get("name") or ""
            if st_name:
                names.add(st_name.strip())
        elif isinstance(s, str):
            names.add(s.strip())

    cleaned_names = {n.lower() for n in names if n}

    # Search for station citation patterns like "Station XYZ", "around XYZ", "at XYZ"
    mentioned = set()
    unsupported = set()

    # Common station mention keywords
    station_patterns = [
        r"(?:station|at|around|monitor(?:ing)?|in)\s+([A-Z][A-Za-z0-9\s\-]+?)(?=[,\.\n\(\)\:]|\s+showed|\s+reached|\s+recorded|\s+reported)",
    ]

    for pat in station_patterns:
        matches = re.finditer(pat, response_text)
        for m in matches:
            candidate = m.group(1).strip()
            # Ignore general words
            if candidate.lower() in {"delhi", "the last", "recent", "all stations", "the area", "india"}:
                continue
            if len(candidate) > 3:
                mentioned.add(candidate)
                # Check if matches any valid station (fuzzy containment)
                cand_lower = candidate.lower()
                is_valid = any(
                    (cand_lower in known or known in cand_lower or cand_lower.split()[0] in known)
                    for known in cleaned_names
                )
                if not is_valid:
                    unsupported.add(candidate)

    return {
        "all_valid": len(unsupported) == 0,
        "mentioned_stations": list(mentioned),
        "unsupported_stations": list(unsupported),
    }


def validate_numeric_claims(
    response_text: str,
    evidence_data: Union[Dict[str, Any], List[Dict[str, Any]]],
    tolerance: float = 0.05,
) -> Dict[str, Any]:
    """Verify that specific numeric pollution values cited by Gemini exist in the evidence.

    Args:
        response_text: The AI-generated investigation text.
        evidence_data: The deterministic analytics or observations dictionary.
        tolerance: Allowed proportional tolerance for minor rounding (default 5%).

    Returns:
        Dict with "all_supported" bool, "cited_values", and "unsupported_claims".
    """
    # Extract all real numbers present in evidence
    valid_numbers: Set[float] = set()

    def _harvest_numbers(obj: Any):
        if isinstance(obj, (int, float)) and not isinstance(obj, bool):
            valid_numbers.add(round(float(obj), 1))
        elif isinstance(obj, dict):
            for v in obj.values():
                _harvest_numbers(v)
        elif isinstance(obj, list):
            for item in obj:
                _harvest_numbers(item)

    _harvest_numbers(evidence_data)

    # Extract numeric claims from text: numbers associated with µg/m³, ug/m3, %, or pollution values
    # Examples: "181 µg/m³", "142.0 ug/m3", "reached 184", "increased by 37%"
    claim_patterns = [
        r"(\d+(?:\.\d+)?)\s*(?:µg/m³|µg/m3|ug/m3|ug/m³)",
        r"(?:pm2\.?5|pm10)\s*(?:of|was|reached|at|level of)?\s*(\d+(?:\.\d+)?)",
        r"(?:increase|decrease|change|spike)\s*(?:of|by)?\s*([+\-]?\d+(?:\.\d+)?)\s*%",
    ]

    cited_values = []
    unsupported = []

    for pattern in claim_patterns:
        for match in re.finditer(pattern, response_text, re.IGNORECASE):
            val_str = match.group(1).replace("+", "")
            try:
                num = float(val_str)
                # Ignore small integer percentages under 5% or hours
                if num in {24.0, 48.0, 12.0, 10.0}:
                    continue
                cited_values.append(num)

                # Check if num matches any verified evidence number within tolerance
                matched = False
                for v in valid_numbers:
                    if abs(v) > 0 and abs(num - v) / abs(v) <= tolerance:
                        matched = True
                        break
                    elif v == 0.0 and abs(num) < 0.5:
                        matched = True
                        break

                if not matched:
                    unsupported.append({
                        "claimed_value": num,
                        "raw_snippet": match.group(0),
                    })
            except ValueError:
                continue

    return {
        "all_supported": len(unsupported) == 0,
        "cited_values": cited_values,
        "unsupported_claims": unsupported,
    }


def detect_unsupported_causality(response_text: str) -> Dict[str, Any]:
    """Detect unqualified causal statements that present hypotheses as definitive facts.

    Args:
        response_text: The AI-generated text.

    Returns:
        Dict with "has_unsupported_causality" bool and "flagged_statements".
    """
    flagged = []
    # Split on sentence boundaries without breaking decimal numbers like PM2.5 or 142.0
    sentences = re.split(r"(?<=[a-zA-Z\)])\.\s+|\n+|;+", response_text)

    for sentence in sentences:
        s_clean = sentence.strip()
        if not s_clean:
            continue

        # Check if sentence matches a strong causal claim
        for pat in UNSUPPORTED_CAUSALITY_PATTERNS:
            if re.search(pat, s_clean, re.IGNORECASE):
                # Check if softened by hypothesis qualifiers
                is_hedged = any(q in s_clean.lower() for q in HYPOTHESIS_QUALIFIERS)
                if not is_hedged:
                    flagged.append(s_clean)
                break

    return {
        "has_unsupported_causality": len(flagged) > 0,
        "flagged_statements": flagged,
    }


def validate_investigation_output(
    response_text: str,
    evidence_data: Union[Dict[str, Any], List[Dict[str, Any]]],
    valid_stations: Optional[List[Union[str, Dict[str, Any]]]] = None,
    custom_secrets: Optional[List[str]] = None,
) -> ValidationResult:
    """Master deterministic output validator.

    Verifies:
    1. Secret isolation (no API keys leaked).
    2. Valid station citations (no fictitious stations invented).
    3. Accurate numeric claims (no hallucinated values like 999 µg/m³).
    4. Unsupported causality detection (facts separated from hypotheses).

    Returns:
        ValidationResult with is_safe status, list of issues, and flags.
    """
    issues = []
    flags = {}

    # 1. Secret leakage check
    secret_res = detect_secret_leakage(response_text, custom_secrets)
    flags["secret_leakage"] = secret_res["has_leakage"]
    if secret_res["has_leakage"]:
        issues.append(f"Secret leakage detected: {', '.join(secret_res['leaked_items'])}")

    # 2. Station reference check
    if valid_stations is None and isinstance(evidence_data, dict):
        valid_stations = evidence_data.get("station_comparisons", [])
    if valid_stations:
        station_res = validate_station_references(response_text, valid_stations)
        flags["unsupported_stations"] = not station_res["all_valid"]
        if not station_res["all_valid"]:
            for unsup in station_res["unsupported_stations"]:
                issues.append(f"Station citation not found in evidence: '{unsup}'")

    # 3. Numeric claim verification
    numeric_res = validate_numeric_claims(response_text, evidence_data)
    flags["unsupported_numbers"] = not numeric_res["all_supported"]
    if not numeric_res["all_supported"]:
        for item in numeric_res["unsupported_claims"]:
            issues.append(f"Unsupported numeric claim '{item['raw_snippet']}' (value {item['claimed_value']} not in evidence)")

    # 4. Causality verification
    causality_res = detect_unsupported_causality(response_text)
    flags["unsupported_causality"] = causality_res["has_unsupported_causality"]
    if causality_res["has_unsupported_causality"]:
        for stmt in causality_res["flagged_statements"]:
            issues.append(f"Unsupported definitive causal assertion: '{stmt}' (must be labeled as a hypothesis)")

    is_safe = len(issues) == 0
    sanitized = response_text
    if not is_safe:
        # Append clear audit warnings to the response text for transparency
        warnings = "\n\n> [!CAUTION]\n> **Output Validation Warning**:\n" + "\n".join(f"> - {i}" for i in issues)
        sanitized = response_text + warnings

    return ValidationResult(
        is_safe=is_safe,
        issues=issues,
        flags=flags,
        sanitized_text=sanitized,
    )

from __future__ import annotations

import re
from typing import List


def parse_ip_range(value: str) -> List[str]:
    value = value.strip()

    # ── Single IP ──────────────────────────────────────────────────────
    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", value):
        _validate_ip(value)
        return [value]

    # ── Dash range ─────────────────────────────────────────────────────
    if "-" in value:
        return _parse_dash(value)

    raise ValueError(
        f"Unsupported IP format: '{value}'\n"
        "  Supported formats:\n"
        "    Single IP  : 192.168.1.1\n"
        "    Dash range : 192.168.1.1-254  or  192.168.1.1-192.168.1.254\n"
    )


# ══════════════════════════════════════════════════════════════════════
# Internal helpers
# ══════════════════════════════════════════════════════════════════════


def _parse_dash(value: str) -> List[str]:
    left, right = value.split("-", 1)
    left = left.strip()
    right = right.strip()

    _validate_ip(left)
    left_parts = left.split(".")

    # Right side is a full IP
    if "." in right:
        _validate_ip(right)
        right_parts = right.split(".")
        if left_parts[:3] != right_parts[:3]:
            raise ValueError(
                f"Only same /24 subnet ranges are supported "
                f"(first three octets must match): {left} vs {right}"
            )
        start = int(left_parts[3])
        end = int(right_parts[3])
    else:
        # Right side is just the last octet
        if not right.isdigit():
            raise ValueError(f"Invalid range end: '{right}'")
        start = int(left_parts[3])
        end = int(right)

    if not (0 <= start <= 255 and 0 <= end <= 255):
        raise ValueError(f"Octet values must be 0-255, got {start}-{end}")
    if start > end:
        raise ValueError(f"Range start ({start}) must be <= end ({end})")

    prefix = ".".join(left_parts[:3])
    return [f"{prefix}.{i}" for i in range(start, end + 1)]


def _validate_ip(ip: str) -> None:
    parts = ip.split(".")
    if len(parts) != 4:
        raise ValueError(f"Invalid IP address: '{ip}'")
    for p in parts:
        if not p.isdigit() or not (0 <= int(p) <= 255):
            raise ValueError(f"Invalid IP octet '{p}' in address '{ip}'")

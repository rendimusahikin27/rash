from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

Credential = Tuple[str, str]  # (username, password)


def load_wordlist(filepath: str) -> List[Credential]:
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Wordlist file not found: '{filepath}'")
    if not path.is_file():
        raise ValueError(f"Path is not a file: '{filepath}'")

    credentials = List[Credential] = []
    errors: List[str] = []

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for lineno, line in enumerate(f, start=1):
            stripped = line.strip()

            # Skip blank lines dan komentar
            if not stripped or stripped.startswith("#"):
                continue

            if ":" not in stripped:
                errors.append(f" Line {lineno}: '{stripped}' -> missing ':' separator")
                continue

            # Split hanya pada ':' pertama supaya password yang mengandung ':' tetap aman
            user, _, passwd = stripped.partition(":")
            user = user.strip()
            passwd = passwd.strip()

            if not user:
                errors.append(f" Line {lineno}: username kosong")
                continue

            credentials.append((user, passwd))

    if errors:
        raise ValueError(
            f"Format error di '{filepath}': \n"
            + "\n".join(errors)
            + "\n\nFormat yang benar: user:pass (satu per baris)"
        )

    if not credentials:
        raise ValueError(f"Wordlist kosong atau semua baris dikomentari: '{filepath}'")

    return credentials

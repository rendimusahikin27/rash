from __future__ import annotations

import csv
import json
import os
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from utils.logger import Logger

if TYPE_CHECKING:
    from core.engine import ScanResult


class ResultWriter:
    def __init__(self, filepath: str, logger: Optional[Logger] = None):
        self.filepath = filepath
        self.log = logger or Logger()
        self._ext = os.path.splitext(filepath)[-1].lower()

    def write(self, result: "ScanResult") -> bool:
        try:
            if self._ext == ".json":
                return self._write_json(result)
            elif self._ext == ".csv":
                return self._write_csv(result)
            else:
                # Default to JSON if unknown extension
                self.log.warn(
                    "Unknown extension '%s', defaulting to JSON output", self._ext
                )
                return self._write_json(result)
        except Exception as exc:
            self.log.error("Failed to write output file: %s", exc)
            return False

    # ------------------------------------------------------------------

    def _write_json(self, result: "ScanResult") -> bool:
        record = self._to_dict(result)

        # Append to existing file if it exists, else create new
        records: list = []
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                    if isinstance(existing, list):
                        records = existing
                    else:
                        records = [existing]
            except Exception:
                records = []

        records.append(record)

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

        self.log.success("Results saved → %s", self.filepath)
        return True

    def _write_csv(self, result: "ScanResult") -> bool:
        record = self._to_dict(result)
        fieldnames = list(record.keys())
        file_exists = os.path.exists(self.filepath)

        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)

        self.log.success("Results saved → %s", self.filepath)
        return True

    # ------------------------------------------------------------------

    @staticmethod
    def _to_dict(result: "ScanResult") -> dict:
        return {
            "ip": result.ip,
            "url": result.url,
            "username": result.username,
            "password": result.password,
            "login_success": result.login_success,
            "ssid_2g": result.ssid,
            "ssid_5g": result.ssid_5g,
            "router_model": result.router_model,
            "error": result.error,
        }

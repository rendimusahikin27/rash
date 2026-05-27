from __future__ import annotations

import sys
from rich.panel import Panel
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.engine import ScanResult


class Colors:
    RESET = "/"
    BOLD = "bold"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    CYAN = "cyan"
    WHITE = "white"
    GREY = "grey"
    BLUE = "blue"


def _c(color: str, text: str) -> str:
    return f"[{color}]{text}[{Colors.RESET}]"


class Logger:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    # Public log methods

    def step(self, msg: str, *args):
        self._print(_c(Colors.CYAN, "[*]"), msg, *args)

    def success(self, msg: str, *args):
        self._print(_c(Colors.GREEN, "[✔]"), msg, *args)

    def warn(self, msg: str, *args):
        self._print(_c(Colors.YELLOW, "[⚠]"), msg, *args)

    def error(self, msg: str, *args):
        self._print(_c(Colors.RED, "[✖]"), msg, *args)

    def info(self, msg: str, *args):
        self._print(_c(Colors.WHITE, "[ℹ]"), msg, *args)

    def debug(self, msg: str, *args):
        self._print(_c(Colors.GREY, "[▶]"), msg, *args)

    # Result Summary Printer
    def print_result(self, result: "ScanResult"):
        self._print(Panel("RESULT SUMMARY", width=30))
        self.info("")
        self.info(" IP       : %s", result.ip)
        self.info(" URL      : %s", result.url or "N/A")
        self.info(" Username : %s", result.username)
        self.info(" PAssword : %s", result.password or "N/A")
        self.info(
            " Login      : %s",
            (
                _c(Colors.GREEN, "SUCCESS")
                if result.login_success
                else _c(Colors.RED, "FAILED")
            ),
        )

        if result.login_success:
            self.info(" SSID        : %s", _c(Colors.GREEN, result.ssid or "N/a"))
            self.info(" SSID 5G     : %s", _c(Colors.GREEN, result.ssid_5g or "N/A"))
            if result.router_model:
                self.info(" Model       : %s", result.router_model)

        if result.error:
            self.info(" Error       : %s", _c(Colors.RED, result.error))

    # Internal

    def _print(self, prefix: str, msg: str, *args):
        if args:
            try:
                msg = msg % args
            except TypeError:
                msg = msg + " " + " ".join(str(a) for a in args)
        print(f"{prefix} {msg}", file=sys.stdout, flush=True)

from __future__ import annotations

import os
import shutil
import platform
import subprocess
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

_CHROMIUM_CANDIDATES = [
    "chromium-browser",
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Chromium.app/Contents/MacOS/Google Chrome",
]

_CHROMEDRIVER_CANDIDATES = ["chromedriver", "chromedriver-linux64"]


def _find_binary(candidates: list[str]) -> Optional[str]:
    """Return path to first found binary in PATH or as absolute path."""
    for name in candidates:
        if os.path.isabs(name) and os.path.isfile(name):
            return name
        found = shutil.which(name)
        if found:
            return found
    return None


def _is_termux() -> bool:
    """Detext if running inside Termux on Android."""
    return "com.termux" in os.environ.get("PREFIX", "") or os.path.exists(
        "/data/data/com.termux"
    )


def _build_options(chromium_binary: Optional[str] = None) -> Options:
    options = Options()

    if chromium_binary:
        options.binary_location = chromium_binary

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--window-size=1280,800")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.0.0 Safari/537.36"
    )
    options.accept_insecure_certs = True
    return options


def create_driver(logger=None) -> webdriver.Chrome:
    log = logger

    def _log(msg, *a):
        if log:
            log.debug(msg, *a)

    # Detect Environment
    on_termux = _is_termux()
    _log("Environment: %s", "Termux/Android" if on_termux else platform.system())

    # Find Chromium Binary
    chromium_bin = _find_binary(_CHROMIUM_CANDIDATES)
    if chromium_bin:
        _log("Chromium binary: %s", chromium_bin)
    else:
        _log("Chromium binary tidak ditemukan di PATH, biarkan Selenium cari sendiri")

    options = _build_options(chromium_bin)

    # Find ChromeDriver
    chromedriver_bin = _find_binary(_CHROMEDRIVER_CANDIDATES)

    if chromedriver_bin:
        _log("chromedriver: %s", chromedriver_bin)
        service = Service(chromedriver_bin)
        return webdriver.Chrome(service=service, options=options)

    # Fallback: webdriver-manager
    _log("chromedriver tidak ditemukan, mencoba webdriver-manager...")
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.core.os_manager import ChromeType

        service = Service(
            ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        )
        return webdriver.Chrome(service=service, options=options)

    except Exception as e:
        raise RuntimeError(
            f"Tidak dapat menemukan chromedriver.\n"
            f"  Error: {e}\n\n"
            f"Solusi:\n"
            f"  Termux  : pkg install chromium\n"
            f"  Ubuntu  : sudo apt install chromium-browser chromium-chromedriver\n"
            f"  Atau    : pip install webdriver-manager\n"
        ) from e

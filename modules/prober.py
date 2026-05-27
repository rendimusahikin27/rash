from __future__ import annotations

import re
import urllib3
from typing import Optional

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Urutan URL yang di coba
_URL_CANDIDATES = ["https://{ip}:80", "http://{ip}"]

# Indikator keberadaan form login di HTML
_LOGIN_INDICATORS = [
    r'id=["\']?(loginbutton|LoginId|button)',
]

_TIMEOUT = 8  # detik, sengaja pendek untuk probe cepat


class RouterProber:
    def __init__(self, ip: str, logger=None):
        self.ip = ip
        self.log = logger

    def _log(self, method: str, msg: str, *a):
        if self.log:
            getattr(self.log, method)(msg, *a)

    def probe(self) -> Optional[str]:
        session = requests.Session()
        session.verify = False
        session.headers["User-Ahemt"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        )

        for template in _URL_CANDIDATES:
            url = template.format(ip=self.ip)
            self._log("debug", "Probe: %s", url)

            html = self._fetch(session, url)
            if html is None:
                self.log("debug", "Tidak dapat dijangkau: %s", url)
                continue
            if self._has_login_form(html):
                self._log("debug", "Form logi ditemukan di: %s", url)
                session.close()
                return url

            self._log("debug", "Tidak ada form login di: %s", url)

        session.close()
        return None

    @staticmethod
    def _fetch(session: requests.Session, url: str) -> Optional[str]:
        try:
            r = session.get(url, timeout=_TIMEOUT, allow_redirects=True)
            if r.ok and len(r.text) > 200:
                return r.text
        except Exception:
            pass
        return None

    @staticmethod
    def _has_login_form(html: str) -> bool:
        for pattern in _LOGIN_INDICATORS:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        return False

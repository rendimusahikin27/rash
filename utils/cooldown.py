from __future__ import annotations

import sys
import time


def cooldown_bar(
    seconds: int = 60,
    message: str = "Terlalu banyak percobaan gagal, jeda",
    bar_width: int = 40,
):
    # ── Deteksi apakah terminal support ANSI ──────────────────────────
    use_color = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    YELLOW = "\033[93m" if use_color else ""
    CYAN = "\033[96m" if use_color else ""
    RESET = "\033[0m" if use_color else ""

    print(f"\n{YELLOW}[!] {message} {seconds}s ...{RESET}")

    start = time.time()
    end = start + seconds

    try:
        while True:
            now = time.time()
            elapsed = now - start
            remain = max(0.0, end - now)

            if remain <= 0:
                break

            progress = elapsed / seconds
            filled = int(bar_width * progress)
            empty = bar_width - filled

            bar = "█" * filled + "░" * empty
            pct = int(progress * 100)

            line = (
                f"\r    {CYAN}[{bar}]{RESET} " f"{pct:3d}%  {remain:5.1f}s tersisa   "
            )
            sys.stdout.write(line)
            sys.stdout.flush()

            time.sleep(0.5)

    except KeyboardInterrupt:
        # Izinkan Ctrl+C melewati cooldown
        sys.stdout.write("\r" + " " * (bar_width + 30) + "\r")
        sys.stdout.flush()
        print(f"{YELLOW}[!] Cooldown dilewati (Ctrl+C){RESET}")
        return

    # Hapus baris progress, cetak selesai
    sys.stdout.write("\r" + " " * (bar_width + 30) + "\r")
    sys.stdout.flush()
    print(f"    Jeda selesai, melanjutkan scan...\n")

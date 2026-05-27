from rich.panel import Panel

BANNER = r"""
__________    _____    _________ ___ ___
\______   \  /  _  \  /   _____//   |   \
 |       _/ /  /_\  \ \_____  \/    ~    \
 |    |   \/    |    \/        \    Y    /
 |____|_  /\____|__  /_______  /\___|_  /
        \/         \/        \/       \/
"""


def print_banner():
    try:
        print(Panel(BANNER))
        print(Panel("Router Access & SSID Harvester"))
    except UnicodeEncodeError:
        # Fallback for terminals without Unicode support
        print("\n  Router Access & SSID Harvester\n")

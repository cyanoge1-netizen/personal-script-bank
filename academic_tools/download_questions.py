#!/usr/bin/env python3
"""
====================================================================
Sylhet Engineering College (sec.ac.bd) Question Archive Downloader
Cross-Platform (Android/Termux, Windows, macOS, Linux) CLI Tool.
Automated multi-threaded downloader organized by Department -> Semester.
====================================================================
"""

import os
import sys
import re
import time
import json
import shutil
import platform
import argparse
import concurrent.futures
from pathlib import Path

# ==================== Cross-OS Console & Terminal Setup ====================
def setup_cross_platform_console():
    """Configures UTF-8 encoding and ANSI color sequences across Windows, macOS, Linux, & Android."""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            h_out = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(h_out, ctypes.byref(mode))
            kernel32.SetConsoleMode(h_out, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        except Exception:
            pass
        try:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

setup_cross_platform_console()


# ==================== Terminal Styling & Palette ====================
class UI:
    RESET       = "\033[0m"
    BOLD        = "\033[1m"
    DIM         = "\033[2m"
    ITALIC      = "\033[3m"
    UNDERLINE   = "\033[4m"

    # Color Palette
    CYAN        = "\033[38;5;51m"
    AQUA        = "\033[38;5;45m"
    MINT        = "\033[38;5;49m"
    GREEN       = "\033[38;5;48m"
    YELLOW      = "\033[38;5;226m"
    AMBER       = "\033[38;5;214m"
    CORAL       = "\033[38;5;209m"
    RED         = "\033[38;5;196m"
    PURPLE      = "\033[38;5;141m"
    MAGENTA     = "\033[38;5;207m"
    BLUE        = "\033[38;5;39m"
    WHITE       = "\033[38;5;255m"
    GRAY        = "\033[38;5;245m"
    DARK_GRAY   = "\033[38;5;239m"

    # Box Symbols
    TOP_LEFT     = "╭"
    TOP_RIGHT    = "╮"
    BOTTOM_LEFT  = "╰"
    BOTTOM_RIGHT = "╯"
    HORIZ        = "─"
    VERT         = "│"
    DIV_LEFT     = "├"
    DIV_RIGHT    = "┤"

    ANSI_RE = re.compile(r"\033\[[0-9;]*m")

    @classmethod
    def strip_ansi(cls, s: str) -> str:
        return cls.ANSI_RE.sub("", s)

    @classmethod
    def width(cls) -> int:
        cols = shutil.get_terminal_size((74, 24)).columns
        return max(60, min(cols - 2, 76))

    @classmethod
    def center_text(cls, text: str, width: int) -> str:
        v_len = len(cls.strip_ansi(text))
        if v_len >= width:
            return text
        left = (width - v_len) // 2
        right = width - v_len - left
        return " " * left + text + " " * right

    @classmethod
    def box_line(cls, content: str, width: int, border_color: str = None) -> str:
        b_col = border_color or cls.CYAN
        v_len = len(cls.strip_ansi(content))
        pad = max(0, width - 2 - v_len)
        return f"{b_col}{cls.VERT}{cls.RESET}{content}{' ' * pad}{b_col}{cls.VERT}{cls.RESET}"

    @classmethod
    def box_top(cls, width: int, title: str = "", border_color: str = None) -> str:
        b_col = border_color or cls.CYAN
        if not title:
            return f"{b_col}{cls.TOP_LEFT}{cls.HORIZ * (width - 2)}{cls.TOP_RIGHT}{cls.RESET}"
        t_len = len(cls.strip_ansi(title))
        remaining = max(2, width - 4 - t_len)
        return f"{b_col}{cls.TOP_LEFT}{cls.HORIZ * 2} {title} {b_col}{cls.HORIZ * remaining}{cls.TOP_RIGHT}{cls.RESET}"

    @classmethod
    def box_bottom(cls, width: int, border_color: str = None) -> str:
        b_col = border_color or cls.CYAN
        return f"{b_col}{cls.BOTTOM_LEFT}{cls.HORIZ * (width - 2)}{cls.BOTTOM_RIGHT}{cls.RESET}"

    @classmethod
    def box_divider(cls, width: int, border_color: str = None) -> str:
        b_col = border_color or cls.CYAN
        return f"{b_col}{cls.DIV_LEFT}{cls.HORIZ * (width - 2)}{cls.DIV_RIGHT}{cls.RESET}"


# ==================== Cross-OS Detection & Storage Resolution ====================
def detect_operating_system():
    system = platform.system().lower()
    is_android = os.path.exists("/sdcard") or "com.termux" in os.environ.get("PREFIX", "") or "ANDROID_ROOT" in os.environ
    
    if is_android:
        return "Android", "Android / Termux OS", "📱"
    elif system == "windows" or sys.platform == "win32":
        win_rel = platform.release()
        return "Windows", f"Windows {win_rel}", "🪟"
    elif system == "darwin":
        mac_ver = platform.mac_ver()[0] or platform.release()
        return "macOS", f"macOS {mac_ver}", "🍎"
    else:
        dist = platform.system()
        return "Linux", f"Linux ({dist})", "🐧"


def resolve_platform_storage(os_type: str) -> tuple[Path, str]:
    """Determine best default directory based on operating system."""
    if os_type == "Android":
        if os.path.exists("/sdcard") and os.access("/sdcard", os.W_OK):
            target = Path("/sdcard/Questions")
            try:
                target.mkdir(parents=True, exist_ok=True)
                return target, "SDcard Storage (/sdcard/Questions)"
            except Exception:
                pass

        termux_shared = Path.home() / "storage" / "shared" / "Questions"
        if termux_shared.parent.exists() and os.access(termux_shared.parent, os.W_OK):
            termux_shared.mkdir(parents=True, exist_ok=True)
            return termux_shared, "Termux Shared Storage (~/storage/shared/Questions)"

        termux_home = Path.home() / "Questions"
        termux_home.mkdir(parents=True, exist_ok=True)
        return termux_home, "Termux Home (~/Questions)"

    elif os_type == "Windows":
        downloads = Path.home() / "Downloads" / "SEC_Questions"
        downloads.mkdir(parents=True, exist_ok=True)
        return downloads, "Windows Downloads (Downloads\\SEC_Questions)"

    elif os_type == "macOS":
        mac_downloads = Path.home() / "Downloads" / "SEC_Questions"
        mac_downloads.mkdir(parents=True, exist_ok=True)
        return mac_downloads, "macOS Downloads (~/Downloads/SEC_Questions)"

    else:  # Linux Desktop / Server
        linux_downloads = Path.home() / "Downloads" / "SEC_Questions"
        try:
            if (Path.home() / "Downloads").exists():
                linux_downloads.mkdir(parents=True, exist_ok=True)
                return linux_downloads, "Linux Downloads (~/Downloads/SEC_Questions)"
        except Exception:
            pass
        linux_home = Path.home() / "Questions"
        linux_home.mkdir(parents=True, exist_ok=True)
        return linux_home, "Linux Home (~/Questions)"


# ==================== Network Engine Detection ====================
try:
    import requests
    HAVE_REQUESTS = True
except ImportError:
    import urllib.request
    HAVE_REQUESTS = False


def run_environment_checks(custom_dest: Path | None = None) -> Path:
    w = UI.width()
    os_type, os_label, os_icon = detect_operating_system()

    print(UI.box_top(w, title=f"{UI.BOLD}{UI.WHITE}ENVIRONMENT & STORAGE VERIFICATION{UI.RESET}", border_color=UI.MINT))

    # 1. Operating System
    print(UI.box_line(f"  {UI.GREEN}✔{UI.RESET} {UI.BOLD}Detected OS:{UI.RESET}         {os_icon} {UI.CYAN}{os_label}{UI.RESET}", w, border_color=UI.MINT))

    # 2. Python Version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info < (3, 7):
        print(UI.box_line(f"  {UI.RED}✖ Python Version:{UI.RESET}   v{py_ver} (Python 3.7+ required)", w, border_color=UI.MINT))
        print(UI.box_bottom(w, border_color=UI.MINT))
        sys.exit(1)
    else:
        print(UI.box_line(f"  {UI.GREEN}✔{UI.RESET} {UI.BOLD}Python Runtime:{UI.RESET}      {UI.MINT}v{py_ver}{UI.RESET} {UI.DIM}(Compliant){UI.RESET}", w, border_color=UI.MINT))

    # 3. Network Engine
    if HAVE_REQUESTS:
        req_ver = getattr(requests, "__version__", "active")
        print(UI.box_line(f"  {UI.GREEN}✔{UI.RESET} {UI.BOLD}Network Engine:{UI.RESET}      {UI.YELLOW}requests v{req_ver}{UI.RESET} {UI.DIM}(Pooled){UI.RESET}", w, border_color=UI.MINT))
    else:
        print(UI.box_line(f"  {UI.GREEN}✔{UI.RESET} {UI.BOLD}Network Engine:{UI.RESET}      {UI.CYAN}Standard urllib.request{UI.RESET} {UI.DIM}(Zero-dependency){UI.RESET}", w, border_color=UI.MINT))

    # 4. Storage Resolution
    if custom_dest:
        target_dir = custom_dest.expanduser().resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        storage_label = "Custom User Specified Directory"
    else:
        target_dir, storage_label = resolve_platform_storage(os_type)

    print(UI.box_line(f"  {UI.GREEN}✔{UI.RESET} {UI.BOLD}Storage Target:{UI.RESET}      {UI.WHITE}{target_dir}{UI.RESET}", w, border_color=UI.MINT))
    print(UI.box_line(f"    {UI.DIM}└─ Destination: {storage_label}{UI.RESET}", w, border_color=UI.MINT))
    print(UI.box_bottom(w, border_color=UI.MINT))
    print()
    return target_dir


# ==================== Question Dataset ====================
ALL_QUESTIONS = {
    "cse": {
        "tag": "CSE",
        "badge_color": UI.CYAN,
        "folder": "CSE",
        "name": "Computer Science & Engineering",
        "icon": "💻",
        "items": [
            ("Semester_1-1", "CSE_Session_2024-2025_Semester_1-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2026/3/540d426a-232e-4283-8702-2820766698c7.pdf"),
            ("Semester_1-1", "CSE_Session_2023-2024_Semester_1-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/a27676e0a1d14ecdae5ef85d7d2e7f8b.pdf"),
            ("Semester_1-2", "CSE_Session_2023-2024_Semester_1-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2026/3/c63ea47e-620f-4f64-b3d9-ad88bd618f39.pdf"),
            ("Semester_1-2", "CSE_Session_2022-2023_Semester_1-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/3b4532e7d88f494291410c34e4c60c61.pdf"),
            ("Semester_2-1", "CSE_Session_2022-2023_Semester_2-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/ed7b570ab7624281a32b139542be11d8.pdf"),
            ("Semester_2-1", "CSE_Session_2021-2022_Semester_2-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/2bd2c7181fea4130acd3c6966e919037.pdf"),
            ("Semester_2-2", "CSE_Session_2022-2023_Semester_2-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2026/3/86f8cdcb-d394-48bd-abbc-0d0f450bfd0a.pdf"),
            ("Semester_2-2", "CSE_Session_2021-2022_Semester_2-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/90202faae3a94c2680414e69ec43c7d8.pdf"),
            ("Semester_3-1", "CSE_Session_2021-2022_Semester_3-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2026/0/eb7c53dd-e762-4f76-aeb7-d464f74c4aba.pdf"),
            ("Semester_3-1", "CSE_Session_2020-2021_Semester_3-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/f27c79f3b1cb477d849e41ed2dd106ac.pdf"),
            ("Semester_3-2", "CSE_Session_2020-2021_Semester_3-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/138d2ede539b4618a192fb0c14b42238.pdf"),
            ("Semester_4-1", "CSE_Session_2020-2021_Semester_4-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2026/0/8b84d636-b959-470e-a00a-7129d79a6b56.pdf"),
            ("Semester_4-1", "CSE_Session_2019-2020_Semester_4-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/7578bef007f845adbae77751f7f53a6f.pdf"),
            ("Semester_4-2", "CSE_Session_2019-2020_Semester_4-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/9e93a6a086ae4d3c94164a59219ffed4.pdf"),
        ]
    },
    "eee": {
        "tag": "EEE",
        "badge_color": UI.YELLOW,
        "folder": "EEE",
        "name": "Electrical & Electronic Engineering",
        "icon": "⚡",
        "items": [
            ("Semester_1-1", "EEE_Session_2023-2024_Semester_1-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/c37717eab8524b8788611371b567cf97.pdf"),
            ("Semester_1-2", "EEE_Session_2022-2023_Semester_1-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/39c3361093fa409181ca7013e28f71f6.pdf"),
            ("Semester_2-1", "EEE_Session_2022-2023_Semester_2-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/23cf61771016476a9c5c650c32922e3b.pdf"),
            ("Semester_2-1", "EEE_Session_2021-2022_Semester_2-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/4b88365590504fcdb849c8f3c4058057.pdf"),
            ("Semester_2-2", "EEE_Session_2021-2022_Semester_2-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/ee42ac0d41dd4e3faeb020be64c86dbf.pdf"),
            ("Semester_3-1", "EEE_Session_2020-2021_Semester_3-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/8a4d2d81ba46415f9f263853b823723d.pdf"),
            ("Semester_3-2", "EEE_Session_2020-2021_Semester_3-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/0b8d18a2c1ac44fd83605df22c0aae99.pdf"),
            ("Semester_4-1", "EEE_Session_2019-2020_Semester_4-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/a317448596114bb888da6f3defb32037.pdf"),
            ("Semester_4-2", "EEE_Session_2019-2020_Semester_4-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/fdd6e5a7452544d782858c1fc1f3489f.pdf"),
        ]
    },
    "civil": {
        "tag": "CE ",
        "badge_color": UI.GREEN,
        "folder": "CE",
        "name": "Civil Engineering",
        "icon": "🏗️",
        "items": [
            ("Semester_1-1", "CE_Session_2024-2025_Semester_1-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2026/3/8570cc69-54d6-4f79-83b0-eeedaab9f713.pdf"),
            ("Semester_1-1", "CE_Session_2023-2024_Semester_1-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/632becd847ce43ec89f06a3c61ceab5f.pdf"),
            ("Semester_1-2", "CE_Session_2023-2024_Semester_1-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2026/3/693de707-3598-4e62-8618-bc9a2e57b370.pdf"),
            ("Semester_1-2", "CE_Session_2022-2023_Semester_1-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/2e02e7887a624d488dfda5fad29d0da9.pdf"),
            ("Semester_2-1", "CE_Session_2022-2023_Semester_2-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/4d54d5531b1448e398265ecfa77838d8.pdf"),
            ("Semester_2-1", "CE_Session_2021-2022_Semester_2-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/aa76965a60a344829462a0d5079fec9a.pdf"),
            ("Semester_2-2", "CE_Session_2022-2023_Semester_2-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2026/3/902428b3-7eaf-42b0-8241-dc1b663e3e9a.pdf"),
            ("Semester_2-2", "CE_Session_2021-2022_Semester_2-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/868c2a93b644482ab9bfb5680cddb1ed.pdf"),
            ("Semester_3-1", "CE_Session_2021-2022_Semester_3-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2026/0/172b4706-2056-457e-9f49-2c9f4a248de6.pdf"),
            ("Semester_3-1", "CE_Session_2020-2021_Semester_3-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/45199ff44b29488286c8bced26419546.pdf"),
            ("Semester_3-2", "CE_Session_2020-2021_Semester_3-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/ceb5159cfb8748db806b4c6e7700a294.pdf"),
            ("Semester_4-1", "CE_Session_2020-2021_Semester_4-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2026/0/4af64d75-830c-4b98-87d1-6aa3801e39c2.pdf"),
            ("Semester_4-1", "CE_Session_2019-2020_Semester_4-1.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/c5edad4785634b998e3535f17ddc3a20.pdf"),
            ("Semester_4-2", "CE_Session_2020-2021_Semester_4-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2026/8/5676b0d9-9185-4990-ab72-51008b888966.pdf"),
            ("Semester_4-2", "CE_Session_2019-2020_Semester_4-2.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/5e97965220fa4902b6591af9ac110f13.pdf"),
        ]
    },
    "admission": {
        "tag": "ADM",
        "badge_color": UI.MAGENTA,
        "folder": "Admission_Test",
        "name": "Undergraduate Admission Tests",
        "icon": "🎯",
        "items": [
            ("", "SEC_Admission_Test_Question_2025-2026.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2026/3/d119f009-31f2-4db8-a0b1-3ec153e0d864.pdf"),
            ("", "SEC_Admission_Test_Question_2024-2025.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/2c5ef297412946dc880f2ca0006f8d08.pdf"),
            ("", "SEC_Admission_Test_Question_2023-2024.pdf", "https://objectstorage.ap-dcc-gazipur-1.oraclecloud15.com/n/axvjbnqprylg/b/V2Ministry/o/office-sec/2024/12/51144ea9275941c0bf9869a7e27d2647.pdf"),
        ]
    }
}

CHOICE_MAPPING = {
    "1": ["cse"],
    "cse": ["cse"],
    "2": ["eee"],
    "eee": ["eee"],
    "3": ["civil"],
    "civil": ["civil"],
    "ce": ["civil"],
    "4": ["admission"],
    "admission": ["admission"],
    "adm": ["admission"],
    "5": ["cse", "eee", "civil", "admission"],
    "all": ["cse", "eee", "civil", "admission"],
}


def print_banner():
    w = UI.width()
    print()
    print(UI.box_top(w, border_color=UI.CYAN))
    title = f"⚡ {UI.BOLD}{UI.WHITE}SYLHET ENGINEERING COLLEGE {UI.GRAY}•{UI.RESET} {UI.AQUA}QUESTION ARCHIVE{UI.RESET} ⚡"
    sub   = f"{UI.DIM}{UI.WHITE}Department ➔ Semester Structured Downloader {UI.GRAY}(sec.ac.bd){UI.RESET}"
    print(f"{UI.CYAN}│{UI.RESET}{UI.center_text(title, w - 2)}{UI.CYAN}│{UI.RESET}")
    print(f"{UI.CYAN}│{UI.RESET}{UI.center_text(sub, w - 2)}{UI.CYAN}│{UI.RESET}")
    print(UI.box_bottom(w, border_color=UI.CYAN))
    print()


def print_menu():
    w = UI.width()
    title = f"{UI.BOLD}{UI.WHITE}SELECT ARCHIVE CATEGORY{UI.RESET}"
    print(UI.box_top(w, title=title, border_color=UI.BLUE))
    print(UI.box_line("", w, border_color=UI.BLUE))

    options = [
        ("1", "CSE",       "💻", "Computer Science & Engineering",      "14 Papers", UI.CYAN),
        ("2", "EEE",       "⚡", "Electrical & Electronic Engineering", " 9 Papers", UI.YELLOW),
        ("3", "Civil / CE","🏗️ ", "Civil Engineering",                  "15 Papers", UI.GREEN),
        ("4", "Admission", "🎯", "Undergraduate Admission Tests",       " 3 Papers", UI.MAGENTA),
        ("5", "ALL",       "🌐", "Download All 41 Papers (Full Bundle)", "41 Papers", UI.AMBER),
    ]

    for key, code, icon, desc, count, col in options:
        opt_text = f"  {UI.BOLD}{UI.WHITE}[{key}]{UI.RESET} {icon} {col}{UI.BOLD}{code:<11}{UI.RESET} {UI.WHITE}{desc}{UI.RESET}"
        count_text = f"{UI.DIM}{count}{UI.RESET}  "
        total_len = len(UI.strip_ansi(opt_text)) + len(UI.strip_ansi(count_text))
        pad = max(1, (w - 2) - total_len)
        line = f"{opt_text}{' ' * pad}{count_text}"
        print(UI.box_line(line, w, border_color=UI.BLUE))

    print(UI.box_line("", w, border_color=UI.BLUE))
    print(UI.box_bottom(w, border_color=UI.BLUE))
    print()


def get_interactive_choice() -> list[str]:
    while True:
        try:
            prompt = f" {UI.CYAN}➤{UI.RESET} {UI.BOLD}Select department [1-5 or cse/eee/civil/all]: {UI.RESET}"
            choice = input(prompt).strip().lower()
            if choice in CHOICE_MAPPING:
                print()
                return CHOICE_MAPPING[choice]
            print(f"   {UI.RED}✖ Invalid choice. Please enter 1, 2, 3, 4, 5 or dept name.{UI.RESET}")
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n {UI.YELLOW}Operation cancelled by user.{UI.RESET}\n")
            sys.exit(0)


def download_file(item, base_dir: Path, force: bool = False):
    badge, tag_color, dept_folder, sem_folder, filename, url = item
    if sem_folder:
        target_dir = base_dir / dept_folder / sem_folder
    else:
        target_dir = base_dir / dept_folder

    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename

    # Check cache unless force is enabled
    if not force and target_path.exists() and target_path.stat().st_size > 1000:
        try:
            with open(target_path, "rb") as f:
                if f.read(5).startswith(b"%PDF"):
                    return (item, True, target_path.stat().st_size, "CACHED")
        except Exception:
            pass

    max_retries = 3
    last_error = ""
    for attempt in range(max_retries):
        try:
            data = None
            if HAVE_REQUESTS:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                resp = requests.get(url, headers=headers, timeout=30)
                if resp.status_code == 200:
                    data = resp.content
                else:
                    raise ConnectionError(f"HTTP {resp.status_code}")
            else:
                import urllib.request
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = resp.read()

            if not data or not data.startswith(b"%PDF"):
                raise ValueError("Payload is not a valid PDF file")

            with open(target_path, "wb") as f:
                f.write(data)

            return (item, True, len(data), "DOWNLOADED")
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                time.sleep(1)

    return (item, False, 0, last_error)


def export_questions_to_json(output_file: Path):
    export_data = {}
    total = 0
    for key, val in ALL_QUESTIONS.items():
        export_data[key] = {
            "name": val["name"],
            "folder": val["folder"],
            "papers": [
                {"semester": sem, "filename": fn, "url": url}
                for sem, fn, url in val["items"]
            ]
        }
        total += len(val["items"])
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    print(f"📄 Successfully exported {total} question paper records to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Sylhet Engineering College (SEC) Official Question Archive Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python3 download_questions.py                  (Launches interactive visual menu)\n"
               "  python3 download_questions.py cse              (Download all CSE question papers)\n"
               "  python3 download_questions.py all -o ~/Archive (Download entire 41-paper bundle)\n"
               "  python3 download_questions.py --dry-run cse    (Preview CSE question list without downloading)\n"
    )
    parser.add_argument(
        "category",
        nargs="?",
        default=None,
        help="Department or category [cse, eee, civil/ce, admission/adm, all]"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Custom destination directory for downloaded archives"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=5,
        help="Number of concurrent download threads (default: 5)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download and overwrite existing cached PDF files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview matching files and URLs without downloading"
    )
    parser.add_argument(
        "--export-json",
        type=Path,
        default=None,
        help="Export the questions catalog to a JSON file and exit"
    )

    args = parser.parse_args()

    if args.export_json:
        export_questions_to_json(args.export_json)
        return

    print_banner()

    # 1. Environment & Storage Verification
    base_dir = run_environment_checks(custom_dest=args.output)

    # 2. Determine Category Selection
    if args.category:
        cat_lower = args.category.strip().lower()
        if cat_lower in CHOICE_MAPPING:
            chosen = CHOICE_MAPPING[cat_lower]
            print(f" {UI.AQUA}➔{UI.RESET} {UI.DIM}CLI Selection:{UI.RESET} {UI.BOLD}{UI.CYAN}{cat_lower.upper()}{UI.RESET}\n")
        else:
            print(f" {UI.AMBER}⚠ Notice:{UI.RESET} Unknown category '{args.category}'. Falling back to interactive menu.\n")
            print_menu()
            chosen = get_interactive_choice()
    else:
        print_menu()
        chosen = get_interactive_choice()

    download_list = []
    for dept_key in chosen:
        dept = ALL_QUESTIONS[dept_key]
        for sem_folder, fn, url in dept["items"]:
            download_list.append((dept["tag"], dept["badge_color"], dept["folder"], sem_folder, fn, url))

    w = UI.width()
    dept_tags = " ".join([f"{ALL_QUESTIONS[k]['badge_color']}[{ALL_QUESTIONS[k]['name']}]{UI.RESET}" for k in chosen])
    
    print(UI.box_top(w, title=f"{UI.BOLD}{UI.WHITE}ACTIVE DOWNLOAD QUEUE{UI.RESET}", border_color=UI.PURPLE))
    print(UI.box_line(f"  📂 {UI.BOLD}Destination:{UI.RESET} {UI.CYAN}{base_dir}/<Dept>/<Semester>/{UI.RESET}", w, border_color=UI.PURPLE))
    print(UI.box_line(f"  🏷️  {UI.BOLD}Categories:{UI.RESET}  {dept_tags}", w, border_color=UI.PURPLE))
    print(UI.box_line(f"  📦 {UI.BOLD}Total Files:{UI.RESET} {UI.YELLOW}{len(download_list)} PDFs{UI.RESET}", w, border_color=UI.PURPLE))
    if args.dry_run:
        print(UI.box_line(f"  ⚙️  {UI.BOLD}Mode:{UI.RESET}        {UI.YELLOW}DRY RUN (Preview Only){UI.RESET}", w, border_color=UI.PURPLE))
    print(UI.box_bottom(w, border_color=UI.PURPLE))
    print()

    if args.dry_run:
        print(f"📋 Question Catalog Preview ({len(download_list)} files):")
        for item in download_list:
            badge, tag_color, dept_folder, sem_folder, fn, url = item
            subpath = f"{dept_folder}/{sem_folder}/{fn}" if sem_folder else f"{dept_folder}/{fn}"
            print(f"  • {tag_color}[{badge}]{UI.RESET} {subpath}")
        print("\n✨ Dry run complete. No files were downloaded.")
        return

    start_time = time.time()
    total_files = len(download_list)
    success_count = 0
    fail_count = 0
    total_bytes = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(download_file, item, base_dir, args.force): item for item in download_list}
        for future in concurrent.futures.as_completed(futures):
            item, success, size, status = future.result()
            badge, tag_color, dept_folder, sem_folder, fn, url = item
            
            badge_str = f"{tag_color}[{badge:^5}]{UI.RESET}"
            size_mb = size / (1024 * 1024) if size > 0 else 0
            size_str = f"{size_mb:5.2f} MB"
            
            if sem_folder:
                display_path = f"{dept_folder}/{sem_folder}/{fn}"
            else:
                display_path = f"{dept_folder}/{fn}"

            max_fn_len = max(24, w - 34)
            display_fn = display_path if len(display_path) <= max_fn_len else ("..." + display_path[-(max_fn_len-3):])

            if success:
                success_count += 1
                total_bytes += size
                if status == "CACHED":
                    tag_status = f"{UI.MINT}✔ CACHED{UI.RESET}"
                else:
                    tag_status = f"{UI.GREEN}✔ DONE  {UI.RESET}"
                print(f" {tag_status} {badge_str} {UI.WHITE}{display_fn:<{max_fn_len}}{UI.RESET} {UI.DIM}{size_str}{UI.RESET}")
            else:
                fail_count += 1
                tag_status = f"{UI.RED}✖ FAIL  {UI.RESET}"
                err_hint = f" ({status[:20]})" if status else ""
                print(f" {tag_status} {badge_str} {UI.RED}{display_fn:<{max_fn_len}}{UI.RESET} {UI.RED}{err_hint}{UI.RESET}")

    elapsed = time.time() - start_time
    total_mb = total_bytes / (1024 * 1024)

    # Final Dashboard Card
    print()
    print(UI.box_top(w, border_color=UI.CYAN))
    header = f"✨ {UI.BOLD}{UI.WHITE}DOWNLOAD & VERIFICATION COMPLETE{UI.RESET} ✨"
    print(f"{UI.CYAN}│{UI.RESET}{UI.center_text(header, w - 2)}{UI.CYAN}│{UI.RESET}")
    print(UI.box_divider(w, border_color=UI.CYAN))

    stat_dir  = f"  📁 {UI.BOLD}Base Storage Path:{UI.RESET} {UI.CYAN}{base_dir}/<Dept>/<Semester>/{UI.RESET}"
    percent   = int(success_count / total_files * 100) if total_files > 0 else 0
    stat_rate = f"  📊 {UI.BOLD}Success Rate:{UI.RESET}      {UI.GREEN}{success_count}/{total_files} ({percent}%){UI.RESET}"
    stat_size = f"  💾 {UI.BOLD}Total Data Size:{UI.RESET}   {UI.YELLOW}{total_mb:.2f} MB{UI.RESET}"
    stat_time = f"  ⏱️  {UI.BOLD}Duration:{UI.RESET}         {UI.WHITE}{elapsed:.2f} seconds{UI.RESET}"
    stat_msg  = f"  🚀 {UI.BOLD}Status:{UI.RESET}           {UI.MINT}All papers organized by Dept ➔ Semester!{UI.RESET}"

    for row in [stat_dir, stat_rate, stat_size, stat_time, stat_msg]:
        print(UI.box_line(row, w, border_color=UI.CYAN))

    print(UI.box_bottom(w, border_color=UI.CYAN))
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n {UI.YELLOW}Process interrupted by user. Exiting.{UI.RESET}\n")
        sys.exit(130)

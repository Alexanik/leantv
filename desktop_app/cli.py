#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android TV Optimizer & Debloater - Interactive Terminal CLI
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import List, Set, Dict, Optional

# Enable ANSI escape sequences on Windows
if sys.platform == "win32":
    os.system("")

# ANSI Color Codes
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BG_BLUE = "\033[44m"

# Ensure core package is accessible
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.adb_client import ADBClient
from core.device_detector import DeviceDetector, DeviceInfo
from core.database import DATABASE, get_package_info, get_category_title, PackageMeta
from core.debloater import Debloater
from core.ram_monitor import RAMMonitor, RAMSnapshot
from core.launcher_installer import LauncherInstaller
from core.network_scanner import NetworkScanner, DiscoveredTV
from core.i18n import t, get_lang, set_lang, toggle_lang


def clear_screen():
    # Only clear if terminal is standard
    if sys.stdout.isatty():
        os.system("cls" if sys.platform == "win32" else "clear")


def print_banner():
    subtitle = t("banner_subtitle")
    banner = f"""
{C.CYAN}{C.BOLD}╔════════════════════════════════════════════════════════════════════════════╗
║                                ⚡ LeanTV ⚡                                ║
║         {subtitle.center(66)}         ║
║                     macOS  •  Windows  •  Linux                            ║
╚════════════════════════════════════════════════════════════════════════════╝{C.RESET}
"""
    print(banner)


def print_guide():
    guide = f"""  {C.YELLOW}{C.BOLD}{t("guide_title")}{C.RESET}
  {t("guide_step1")}
  {C.DIM}{t("guide_step1_sub")}{C.RESET}
  {t("guide_step2")}
  {C.DIM}{t("guide_step2_sub")}{C.RESET}
  {t("guide_step3")}
  {t("guide_step3_sub")}
  {t("guide_step4")}
  {t("guide_step4_sub")}
  {C.YELLOW}{t("guide_bottom")}{C.RESET}
"""
    print(guide)


def draw_progress_bar(percent: float, width: int = 30) -> str:
    filled = int(width * (percent / 100.0))
    bar = "█" * filled + "░" * (width - filled)
    if percent < 60:
        col = C.GREEN
    elif percent < 80:
        col = C.YELLOW
    else:
        col = C.RED
    return f"{col}[{bar}] {percent:.1f}%{C.RESET}"


def get_backup_file_path() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    return os.path.join(parent_dir, "backup_history.json")


def save_backup_packages(packages: List[str]):
    filepath = get_backup_file_path()
    existing = set()
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                existing = set(data.get("uninstalled", []))
        except Exception:
            pass
    existing.update(packages)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({"uninstalled": sorted(list(existing)), "updated": datetime.now().isoformat()}, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"{C.RED}Error saving rollback history: {e}{C.RESET}")


def load_backup_packages() -> List[str]:
    filepath = get_backup_file_path()
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("uninstalled", [])
        except Exception:
            pass
    return []


def get_config_file_path() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    return os.path.join(parent_dir, ".config.json")


def load_last_ip() -> Optional[str]:
    filepath = get_config_file_path()
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("last_ip")
        except Exception:
            pass
    return None


def save_last_ip(ip: str):
    filepath = get_config_file_path()
    data = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
    data["last_ip"] = ip
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


class TVOptimizerCLI:
    def __init__(self):
        self.adb = ADBClient()
        self.device_info: Optional[DeviceInfo] = None
        self.installed_packages: List[PackageMeta] = []
        self.ram_before: Optional[RAMSnapshot] = None
        self.ram_after: Optional[RAMSnapshot] = None

    def start(self):
        clear_screen()
        print_banner()
        print_guide()

        # Step 1: Check ADB
        if not self._check_adb():
            return

        # Step 2: Connect
        if not self._connection_wizard():
            return

        # Step 3: Device Info & RAM Profile
        self._analyze_device()

        # Step 4: Main Interactive Loop
        self._main_menu()

    def _check_adb(self) -> bool:
        print(f"{C.BOLD}{t('step_check_adb')}{C.RESET}")
        if self.adb.is_available():
            print(f"  {C.GREEN}{t('adb_found')}{C.RESET} {self.adb.adb_path}\n")
            return True
        else:
            print(f"  {C.RED}{t('adb_not_found')}{C.RESET}")
            print(f"  {t('adb_manual_prompt')}")
            custom_path = input(f"  {C.YELLOW}{t('adb_prompt_path')}{C.RESET}").strip()
            if custom_path and os.path.exists(custom_path):
                self.adb = ADBClient(custom_path)
                if self.adb.is_available():
                    print(f"  {C.GREEN}{t('adb_success')}{C.RESET}\n")
                    return True
            print(f"  {C.RED}{t('adb_error')}{C.RESET}")
            return False

    def _connection_wizard(self) -> bool:
        while True:
            print(f"{C.BOLD}{t('step_connect')}{C.RESET}")
            devices = self.adb.get_devices()
            online_devices = [d for d in devices if d[1] == "device"]

            if online_devices:
                print(f"  {t('active_connections')}")
                for idx, (dev_id, status) in enumerate(online_devices, 1):
                    print(f"   [{idx}] {C.CYAN}{dev_id}{C.RESET} ({status})")
                print(f"   [S] {t('btn_auto_scan')}")
                print(f"   [N] {t('btn_manual_ip')}")
                print(f"   [R] {t('btn_refresh')}")
                print(f"   [L] {t('btn_switch_lang')}")
                print(f"   [0] {t('btn_exit')}")

                choice = input(f"\n  {C.YELLOW}{t('prompt_choice')}{C.RESET}").strip() or "1"
                if choice == "0":
                    return False
                elif choice.upper() == "L":
                    toggle_lang()
                    print(f"  {C.GREEN}{t('lang_switched')}{C.RESET}\n")
                    continue
                elif choice.upper() == "R":
                    continue
                elif choice.upper() == "S":
                    if self._scan_and_select_tv():
                        return True
                elif choice.upper() == "N":
                    if self._prompt_wifi_connect():
                        return True
                elif choice.isdigit() and 1 <= int(choice) <= len(online_devices):
                    selected = online_devices[int(choice) - 1][0]
                    self.adb.selected_device = selected
                    print(f"  {C.GREEN}{t('device_selected')} {selected}{C.RESET}\n")
                    return True
                else:
                    print(f"  {C.RED}{t('invalid_choice')}{C.RESET}")
            else:
                print(f"  {C.YELLOW}{t('no_connections')}{C.RESET}")
                print(f"   [1] {t('btn_auto_scan_rec')}")
                print(f"   [2] {t('btn_manual_ip')}")
                print(f"   [?] {t('btn_guide')}")
                print(f"   [R] {t('btn_check_active')}")
                print(f"   [L] {t('btn_switch_lang')}")
                print(f"   [0] {t('btn_exit')}")

                choice = input(f"\n  {C.YELLOW}{t('prompt_choice')}{C.RESET}").strip() or "1"
                if choice.upper() == "L":
                    toggle_lang()
                    print(f"  {C.GREEN}{t('lang_switched')}{C.RESET}\n")
                    continue
                elif choice == "1" or choice.upper() == "S":
                    if self._scan_and_select_tv():
                        return True
                elif choice == "2" or choice.upper() == "N":
                    if self._prompt_wifi_connect():
                        return True
                elif choice == "?":
                    print_guide()
                elif choice.upper() == "R":
                    continue
                elif choice == "0":
                    return False
                else:
                    print(f"  {C.RED}{t('invalid_choice')}{C.RESET}")

    def _scan_and_select_tv(self) -> bool:
        print(f"\n  {C.CYAN}{t('scanning_network')}{C.RESET}")
        discovered = NetworkScanner.scan_network()

        if not discovered:
            print(f"  {C.YELLOW}{t('no_tvs_found')}{C.RESET}")
            return self._prompt_wifi_connect()

        print(f"\n  {C.BOLD}{t('found_tvs')}{C.RESET}")
        for idx, tv in enumerate(discovered, 1):
            source_tag = f"{C.DIM}[{tv.source}]{C.RESET}"
            print(f"   [{idx}] {C.GREEN}{tv.ip}{C.RESET}:{tv.port}  {C.BOLD}{tv.friendly_name}{C.RESET} {source_tag}")

        print(f"   [M] {t('btn_manual_ip')}")
        print(f"   [0] {t('rollback_opt_back')}")

        choice = input(f"\n  {C.YELLOW}{t('prompt_choice')}{C.RESET}").strip() or "1"
        if choice == "0":
            return False
        elif choice.upper() == "M":
            return self._prompt_wifi_connect()
        elif choice.isdigit() and 1 <= int(choice) <= len(discovered):
            selected_tv = discovered[int(choice) - 1]
            return self._connect_to_endpoint(selected_tv.ip, selected_tv.port)
        return False

    def _prompt_wifi_connect(self) -> bool:
        last_ip = load_last_ip()
        prompt_text = f"  {C.YELLOW}{t('enter_ip')}"
        if last_ip:
            prompt_text += f"[{last_ip}]: {C.RESET}"
        else:
            prompt_text += f"{C.RESET}"

        ip = input(prompt_text).strip()
        if not ip and last_ip:
            ip = last_ip

        if not ip:
            return False

        save_last_ip(ip)
        return self._connect_to_endpoint(ip, 5555)

    def _connect_to_endpoint(self, ip: str, port: int = 5555) -> bool:
        endpoint = f"{ip}:{port}"
        print(f"  {t('connecting_to')} {endpoint}...")
        ok, msg = self.adb.connect_device(endpoint)
        if ok:
            print(f"  {C.GREEN}{t('connect_success')} {endpoint}!{C.RESET}\n")
            self.adb.selected_device = endpoint
            return True
        else:
            print(f"  {C.RED}{t('connect_failed')} {endpoint}: {msg}{C.RESET}")
            print_guide()
            return False

    def _analyze_device(self):
        print(f"{C.BOLD}{t('diag_title')}{C.RESET}")
        self.device_info = DeviceDetector.get_device_info(self.adb)
        print(f"  {t('diag_tv')}    {C.CYAN}{self.device_info.tv_name}{C.RESET}")
        print(f"  {t('diag_model')} {self.device_info.model}")
        print(f"  {t('diag_os')}    Android {self.device_info.android_version} (API {self.device_info.api_level})\n")

        self.installed_packages = Debloater.scan_installed_packages(self.adb)
        self.ram_before = RAMMonitor.get_snapshot(self.adb)
        self._show_ram_profile()

    def _show_ram_profile(self):
        if self.ram_before:
            r = self.ram_before
            print(f"  {draw_progress_bar(r.used_percent)}")
            print(f"  • {t('diag_ram_total')}     {C.BOLD}{r.total_mb:.0f} MB{C.RESET} ({r.total_mb/1024.0:.1f} GB)")
            print(f"  • {t('diag_ram_used')} {C.YELLOW}{r.used_mb:.0f} MB{C.RESET} ({r.used_percent:.0f}%)")
            print(f"  • {t('diag_ram_free')}      {C.GREEN}{r.free_mb:.0f} MB{C.RESET}")

            if r.top_consumers:
                print(f"\n  {C.BOLD}{t('diag_top_consumers')}{C.RESET}")
                for idx, p in enumerate(r.top_consumers[:6], 1):
                    print(f"   {idx}. {p.title:<35} {C.CYAN}{p.ram_mb:>5.0f} MB{C.RESET}  {C.DIM}({p.process_name}){C.RESET}")
            print()
        else:
            print(f"  {C.YELLOW}{t('diag_ram_failed')}{C.RESET}\n")

    def _main_menu(self):
        while True:
            print(f"{C.BOLD}{C.CYAN}{t('menu_header')}{C.RESET}")
            print(f" [{C.GREEN}1{C.RESET}] {t('menu_opt1')}")
            print(f"     {t('menu_opt1_desc1')}")
            print(f"     {t('menu_opt1_desc2')}")
            print(f"     {t('menu_opt1_desc3')}")
            print(f"     {t('menu_opt1_desc4')}")
            print(f"     {t('menu_opt1_desc5')}")
            print(f"     {t('menu_opt1_desc6')}")
            print()
            print(f" [{C.CYAN}2{C.RESET}] {t('menu_opt2')}")
            print(f" [{C.CYAN}3{C.RESET}] {t('menu_opt3')}")
            print(f" [{C.CYAN}4{C.RESET}] {t('menu_opt4')}")
            print(f" [{C.CYAN}5{C.RESET}] {t('menu_opt5')}")
            print(f" [{C.CYAN}6{C.RESET}] {t('menu_opt6')}")
            print(f" [{C.CYAN}7{C.RESET}] {t('menu_opt7')}")
            print(f" [{C.CYAN}8{C.RESET}] {t('menu_opt8')}")
            print(f" [{C.CYAN}0{C.RESET}] {t('menu_opt0')}")
            print(f"{C.CYAN}{t('menu_footer')}{C.RESET}")

            choice = input(f"\n{C.YELLOW}{t('menu_prompt')}{C.RESET}").strip() or "1"

            if choice == "1":
                self._run_recommended_optimization()
            elif choice == "2":
                self._manual_selection_mode()
            elif choice == "3":
                self._install_launcher_only()
            elif choice == "4":
                self._revoke_permissions_only()
            elif choice == "5":
                self._show_ram_profile()
            elif choice == "6":
                self._take_quick_screenshot()
            elif choice == "7":
                self._rollback_wizard()
            elif choice == "8":
                toggle_lang()
                print(f"\n{C.GREEN}{t('lang_switched')}{C.RESET}\n")
            elif choice == "0":
                print(f"\n{C.GREEN}{t('goodbye')}{C.RESET}\n")
                break
            else:
                print(f"{C.RED}{t('menu_invalid')}{C.RESET}")

    def _run_recommended_optimization(self):
        rec_pkgs = [p.package_name for p in self.installed_packages if p.recommended_action in ["REMOVE", "DISABLE"] and p.risk_level != "CRITICAL"]

        if not rec_pkgs:
            print(f"\n{C.GREEN}{t('rec_all_clean')}{C.RESET}")
            confirm = input(t('rec_already_clean_prompt')).strip().lower() or "y"
            if confirm != "y":
                return
        else:
            print(f"\n{C.BOLD}{t('rec_prep_title')}{C.RESET}")
            print(t('rec_found_bloat', count=len(rec_pkgs)))
            for pkg in rec_pkgs:
                meta = get_package_info(pkg)
                print(f"   {C.RED}✖{C.RESET} {meta.title}")

            confirm = input(f"\n{C.YELLOW}{t('rec_confirm_prompt')}{C.RESET}").strip().lower() or "y"
            if confirm != "y":
                print(f"{C.DIM}{t('cancelled_by_user')}{C.RESET}\n")
                return

        self._execute_pipeline(
            packages_to_remove=rec_pkgs,
            revoke_perms=True,
            install_launcher=True,
            disable_stock=True
        )

    def _manual_selection_mode(self):
        print(f"\n{C.BOLD}{t('manual_cat_title')}{C.RESET}")
        cat_keys = ["vendor_bloat", "google_bloat", "streaming", "other", "safe_system"]

        indexed_list = []
        for cat in cat_keys:
            cat_pkgs = [p for p in self.installed_packages if p.category == cat]
            if not cat_pkgs:
                continue
            cat_name = get_category_title(cat)
            print(f"\n{C.CYAN}{C.BOLD}--- {cat_name} ---{C.RESET}")
            for p in cat_pkgs:
                indexed_list.append(p)
                idx = len(indexed_list)
                risk_tag = ""
                if p.risk_level == "CRITICAL":
                    risk_tag = f" {C.RED}{t('manual_protected')}{C.RESET}"
                elif p.recommended_action in ["REMOVE", "DISABLE"]:
                    risk_tag = f" {C.GREEN}{t('manual_rec_delete')}{C.RESET}"

                print(f"  [{idx:2d}] {p.title:<42}{risk_tag}")

        print(f"\n{C.YELLOW}{t('manual_prompt')}{C.RESET}")
        print(f"{C.DIM}{t('manual_prompt_sub')}{C.RESET}")
        raw = input(f"{t('rollback_action_prompt')}").strip()

        if not raw or raw == "0":
            return

        selected_pkgs = []
        if raw.lower() == "all_rec":
            selected_pkgs = [p.package_name for p in indexed_list if p.recommended_action in ["REMOVE", "DISABLE"] and p.risk_level != "CRITICAL"]
        else:
            parts = raw.replace(",", " ").split()
            for part in parts:
                if "-" in part:
                    sub = part.split("-")
                    if len(sub) == 2 and sub[0].isdigit() and sub[1].isdigit():
                        start, end = int(sub[0]), int(sub[1])
                        for i in range(start, end + 1):
                            if 1 <= i <= len(indexed_list):
                                p = indexed_list[i - 1]
                                if p.risk_level != "CRITICAL":
                                    selected_pkgs.append(p.package_name)
                                else:
                                    print(f"  {C.RED}{t('manual_skipped_crit', title=p.title)}{C.RESET}")
                elif part.isdigit():
                    i = int(part)
                    if 1 <= i <= len(indexed_list):
                        p = indexed_list[i - 1]
                        if p.risk_level != "CRITICAL":
                            selected_pkgs.append(p.package_name)
                        else:
                            print(f"  {C.RED}{t('manual_skipped_crit', title=p.title)}{C.RESET}")

        selected_pkgs = list(dict.fromkeys(selected_pkgs))
        if not selected_pkgs:
            print(f"{C.YELLOW}{t('manual_none_selected')}{C.RESET}\n")
            return

        print(f"\n{C.BOLD}{t('manual_selected_count', count=len(selected_pkgs))}{C.RESET}")
        for pkg in selected_pkgs:
            m = get_package_info(pkg)
            print(f"  • {m.title}")

        confirm = input(f"\n{C.YELLOW}{t('manual_confirm_prompt', count=len(selected_pkgs))}{C.RESET}").strip().lower() or "y"
        if confirm != "y":
            print(f"{C.DIM}{t('cancelled_by_user')}{C.RESET}\n")
            return

        print(f"\n{C.BOLD}{C.CYAN}{t('manual_removing_header')}{C.RESET}")
        removed_list = []
        for pkg in selected_pkgs:
            meta = get_package_info(pkg)
            sys.stdout.write(f"  {t('manual_removing_item', title=meta.title)}")
            sys.stdout.flush()
            success = Debloater.uninstall_package(self.adb, pkg)
            if success:
                print(f"{C.GREEN}{t('manual_success')}{C.RESET}")
                removed_list.append(pkg)
            else:
                print(f"{C.RED}{t('manual_error')}{C.RESET}")

        if removed_list:
            save_backup_packages(removed_list)
            self.adb.shell("am kill-all")
            self.installed_packages = Debloater.scan_installed_packages(self.adb)

        print(f"\n{C.GREEN}{t('manual_done', success=len(removed_list), total=len(selected_pkgs))}{C.RESET}\n")
        input(f"{C.DIM}{t('press_enter')}{C.RESET}")

    def _execute_pipeline(self, packages_to_remove: List[str], revoke_perms: bool, install_launcher: bool, disable_stock: bool):
        screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tv_screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"\n{C.BOLD}{C.CYAN}{t('pipeline_header')}{C.RESET}")

        # 1. Screenshot BEFORE
        print(f"\n[1/5] {C.BOLD}{t('pipeline_step1')}{C.RESET}")
        before_file = os.path.join(screenshots_dir, f"screen_BEFORE_{timestamp}.png")
        ok, res = self.adb.capture_screenshot(before_file)
        if ok:
            print(f"  {C.GREEN}{t('pipeline_screen_saved')}{C.RESET} {before_file}")
        else:
            print(f"  {C.YELLOW}{t('pipeline_screen_err')} ({res}){C.RESET}")

        # 2. Debloat
        if packages_to_remove:
            print(f"\n[2/5] {C.BOLD}{t('pipeline_step2', count=len(packages_to_remove))}{C.RESET}")
            removed_list = []
            for pkg in packages_to_remove:
                meta = get_package_info(pkg)
                sys.stdout.write(f"  {t('pipeline_item_removing', title=meta.title)}")
                sys.stdout.flush()
                success = Debloater.uninstall_package(self.adb, pkg)
                if success:
                    print(f"{C.GREEN}{t('pipeline_item_success')}{C.RESET}")
                    removed_list.append(pkg)
                else:
                    print(f"{C.YELLOW}{t('pipeline_item_skipped')}{C.RESET}")
            save_backup_packages(removed_list)
            print(f"  {C.GREEN}{t('pipeline_debloat_total', count=len(removed_list))}{C.RESET}")
        else:
            print(f"\n[2/5] {C.DIM}{t('pipeline_step2_skip')}{C.RESET}")

        # 3. Revoke permissions
        if revoke_perms:
            print(f"\n[3/5] {C.BOLD}{t('pipeline_step3')}{C.RESET}")
            Debloater.revoke_telemetry_permissions(self.adb, ["com.google.android.katniss", "com.xiaomi.statistic"])
            print(f"  {C.GREEN}{t('pipeline_perms_done')}{C.RESET}")
        else:
            print(f"\n[3/5] {C.DIM}{t('pipeline_step3_skip')}{C.RESET}")

        # 4. Launcher Install
        if install_launcher:
            print(f"\n[4/5] {C.BOLD}{t('pipeline_step4')}{C.RESET}")
            ok, msg = LauncherInstaller.install_and_activate(
                self.adb,
                disable_stock_launchers=disable_stock,
                status_callback=lambda s: print(f"  • {s}")
            )
            if ok:
                print(f"  {C.GREEN}{t('pipeline_launcher_success')}{C.RESET}")
            else:
                print(f"  {C.RED}{t('pipeline_launcher_err', msg=msg)}{C.RESET}")
        else:
            print(f"\n[4/5] {C.DIM}{t('pipeline_step4_skip')}{C.RESET}")

        # Stabilize and flush memory
        print(f"\n  {C.DIM}{t('pipeline_flushing')}{C.RESET}")

        # Wait for any background dex2oat compiler to exit
        for _ in range(8):
            c_dex, out_dex = self.adb.shell("pgrep dex2oat")
            if not out_dex.strip():
                break
            time.sleep(1)

        # Flush dead processes from RAM
        self.adb.shell("am kill-all")
        time.sleep(2)

        # 5. Measure RAM AFTER & Screenshot AFTER
        print(f"\n[5/5] {C.BOLD}{t('pipeline_step5')}{C.RESET}")
        self.ram_after = RAMMonitor.get_snapshot(self.adb)

        # Refresh installed packages list
        self.installed_packages = Debloater.scan_installed_packages(self.adb)

        # Print comparison report
        print(f"\n{C.GREEN}{C.BOLD}{t('pipeline_results_header')}{C.RESET}")

        if self.ram_before and self.ram_after:
            b = self.ram_before
            a = self.ram_after
            freed = b.used_mb - a.used_mb
            print(f"  {t('pipeline_ram_before', used=b.used_mb, total=b.total_mb, percent=b.used_percent)}")
            print(f"  {t('pipeline_ram_after', used=a.used_mb, total=a.total_mb, percent=a.used_percent)}")
            if freed > 0:
                print(f"  {C.GREEN}{C.BOLD}{t('pipeline_ram_freed', freed=freed, percent=((freed/b.total_mb)*100))}{C.RESET}")
            else:
                print(f"  {t('pipeline_ram_stable', free=a.free_mb)}")
        print()

        # Screenshot AFTER
        after_file = os.path.join(screenshots_dir, f"screen_AFTER_{timestamp}.png")
        ok, res = self.adb.capture_screenshot(after_file)
        if ok:
            print(f"  {t('pipeline_screen_after_saved', path=after_file)}")

        print(f"\n{C.BOLD}{C.GREEN}{t('pipeline_done')}{C.RESET}\n")
        input(f"{C.DIM}{t('press_enter')}{C.RESET}")

    def _install_launcher_only(self):
        print(f"\n{C.BOLD}{t('install_launcher_title')}{C.RESET}")
        disable_stock = input(t('install_launcher_disable_prompt')).strip().lower() or "y"
        ok, msg = LauncherInstaller.install_and_activate(
            self.adb,
            disable_stock_launchers=(disable_stock == "y"),
            status_callback=lambda s: print(f"  • {s}")
        )
        if ok:
            print(f"{C.GREEN}{t('install_launcher_success')}{C.RESET}\n")
        else:
            print(f"{C.RED}{t('install_launcher_error', msg=msg)}{C.RESET}\n")

    def _revoke_permissions_only(self):
        print(f"\n{C.BOLD}{t('revoke_perms_title')}{C.RESET}")
        Debloater.revoke_telemetry_permissions(self.adb, ["com.google.android.katniss", "com.xiaomi.statistic"])
        print(f"{C.GREEN}{t('revoke_perms_done')}{C.RESET}\n")

    def _take_quick_screenshot(self):
        screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tv_screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(screenshots_dir, f"quick_screenshot_{timestamp}.png")
        print(f"  {C.DIM}{t('screenshot_taking')}{C.RESET}")
        ok, res = self.adb.capture_screenshot(filepath)
        if ok:
            print(f"{C.GREEN}{t('screenshot_success', path=filepath)}{C.RESET}\n")
        else:
            print(f"{C.RED}{t('screenshot_err', msg=res)}{C.RESET}\n")

    def _rollback_wizard(self):
        print(f"\n{C.BOLD}{C.CYAN}{t('rollback_header')}{C.RESET}")
        history = load_backup_packages()

        if not history:
            print(f"  {C.YELLOW}{t('rollback_empty')}{C.RESET}")
            pkg = input(f"  {t('rollback_manual_prompt')}").strip()
            if pkg:
                ok = Debloater.restore_package(self.adb, pkg)
                if ok:
                    print(f"  {C.GREEN}{t('rollback_item_restored', pkg=pkg)}{C.RESET}\n")
                else:
                    print(f"  {C.RED}{t('rollback_item_err', pkg=pkg)}{C.RESET}\n")
            return

        print(f"  {t('rollback_list_title', count=len(history))}")
        for idx, pkg in enumerate(history, 1):
            meta = get_package_info(pkg)
            print(f"   [{idx:2d}] {meta.title}")

        print(f"\n  {t('rollback_opt_all')}")
        print(f"  {t('rollback_opt_sel')}")
        print(f"  {t('rollback_opt_back')}")

        choice = input(f"\n  {C.YELLOW}{t('rollback_action_prompt')}{C.RESET}").strip()
        if not choice or choice == "0":
            return

        to_restore = []
        if choice.upper() == "A":
            to_restore = history
        else:
            for part in choice.replace(",", " ").split():
                if part.isdigit():
                    idx = int(part)
                    if 1 <= idx <= len(history):
                        to_restore.append(history[idx - 1])

        if not to_restore:
            print(f"  {C.YELLOW}{t('rollback_nothing_sel')}{C.RESET}\n")
            return

        print(f"\n  {t('rollback_restoring_count', count=len(to_restore))}")
        for pkg in to_restore:
            meta = get_package_info(pkg)
            ok = Debloater.restore_package(self.adb, pkg)
            status = f"{C.GREEN}{t('rollback_status_restored')}{C.RESET}" if ok else f"{C.RED}{t('rollback_status_err')}{C.RESET}"
            print(f"   • {meta.title}: {status}")

        print(f"\n  {C.GREEN}{t('rollback_done')}{C.RESET}\n")


def main():
    try:
        app = TVOptimizerCLI()
        app.start()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{C.YELLOW}Goodbye! / До свидания!{C.RESET}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()

import time
from typing import List, Dict, Callable, Optional, Set
from .adb_client import ADBClient
from .database import PackageMeta, get_package_info

class Debloater:
    @staticmethod
    def get_installed_packages(adb: ADBClient) -> List[PackageMeta]:
        # Query active packages using robust fallback chain
        out = ""
        for cmd in ["pm list packages --user 0", "pm list packages", "cmd package list packages"]:
            code, cmd_out = adb.shell(cmd)
            if "package:" in cmd_out:
                out = cmd_out
                break

        if not out.strip() or "package:" not in out:
            # Fallback: query 3rd-party and system packages separately
            _, cmd_3 = adb.shell("pm list packages -3")
            _, cmd_s = adb.shell("pm list packages -s")
            combined = f"{cmd_3}\n{cmd_s}"
            if "package:" in combined:
                out = combined

        installed_pkgs = []
        seen = set()
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("package:"):
                pkg_name = line.replace("package:", "").strip()
                if pkg_name and pkg_name not in seen:
                    seen.add(pkg_name)
                    meta = get_package_info(pkg_name)
                    installed_pkgs.append(meta)

        # Sort: Vendor bloat first, then Google bloat, then Streaming, Other, Safe
        order_map = {"vendor_bloat": 0, "google_bloat": 1, "streaming": 2, "other": 3, "safe_system": 4}
        installed_pkgs.sort(key=lambda x: (order_map.get(x.category, 5), x.package_name))
        return installed_pkgs

    @staticmethod
    def get_uninstalled_packages(adb: ADBClient) -> List[PackageMeta]:
        code1, out1 = adb.shell("pm list packages -u")
        code2, out2 = adb.shell("pm list packages --user 0")
        if code1 != 0:
            return []
        all_pkgs = {line.replace("package:", "").strip() for line in out1.splitlines() if line.startswith("package:")}
        active_pkgs = {line.replace("package:", "").strip() for line in out2.splitlines() if line.startswith("package:")} if code2 == 0 else set()
        uninstalled = all_pkgs - active_pkgs
        return [get_package_info(p) for p in sorted(uninstalled)]

    # Alias for convenience
    scan_installed_packages = get_installed_packages

    @classmethod
    def uninstall_package(cls, adb: ADBClient, pkg: str) -> bool:
        res = cls.remove_packages(adb, [pkg])
        return res.get(pkg, False)

    @classmethod
    def restore_package(cls, adb: ADBClient, pkg: str) -> bool:
        res = cls.restore_packages(adb, [pkg])
        return res.get(pkg, False)

    @staticmethod
    def get_disabled_packages(adb: ADBClient) -> Set[str]:
        code, out = adb.shell("pm list packages -d")
        if code != 0:
            return set()
        disabled = set()
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("package:"):
                disabled.add(line.replace("package:", "").strip())
        return disabled

    @staticmethod
    def remove_packages(
        adb: ADBClient,
        packages: List[str],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, bool]:
        results = {}
        total = len(packages)

        for i, pkg in enumerate(packages):
            if progress_callback:
                progress_callback(f"Удаление: {pkg}...", i / total)

            # Critical protection check
            meta = get_package_info(pkg)
            if meta.risk_level == "CRITICAL":
                results[pkg] = False
                continue

            # Force stop process first to immediately free RAM
            adb.shell(f"am force-stop {pkg}")
            code, out = adb.shell(f"pm uninstall -k --user 0 {pkg}")
            success = "success" in out.lower()
            if not success:
                # If uninstall is not allowed, try disabling
                code_d, out_d = adb.shell(f"pm disable-user --user 0 {pkg}")
                success = "disabled" in out_d.lower() or "new state: disabled" in out_d.lower()

            results[pkg] = success
            time.sleep(0.05)

        if progress_callback:
            progress_callback("Удаление завершено", 1.0)
        return results

    @staticmethod
    def disable_packages(
        adb: ADBClient,
        packages: List[str],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, bool]:
        results = {}
        total = len(packages)

        for i, pkg in enumerate(packages):
            if progress_callback:
                progress_callback(f"Отключение: {pkg}...", i / total)

            code, out = adb.shell(f"pm disable-user --user 0 {pkg}")
            success = "new state: disabled" in out.lower() or "disabled" in out.lower()
            results[pkg] = success
            time.sleep(0.05)

        if progress_callback:
            progress_callback("Отключение завершено", 1.0)
        return results

    @staticmethod
    def revoke_telemetry_permissions(
        adb: ADBClient,
        packages: List[str],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ):
        dangerous_perms = [
            "android.permission.RECORD_AUDIO",
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.ACCESS_COARSE_LOCATION",
            "android.permission.CAMERA"
        ]

        total = len(packages)
        for i, pkg in enumerate(packages):
            if progress_callback:
                progress_callback(f"Ограничение прав: {pkg}...", i / total)

            for perm in dangerous_perms:
                adb.shell(f"pm revoke {pkg} {perm} 2>/dev/null")

        if progress_callback:
            progress_callback("Права ограничены", 1.0)

    @staticmethod
    def restore_packages(
        adb: ADBClient,
        packages: List[str],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> Dict[str, bool]:
        results = {}
        total = len(packages)

        for i, pkg in enumerate(packages):
            if progress_callback:
                progress_callback(f"Восстановление: {pkg}...", i / total)

            # Try restoring user 0 package
            code, out = adb.shell(f"pm install-existing --user 0 {pkg}")
            success = "installed" in out.lower() or "package" in out.lower()
            if not success:
                # Also try enabling if it was disabled
                code2, out2 = adb.shell(f"pm enable {pkg}")
                success = "enabled" in out2.lower()

            results[pkg] = success

        if progress_callback:
            progress_callback("Восстановление завершено", 1.0)
        return results

import os
import sys
import subprocess
import shutil
import time
from typing import List, Tuple, Optional

class ADBClient:
    def __init__(self, custom_adb_path: Optional[str] = None):
        self.adb_path = custom_adb_path or self._find_adb()
        self.selected_device: Optional[str] = None

    def _find_adb(self) -> str:
        exe_name = "adb.exe" if sys.platform == "win32" else "adb"
        os_dir = "windows" if sys.platform == "win32" else ("macos" if sys.platform == "darwin" else "linux")

        # 1. Check bundled ADB in PyInstaller runtime (frozen single-file bundle)
        if hasattr(sys, "_MEIPASS"):
            bundled_candidates = [
                os.path.join(sys._MEIPASS, "resources", "bin", os_dir, exe_name),
                os.path.join(sys._MEIPASS, "resources", "bin", exe_name),
                os.path.join(sys._MEIPASS, "resources", exe_name),
                os.path.join(sys._MEIPASS, "bin", os_dir, exe_name),
                os.path.join(sys._MEIPASS, "bin", exe_name),
                os.path.join(sys._MEIPASS, exe_name),
            ]
            for b in bundled_candidates:
                if os.path.isfile(b):
                    if sys.platform != "win32":
                        try:
                            os.chmod(b, 0o755)
                        except Exception:
                            pass
                    return b

        # 2. Check local project resources if running from source or repo
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_candidates = [
            os.path.join(base_dir, "resources", "bin", os_dir, exe_name),
            os.path.join(base_dir, "resources", "bin", exe_name),
            os.path.join(base_dir, "resources", exe_name),
            os.path.join(base_dir, "bin", os_dir, exe_name),
            os.path.join(base_dir, "bin", exe_name),
        ]
        for lb in local_candidates:
            if os.path.isfile(lb):
                if sys.platform != "win32":
                    try:
                        os.chmod(lb, 0o755)
                    except Exception:
                        pass
                return lb

        # 3. Check system PATH
        system_adb = shutil.which("adb")
        if system_adb:
            return system_adb

        # 4. Check platform-specific well-known paths
        home = os.path.expanduser("~")
        candidates = []

        if sys.platform == "darwin":
            candidates.extend([
                os.path.join(home, "Library/Android/sdk/platform-tools/adb"),
                "/opt/homebrew/bin/adb",
                "/usr/local/bin/adb",
                "/usr/bin/adb",
            ])
        elif sys.platform == "win32":
            local_appdata = os.environ.get("LOCALAPPDATA", "")
            candidates.extend([
                os.path.join(local_appdata, "Android", "Sdk", "platform-tools", "adb.exe"),
                r"C:\adb\adb.exe",
                r"C:\platform-tools\adb.exe",
            ])
        else:  # Linux
            candidates.extend([
                os.path.join(home, "Android/Sdk/platform-tools/adb"),
                "/usr/bin/adb",
                "/usr/local/bin/adb",
            ])

        for c in candidates:
            if os.path.isfile(c) and (sys.platform == "win32" or os.access(c, os.X_OK)):
                return c

        return "adb"  # fallback to PATH call

    def is_available(self) -> bool:
        try:
            res = self._run(["version"], timeout=5)
            return res[0] == 0
        except Exception:
            return False

    def _run(self, args: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        cmd = [self.adb_path]
        if self.selected_device:
            cmd.extend(["-s", self.selected_device])
        cmd.extend(args)

        try:
            # Hide console window on Windows
            creationflags = 0
            if sys.platform == "win32":
                creationflags = 0x08000000  # CREATE_NO_WINDOW

            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                creationflags=creationflags
            )
            out = proc.stdout.decode("utf-8", errors="replace")
            err = proc.stderr.decode("utf-8", errors="replace")
            return proc.returncode, out.strip(), err.strip()
        except subprocess.TimeoutExpired:
            return -1, "", "Команда превысила лимит времени (timeout)"
        except Exception as e:
            return -1, "", str(e)

    def connect(self, host: str, port: int = 5555) -> Tuple[bool, str]:
        endpoint = f"{host.strip()}:{port}"
        # We run direct command without -s since we are establishing connection
        cmd = [self.adb_path, "connect", endpoint]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            out = proc.stdout.decode("utf-8", errors="replace").strip()
            if "connected to" in out.lower() or "already connected" in out.lower():
                self.selected_device = endpoint
                return True, out
            return False, out
        except Exception as e:
            return False, str(e)

    def disconnect(self, endpoint: Optional[str] = None) -> Tuple[bool, str]:
        target = endpoint or self.selected_device
        cmd = [self.adb_path, "disconnect"]
        if target:
            cmd.append(target)
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            out = proc.stdout.decode("utf-8", errors="replace").strip()
            if self.selected_device == target:
                self.selected_device = None
            return True, out
        except Exception as e:
            return False, str(e)

    def get_devices(self) -> List[Tuple[str, str]]:
        """Returns list of tuples: (device_id, status)"""
        cmd = [self.adb_path, "devices"]
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
            out = proc.stdout.decode("utf-8", errors="replace").strip()
            lines = out.splitlines()
            devices = []
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 2:
                    devices.append((parts[0], parts[1]))
            return devices
        except Exception:
            return []

    def shell(self, cmd: str, timeout: int = 30) -> Tuple[int, str]:
        code, out, err = self._run(["shell", cmd], timeout=timeout)
        if code != 0 and err:
            return code, err
        return code, out

    def install(self, apk_path: str, timeout: int = 60) -> Tuple[bool, str]:
        code, out, err = self._run(["install", "-r", "-d", apk_path], timeout=timeout)
        combined = f"{out}\n{err}".strip()
        success = "success" in combined.lower()
        return success, combined

    def capture_screenshot(self, local_output_path: str) -> Tuple[bool, str]:
        remote_tmp = "/sdcard/tv_cleaner_screen.png"
        code1, out1 = self.shell(f"screencap -p {remote_tmp}")
        if code1 != 0:
            return False, f"Ошибка создания снимка на ТВ: {out1}"

        os.makedirs(os.path.dirname(os.path.abspath(local_output_path)), exist_ok=True)
        code2, out2, err2 = self._run(["pull", remote_tmp, local_output_path])
        self.shell(f"rm -f {remote_tmp}")

        if code2 == 0 and os.path.exists(local_output_path):
            return True, local_output_path
        return False, f"Ошибка скачивания снимка: {out2} {err2}"

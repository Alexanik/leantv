import os
import sys
import time
from typing import Tuple, Callable, Optional
from .adb_client import ADBClient

class LauncherInstaller:
    DEFAULT_APK_NAME = "lean_home.apk"

    @classmethod
    def get_bundled_apk_path(cls) -> str:
        # Check if running in PyInstaller bundle
        if hasattr(sys, "_MEIPASS"):
            bundle_path = os.path.join(sys._MEIPASS, "resources", cls.DEFAULT_APK_NAME)
            if os.path.exists(bundle_path):
                return bundle_path
            legacy = os.path.join(sys._MEIPASS, "resources", "minimal_launcher.apk")
            if os.path.exists(legacy):
                return legacy

        # Check in resources directory relative to source
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        res_path = os.path.join(base_dir, "resources", cls.DEFAULT_APK_NAME)
        if os.path.exists(res_path):
            return res_path
        legacy_res = os.path.join(base_dir, "resources", "minimal_launcher.apk")
        if os.path.exists(legacy_res):
            return legacy_res

        # Fallback to local working directory
        local_path = os.path.join(os.getcwd(), "resources", cls.DEFAULT_APK_NAME)
        if os.path.exists(local_path):
            return local_path

        return cls.DEFAULT_APK_NAME

    @classmethod
    def install_and_activate(
        cls,
        adb: ADBClient,
        custom_apk_path: Optional[str] = None,
        disable_stock_launchers: bool = True,
        status_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[bool, str]:
        apk_path = custom_apk_path or cls.get_bundled_apk_path()

        if not os.path.exists(apk_path):
            return False, f"Файл лаунчера не найден: {apk_path}"

        # Check if already installed on device
        code_chk, out_chk = adb.shell("pm list packages com.minimal.tvlauncher")
        already_installed = "com.minimal.tvlauncher" in out_chk

        from .i18n import get_lang
        is_en = (get_lang() == "en")

        action_name = ("Updating / reinstalling" if is_en else "Обновление / переустановка") if already_installed else ("Installing" if is_en else "Установка")
        if status_callback:
            status_callback(f"{action_name} лаунчера LeanHome ({os.path.basename(apk_path)})..." if not is_en else f"{action_name} LeanHome launcher ({os.path.basename(apk_path)})...")

        success, msg = adb.install(apk_path)
        if not success and already_installed:
            # If update failed (e.g. signature mismatch INSTALL_FAILED_UPDATE_INCOMPATIBLE,
            # version downgrade, or corrupted package state), perform clean uninstall and re-install
            if status_callback:
                status_callback(
                    "Detected signature/version incompatibility. Completely removing previous version..."
                    if is_en else
                    "Обнаружена несовместимость подписи/версии. Выполняем чистое удаление старой версии..."
                )
            adb.shell("pm uninstall com.minimal.tvlauncher")
            adb.shell("pm uninstall -k --user 0 com.minimal.tvlauncher")
            time.sleep(1)
            if status_callback:
                status_callback(
                    "Performing clean install of LeanHome launcher..."
                    if is_en else
                    "Чистая установка лаунчера LeanHome..."
                )
            success, msg = adb.install(apk_path)

        if not success:
            err_prefix = "Installation error" if is_en else "Ошибка установки APK"
            return False, f"{err_prefix}: {msg}"

        if disable_stock_launchers:
            if status_callback:
                status_callback("Назначение LeanHome лаунчером по умолчанию...")
            # Set LeanHome as default home activity so it handles Home button
            adb.shell("cmd package set-home-activity com.minimal.tvlauncher/.MainActivity")
            # Disable stock Google TV launcher so Home button exclusively opens LeanHome and frees 80-120 MB RAM
            adb.shell("pm disable-user --user 0 com.google.android.tvlauncher")
            # Disable PatchWall (ad-heavy Xiaomi home) if present
            adb.shell("pm disable-user --user 0 com.mitv.tvhome.atv")
            # Disable Projectivy if present
            adb.shell("pm disable-user --user 0 com.spocky.projengmenu")

        if status_callback:
            status_callback("Запуск лаунчера LeanHome на экране ТВ...")
        adb.shell("am start -n com.minimal.tvlauncher/.MainActivity")

        # Verify
        code, focus_out = adb.shell("dumpsys window | grep mCurrentFocus")
        if "com.minimal.tvlauncher" in focus_out:
            msg_res = "Лаунчер LeanHome успешно обновлен и запущен на ТВ!" if already_installed else "Лаунчер LeanHome успешно установлен и запущен на ТВ!"
            return True, msg_res
        else:
            return True, "Лаунчер установлен. Нажмите кнопку Домой на пульте ТВ."

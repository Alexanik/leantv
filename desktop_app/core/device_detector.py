from dataclasses import dataclass
from typing import Optional
from .adb_client import ADBClient

@dataclass
class DeviceInfo:
    manufacturer: str
    brand: str
    model: str
    market_name: str
    android_version: str
    sdk_version: str
    build_id: str
    resolution: str
    density: str
    is_xiaomi: bool
    is_tcl: bool
    is_sony: bool
    vendor_display: str

    @property
    def screen_resolution(self) -> str:
        return self.resolution

    @property
    def display_title(self) -> str:
        name = self.market_name or self.model
        return f"{self.vendor_display} {name}".strip()

    @property
    def tv_name(self) -> str:
        return self.display_title

    @property
    def api_level(self) -> str:
        return self.sdk_version

    @property
    def full_summary(self) -> str:
        return (
            f"Устройство: {self.display_title}\n"
            f"Модель: {self.model} ({self.manufacturer})\n"
            f"Версия ОС: Android {self.android_version} (API {self.sdk_version})\n"
            f"Экран: {self.resolution} ({self.density} dpi)\n"
            f"Сборка: {self.build_id}"
        )

class DeviceDetector:
    @staticmethod
    def detect(adb: ADBClient) -> Optional[DeviceInfo]:
        def getprop(prop_name: str) -> str:
            _, val = adb.shell(f"getprop {prop_name}")
            return val.strip()

        manufacturer = getprop("ro.product.manufacturer")
        brand = getprop("ro.product.brand")
        model = getprop("ro.product.model")
        market_name = getprop("ro.product.marketname") or getprop("ro.product.name")
        android_ver = getprop("ro.build.version.release")
        sdk_ver = getprop("ro.build.version.sdk")
        build_id = getprop("ro.build.display.id") or getprop("ro.build.id")

        if not model and not manufacturer:
            return None

        # Screen size and density
        _, wm_size = adb.shell("wm size")
        _, wm_density = adb.shell("wm density")
        res_str = wm_size.replace("Physical size:", "").strip() if "Physical size:" in wm_size else wm_size.strip()
        density_str = wm_density.replace("Physical density:", "").strip() if "Physical density:" in wm_density else wm_density.strip()

        # Identify Vendor
        lower_all = f"{manufacturer} {brand} {model}".lower()
        is_xiaomi = any(k in lower_all for k in ["xiaomi", "mitv", "redmi", "mi "])
        is_tcl = "tcl" in lower_all
        is_sony = any(k in lower_all for k in ["sony", "bravia"])

        if is_xiaomi:
            vendor_display = "Xiaomi"
        elif is_tcl:
            vendor_display = "TCL"
        elif is_sony:
            vendor_display = "Sony"
        elif manufacturer:
            vendor_display = manufacturer.capitalize()
        else:
            vendor_display = "Android TV"

        return DeviceInfo(
            manufacturer=manufacturer,
            brand=brand,
            model=model,
            market_name=market_name,
            android_version=android_ver,
            sdk_version=sdk_ver,
            build_id=build_id,
            resolution=res_str or "1920x1080",
            density=density_str or "320",
            is_xiaomi=is_xiaomi,
            is_tcl=is_tcl,
            is_sony=is_sony,
            vendor_display=vendor_display
        )

    @classmethod
    def get_device_info(cls, adb: ADBClient) -> DeviceInfo:
        info = cls.detect(adb)
        if not info:
            return DeviceInfo(
                manufacturer="Android",
                brand="Generic",
                model="TV",
                market_name="Android TV",
                android_version="9+",
                sdk_version="28",
                build_id="unknown",
                resolution="1920x1080",
                density="320",
                is_xiaomi=False,
                is_tcl=False,
                is_sony=False,
                vendor_display="Android TV"
            )
        return info

import re
from dataclasses import dataclass
from typing import List, Tuple, Optional
from .adb_client import ADBClient
from .database import get_package_info

@dataclass
class ProcessRAM:
    process_name: str
    title_ru: str
    ram_mb: float
    title_en: Optional[str] = None

    @property
    def title(self) -> str:
        from .i18n import get_lang
        if get_lang() == "en" and self.title_en:
            return self.title_en
        return self.title_ru

@dataclass
class RAMSnapshot:
    total_mb: float
    used_mb: float
    free_mb: float
    used_percent: float
    top_consumers: List[ProcessRAM]

    @property
    def summary_ru(self) -> str:
        return (
            f"Всего памяти: {self.total_mb:.0f} МБ | "
            f"Занято: {self.used_mb:.0f} МБ ({self.used_percent:.1f}%) | "
            f"Свободно: {self.free_mb:.0f} МБ"
        )

class RAMMonitor:
    @staticmethod
    def get_snapshot(adb: ADBClient) -> Optional[RAMSnapshot]:
        # 1. Fetch physical memory stats from /proc/meminfo (standard Linux kernel metric)
        total_mb, free_mb, used_mb, used_percent = RAMMonitor._read_proc_meminfo(adb)

        # 2. Parse top processes specifically from the "Total PSS by process:" section in dumpsys
        code, out = adb.shell("dumpsys meminfo")
        top_consumers: List[ProcessRAM] = []

        if code == 0 and out:
            proc_section = out.split("Total PSS by process:")[1].split("Total PSS by")[0] if "Total PSS by process:" in out else out
            process_lines = re.findall(r"^\s*([0-9,]+)K:\s+([a-zA-Z0-9_\.:]+)\s+\(pid\s+\d+", proc_section, re.MULTILINE)

            ignore_system_names = {"dex2oat", "system", "zygote", "logd", "surfaceflinger", "audioserver", "media.codec"}

            for kb_str, proc_name in process_lines:
                kb = float(kb_str.replace(",", ""))
                mb = kb / 1024.0
                if mb < 5.0 or proc_name in ignore_system_names:
                    continue

                meta = get_package_info(proc_name)
                title_ru = meta.title_ru if meta.title_ru != proc_name else proc_name
                title_en = meta.title_en if getattr(meta, "title_en", None) and meta.title_en != proc_name else title_ru
                top_consumers.append(ProcessRAM(process_name=proc_name, title_ru=title_ru, ram_mb=mb, title_en=title_en))

            # Sort top consumers descending
            top_consumers.sort(key=lambda x: x.ram_mb, reverse=True)
            top_consumers = top_consumers[:8]

        return RAMSnapshot(
            total_mb=total_mb,
            used_mb=used_mb,
            free_mb=free_mb,
            used_percent=used_percent,
            top_consumers=top_consumers
        )

    @staticmethod
    def _read_proc_meminfo(adb: ADBClient) -> Tuple[float, float, float, float]:
        code, out = adb.shell("cat /proc/meminfo")
        if code == 0 and out:
            mem = {}
            for line in out.splitlines():
                parts = line.split(":")
                if len(parts) == 2:
                    k = parts[0].strip()
                    v = parts[1].replace("kB", "").strip()
                    try:
                        mem[k] = float(v)
                    except ValueError:
                        pass

            tot_kb = mem.get("MemTotal", 0.0)
            free_kb = mem.get("MemFree", 0.0)
            cached_kb = mem.get("Cached", 0.0)
            buffers_kb = mem.get("Buffers", 0.0)

            if tot_kb > 0:
                tot_mb = tot_kb / 1024.0
                avail_mb = (free_kb + cached_kb + buffers_kb) / 1024.0
                avail_mb = min(tot_mb, max(0.0, avail_mb))
                used_mb = max(0.0, tot_mb - avail_mb)
                pct = (used_mb / tot_mb * 100.0)
                return tot_mb, avail_mb, used_mb, pct

        # Fallback default estimate
        return 908.0, 300.0, 608.0, 67.0

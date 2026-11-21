import socket
import concurrent.futures
import urllib.request
import re
import html
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable

@dataclass
class DiscoveredTV:
    ip: str
    port: int = 5555
    name: str = "Smart TV"
    model: str = ""
    is_adb_ready: bool = False
    details: str = ""

    @property
    def friendly_name(self) -> str:
        if self.model and self.model not in self.name:
            return f"{self.name} ({self.model})"
        return self.name

    @property
    def source(self) -> str:
        return "ADB Ready" if self.is_adb_ready else "Network TV"

    @property
    def display_label(self) -> str:
        status_tag = "✔ ADB активен (Готов)" if self.is_adb_ready else "⚠ Отладка выключена"
        info = f"{self.name}"
        if self.model and self.model not in self.name:
            info += f" ({self.model})"
        return f"{self.ip:<15} │ {info:<35} │ {status_tag}"

class NetworkScanner:
    TV_PROBE_PORTS = [5555, 8009, 6467, 7678, 8001]

    @staticmethod
    def get_local_ip() -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
        finally:
            s.close()

    @classmethod
    def scan_network(cls, progress_callback: Optional[Callable[[str], None]] = None) -> List[DiscoveredTV]:
        local_ip = cls.get_local_ip()
        if local_ip == "127.0.0.1":
            return []

        parts = local_ip.split(".")
        if len(parts) != 4:
            return []
        subnet_prefix = ".".join(parts[:3])

        if progress_callback:
            progress_callback(f"Поиск телевизоров в сети {subnet_prefix}.0/24...")

        # 1. SSDP / UPnP Discovery
        ssdp_devices = cls._scan_ssdp(timeout=1.8)

        # 2. Fast multi-port subnet sweep
        if progress_callback:
            progress_callback("Сканирование открытых портов ТВ и ADB...")

        alive_hosts: Dict[str, List[int]] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=80) as executor:
            futures = {
                executor.submit(cls._probe_host, f"{subnet_prefix}.{i}"): f"{subnet_prefix}.{i}"
                for i in range(1, 255)
            }
            for future in concurrent.futures.as_completed(futures):
                res = future.result()
                if res:
                    ip, open_ports = res
                    alive_hosts[ip] = open_ports

        # 3. Combine and categorize
        discovered: List[DiscoveredTV] = []
        all_ips = set(ssdp_devices.keys()).union(set(alive_hosts.keys()))

        for ip in all_ips:
            ports = alive_hosts.get(ip, [])
            ssdp_info = ssdp_devices.get(ip)

            has_adb = (5555 in ports)
            has_cast = (8009 in ports) or (6467 in ports)

            name = "Телевизор"
            model = ""
            details = ""

            if ssdp_info:
                name, model = ssdp_info

            if has_adb:
                if not ssdp_info:
                    name = "Android TV / Приставка"
                details = "Порт ADB 5555 открыт"
            elif has_cast:
                if not ssdp_info:
                    name = "Android TV / Google Cast"
                details = "Google Cast активен, но порт 5555 закрыт"
            elif not ssdp_info:
                # Device only had other ports open
                continue

            discovered.append(DiscoveredTV(
                ip=ip,
                port=5555,
                name=name,
                model=model,
                is_adb_ready=has_adb,
                details=details
            ))

        # Sort: ADB-ready devices first, then by IP
        discovered.sort(key=lambda d: (not d.is_adb_ready, cls._ip_to_int(d.ip)))
        return discovered

    @staticmethod
    def _ip_to_int(ip: str) -> int:
        try:
            parts = [int(p) for p in ip.split(".")]
            return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
        except Exception:
            return 0

    @classmethod
    def _probe_host(cls, ip: str) -> Optional[tuple]:
        open_ports = []
        for port in cls.TV_PROBE_PORTS:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            try:
                if s.connect_ex((ip, port)) == 0:
                    open_ports.append(port)
            except Exception:
                pass
            finally:
                s.close()
        if open_ports:
            return (ip, open_ports)
        return None

    @classmethod
    def _scan_ssdp(cls, timeout: float = 1.8) -> Dict[str, tuple]:
        """Returns dict: {ip: (friendlyName, modelName)}"""
        devices = {}
        msg = (
            "M-SEARCH * HTTP/1.1\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            "MAN: \"ssdp:discover\"\r\n"
            "MX: 2\r\n"
            "ST: ssdp:all\r\n\r\n"
        )
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.settimeout(timeout)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        try:
            s.sendto(msg.encode(), ("239.255.255.250", 1900))
            while True:
                try:
                    data, addr = s.recvfrom(65507)
                    ip = addr[0]
                    text = data.decode("utf-8", errors="ignore")
                    loc = re.search(r"LOCATION:\s*(.+)", text, re.IGNORECASE)
                    if loc and ip not in devices:
                        devices[ip] = loc.group(1).strip()
                except socket.timeout:
                    break
        finally:
            s.close()

        res = {}
        for ip, loc_url in devices.items():
            try:
                with urllib.request.urlopen(loc_url, timeout=1.2) as resp:
                    xml = resp.read().decode("utf-8", errors="ignore")
                    fn = re.search(r"<friendlyName>(.*?)</friendlyName>", xml)
                    md = re.search(r"<modelName>(.*?)</modelName>", xml)
                    name = html.unescape(fn.group(1).strip()) if fn else "Устройство сети"
                    model = html.unescape(md.group(1).strip()) if md else ""

                    # Filter out routers/gateways
                    low_name = name.lower()
                    if any(w in low_name for w in ["router", "gateway", "keenetic", "mikrotik", "asus", "tplink"]):
                        continue
                    res[ip] = (name, model)
            except Exception:
                pass
        return res

    scan_local_network = scan_network

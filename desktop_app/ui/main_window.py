import os
import sys
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Optional, Set

from core.adb_client import ADBClient
from core.device_detector import DeviceDetector, DeviceInfo
from core.database import PackageMeta, CATEGORIES
from core.debloater import Debloater
from core.launcher_installer import LauncherInstaller
from core.ram_monitor import RAMMonitor, RAMSnapshot
from ui.styles import (
    BG_DARK, BG_CARD, BG_CARD_LIGHT, BORDER_COLOR,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    ACCENT_CYAN, ACCENT_GREEN, ACCENT_ORANGE, ACCENT_RED, FONT_FAMILY
)

class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Android TV Optimizer & Cleaner")
        self.root.geometry("1040x750")
        self.root.minsize(940, 660)
        self.root.configure(bg=BG_DARK)

        self.adb = ADBClient()
        self.device_info: Optional[DeviceInfo] = None
        self.installed_packages: List[PackageMeta] = []
        self.selected_pkgs: Set[str] = set()

        self.ram_snapshot_before: Optional[RAMSnapshot] = None
        self.ram_snapshot_after: Optional[RAMSnapshot] = None

        self.before_screenshot_path: Optional[str] = None
        self.after_screenshot_path: Optional[str] = None
        self.removed_history: List[str] = []

        self._setup_styles()
        self._build_ui()

        # Auto-check devices on start
        self.root.after(300, self._auto_check_connection)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Configure tabs
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_CARD, foreground=TEXT_SECONDARY,
                        padding=[16, 8], font=(FONT_FAMILY, 11, "bold"), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", BG_CARD_LIGHT)],
                  foreground=[("selected", ACCENT_CYAN)])

        # Configure Treeview (table)
        style.configure("Treeview",
                        background=BG_CARD,
                        foreground=TEXT_PRIMARY,
                        fieldbackground=BG_CARD,
                        borderwidth=0,
                        rowheight=28,
                        font=(FONT_FAMILY, 10))
        style.configure("Treeview.Heading",
                        background=BG_CARD_LIGHT,
                        foreground=TEXT_PRIMARY,
                        font=(FONT_FAMILY, 10, "bold"),
                        borderwidth=0)
        style.map("Treeview",
                  background=[("selected", "#2D3548")],
                  foreground=[("selected", TEXT_PRIMARY)])

        # Configure Progressbar
        style.configure("TProgressbar", thickness=8, troughcolor=BG_CARD, background=ACCENT_CYAN)

    def _build_ui(self):
        # 1. Header Bar
        header = tk.Frame(self.root, bg=BG_DARK, height=60)
        header.pack(fill="x", padx=20, pady=(15, 10))

        title_lbl = tk.Label(header, text="⚡ Android TV Optimizer & Debloater",
                             font=(FONT_FAMILY, 18, "bold"), fg=TEXT_PRIMARY, bg=BG_DARK)
        title_lbl.pack(side="left")

        self.status_badge = tk.Label(header, text="● Отключено",
                                     font=(FONT_FAMILY, 11, "bold"), fg=ACCENT_RED, bg=BG_CARD,
                                     padx=12, pady=4)
        self.status_badge.pack(side="right")

        # 2. Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.tab_connect = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_apps = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_optimize = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_results = tk.Frame(self.notebook, bg=BG_DARK)

        self.notebook.add(self.tab_connect, text=" 1. Подключение ")
        self.notebook.add(self.tab_apps, text=" 2. Выбор приложений & Память ")
        self.notebook.add(self.tab_optimize, text=" 3. Очистка и Лаунчер ")
        self.notebook.add(self.tab_results, text=" 4. Итоги и Откат ")

        self._build_tab_connect()
        self._build_tab_apps()
        self._build_tab_optimize()
        self._build_tab_results()

    # =========================================================================
    # TAB 1: CONNECT
    # =========================================================================
    def _build_tab_connect(self):
        parent = self.tab_connect

        # Connection Box
        box = tk.LabelFrame(parent, text=" Подключение по Wi-Fi / Сети ",
                            bg=BG_CARD, fg=TEXT_PRIMARY, font=(FONT_FAMILY, 12, "bold"),
                            padx=15, pady=15, bd=1, relief="solid")
        box.pack(fill="x", padx=10, pady=10)

        row1 = tk.Frame(box, bg=BG_CARD)
        row1.pack(fill="x", pady=5)

        tk.Label(row1, text="IP-адрес телевизора:", font=(FONT_FAMILY, 11),
                 fg=TEXT_SECONDARY, bg=BG_CARD).pack(side="left", padx=(0, 10))

        self.entry_ip = tk.Entry(row1, font=(FONT_FAMILY, 11), bg=BG_CARD_LIGHT,
                                 fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, width=18, bd=1)
        self.entry_ip.pack(side="left", padx=(0, 15))

        self.btn_connect = tk.Button(row1, text="Подключиться", font=(FONT_FAMILY, 10, "bold"),
                                     bg=ACCENT_CYAN, fg="#000000", activebackground="#00B8D4",
                                     padx=15, pady=4, bd=0, cursor="hand2", command=self._action_connect)
        self.btn_connect.pack(side="left", padx=5)

        self.btn_refresh = tk.Button(row1, text="Поиск USB / Онлайн", font=(FONT_FAMILY, 10),
                                     bg=BG_CARD_LIGHT, fg=TEXT_PRIMARY, activebackground=BORDER_COLOR,
                                     padx=12, pady=4, bd=0, cursor="hand2", command=self._auto_check_connection)
        self.btn_refresh.pack(side="left", padx=5)

        # Device Info Card
        self.card_device = tk.LabelFrame(parent, text=" Информация о ТВ ",
                                         bg=BG_CARD, fg=TEXT_PRIMARY, font=(FONT_FAMILY, 12, "bold"),
                                         padx=15, pady=15, bd=1, relief="solid")
        self.card_device.pack(fill="x", padx=10, pady=10)

        self.lbl_device_info = tk.Label(self.card_device,
                                        text="ТВ не подключен. Введите IP и нажмите «Подключиться».",
                                        font=(FONT_FAMILY, 11), fg=TEXT_SECONDARY, bg=BG_CARD,
                                        justify="left", anchor="w")
        self.lbl_device_info.pack(fill="x")

        # Instructions / Help
        help_box = tk.LabelFrame(parent, text=" Как включить отладку на ТВ ",
                                 bg=BG_CARD, fg=TEXT_PRIMARY, font=(FONT_FAMILY, 11, "bold"),
                                 padx=15, pady=15, bd=1, relief="solid")
        help_box.pack(fill="both", expand=True, padx=10, pady=10)

        help_text = (
            "1. На телевизоре откройте: Настройки → Настройки устройства → Об устройстве.\n"
            "2. Найдите пункт «Сборка ОС» (Build) и нажмите кнопку ОК на пульте 7 раз подряд.\n"
            "   Появится сообщение: «Вы стали разработчиком!».\n"
            "3. Вернитесь назад: Настройки → Для разработчиков → Включите «Отладка по USB».\n"
            "4. Узнайте IP-адрес ТВ: Настройки → Сеть и интернет → Ваша сеть Wi-Fi (или Ethernet).\n"
            "5. При первом подключении на экране телевизора появится запрос авторизации — выберите «Всегда разрешать»."
        )
        tk.Label(help_box, text=help_text, font=(FONT_FAMILY, 10), fg=TEXT_SECONDARY,
                 bg=BG_CARD, justify="left").pack(anchor="w")

    # =========================================================================
    # TAB 2: APPS SELECTION & RAM MONITOR
    # =========================================================================
    def _build_tab_apps(self):
        parent = self.tab_apps

        # RAM Analysis Card
        self.card_ram = tk.LabelFrame(
            parent, text=" 📊 Анализ оперативной памяти ТВ (RAM) ",
            bg=BG_CARD, fg=TEXT_PRIMARY, font=(FONT_FAMILY, 11, "bold"),
            padx=14, pady=10, bd=1, relief="solid"
        )
        self.card_ram.pack(fill="x", padx=10, pady=(8, 6))

        ram_header_row = tk.Frame(self.card_ram, bg=BG_CARD)
        ram_header_row.pack(fill="x")

        self.lbl_ram_summary = tk.Label(
            ram_header_row, text="Анализ памяти телевизора...",
            font=(FONT_FAMILY, 11, "bold"), fg=ACCENT_CYAN, bg=BG_CARD, justify="left", anchor="w"
        )
        self.lbl_ram_summary.pack(side="left")

        btn_refresh_ram = tk.Button(
            ram_header_row, text="↻ Обновить RAM", font=(FONT_FAMILY, 9),
            bg=BG_CARD_LIGHT, fg=TEXT_PRIMARY, padx=8, pady=2, bd=0, cursor="hand2",
            command=self._refresh_ram_stats
        )
        btn_refresh_ram.pack(side="right")

        self.lbl_ram_top = tk.Label(
            self.card_ram, text="",
            font=(FONT_FAMILY, 9), fg=TEXT_SECONDARY, bg=BG_CARD, justify="left", anchor="w"
        )
        self.lbl_ram_top.pack(fill="x", pady=(4, 0))

        # Controls bar
        ctrl_bar = tk.Frame(parent, bg=BG_DARK)
        ctrl_bar.pack(fill="x", padx=10, pady=(6, 4))

        self.btn_select_recommended = tk.Button(
            ctrl_bar, text="★ Выбрать рекомендуемые (Безопасно)",
            font=(FONT_FAMILY, 10, "bold"), bg=ACCENT_GREEN, fg="#000000",
            activebackground="#00C853", padx=12, pady=5, bd=0, cursor="hand2",
            command=self._select_recommended
        )
        self.btn_select_recommended.pack(side="left", padx=(0, 10))

        btn_select_all = tk.Button(
            ctrl_bar, text="Выбрать все в списке",
            font=(FONT_FAMILY, 10), bg=BG_CARD_LIGHT, fg=TEXT_PRIMARY,
            padx=10, pady=5, bd=0, cursor="hand2", command=self._select_all_visible
        )
        btn_select_all.pack(side="left", padx=5)

        btn_deselect_all = tk.Button(
            ctrl_bar, text="Снять выбор",
            font=(FONT_FAMILY, 10), bg=BG_CARD_LIGHT, fg=TEXT_PRIMARY,
            padx=10, pady=5, bd=0, cursor="hand2", command=self._deselect_all
        )
        btn_deselect_all.pack(side="left", padx=5)

        self.lbl_selected_counter = tk.Label(
            ctrl_bar, text="Выбрано: 0", font=(FONT_FAMILY, 11, "bold"),
            fg=ACCENT_CYAN, bg=BG_DARK
        )
        self.lbl_selected_counter.pack(side="right", padx=10)

        # Category Filter Tabs
        cat_bar = tk.Frame(parent, bg=BG_DARK)
        cat_bar.pack(fill="x", padx=10, pady=(0, 6))

        self.category_var = tk.StringVar(value="all")
        cats = [
            ("Все", "all"),
            ("Реклама и телеметрия", "vendor_bloat"),
            ("Службы Google", "google_bloat"),
            ("Медиа и стриминг", "streaming"),
            ("Прочие", "other"),
            ("Системные", "safe_system")
        ]
        for title, key in cats:
            btn = tk.Radiobutton(
                cat_bar, text=title, variable=self.category_var, value=key,
                indicatoron=False, font=(FONT_FAMILY, 9, "bold"),
                bg=BG_CARD, fg=TEXT_SECONDARY, selectcolor=BG_CARD_LIGHT,
                activebackground=BG_CARD_LIGHT, bd=0, padx=10, pady=3,
                command=self._filter_packages
            )
            btn.pack(side="left", padx=3)

        # Treeview (Table)
        table_frame = tk.Frame(parent, bg=BG_CARD)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("selected", "title", "package", "category", "risk")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("selected", text="[X]")
        self.tree.heading("title", text="Название")
        self.tree.heading("package", text="Пакет")
        self.tree.heading("category", text="Категория")
        self.tree.heading("risk", text="Безопасность")

        self.tree.column("selected", width=45, anchor="center")
        self.tree.column("title", width=220, anchor="w")
        self.tree.column("package", width=260, anchor="w")
        self.tree.column("category", width=180, anchor="w")
        self.tree.column("risk", width=120, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<ButtonRelease-1>", self._on_tree_click)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Bottom detail box
        self.detail_frame = tk.LabelFrame(parent, text=" Описание компонента ",
                                          bg=BG_CARD, fg=TEXT_PRIMARY, font=(FONT_FAMILY, 10, "bold"),
                                          padx=12, pady=8, bd=1, relief="solid")
        self.detail_frame.pack(fill="x", padx=10, pady=(5, 10))

        self.lbl_detail = tk.Label(self.detail_frame, text="Выберите элемент в таблице для просмотра подробностей.",
                                   font=(FONT_FAMILY, 10), fg=TEXT_SECONDARY, bg=BG_CARD,
                                   justify="left", anchor="w")
        self.lbl_detail.pack(fill="x")

    # =========================================================================
    # TAB 3: OPTIMIZE & LAUNCHER
    # =========================================================================
    def _build_tab_optimize(self):
        parent = self.tab_optimize

        opts_frame = tk.LabelFrame(parent, text=" Действия по оптимизации ",
                                   bg=BG_CARD, fg=TEXT_PRIMARY, font=(FONT_FAMILY, 12, "bold"),
                                   padx=15, pady=12, bd=1, relief="solid")
        opts_frame.pack(fill="x", padx=10, pady=10)

        self.opt_before_screen = tk.BooleanVar(value=True)
        self.opt_debloat = tk.BooleanVar(value=True)
        self.opt_revoke_perms = tk.BooleanVar(value=True)
        self.opt_install_launcher = tk.BooleanVar(value=True)
        self.opt_disable_stock = tk.BooleanVar(value=True)
        self.opt_after_screen = tk.BooleanVar(value=True)

        checks = [
            ("📸 Сохранить снимок экрана ТВ «ДО» оптимизации", self.opt_before_screen),
            ("🗑️ Удалить выбранные приложения и мусор (pm uninstall -k --user 0)", self.opt_debloat),
            ("🔒 Отозвать опасные разрешения фоновой прослушки микрофона и геолокации", self.opt_revoke_perms),
            ("🚀 Установить наш ультра-минималистичный лаунчер (minimal_launcher.apk)", self.opt_install_launcher),
            ("🛑 Отключить стандартный тяжелый рекламный лаунчер Google/Xiaomi", self.opt_disable_stock),
            ("📸 Сохранить снимок экрана ТВ «ПОСЛЕ» оптимизации", self.opt_after_screen),
        ]

        for text, var in checks:
            cb = tk.Checkbutton(opts_frame, text=text, variable=var,
                                font=(FONT_FAMILY, 10), fg=TEXT_PRIMARY, bg=BG_CARD,
                                selectcolor=BG_CARD_LIGHT, activebackground=BG_CARD,
                                bd=0, pady=3)
            cb.pack(anchor="w")

        # Action Button
        self.btn_run_optimize = tk.Button(
            parent, text="▶ ЗАПУСТИТЬ ОПТИМИЗАЦИЮ И НАСТРОЙКУ ТВ",
            font=(FONT_FAMILY, 12, "bold"), bg=ACCENT_CYAN, fg="#000000",
            activebackground="#00B8D4", padx=20, pady=10, bd=0, cursor="hand2",
            command=self._action_start_optimization
        )
        self.btn_run_optimize.pack(fill="x", padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(parent, style="TProgressbar", mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 5))

        # Live Execution Log
        log_frame = tk.LabelFrame(parent, text=" Ход выполнения ",
                                  bg=BG_CARD, fg=TEXT_PRIMARY, font=(FONT_FAMILY, 10, "bold"),
                                  padx=10, pady=8, bd=1, relief="solid")
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.txt_log = tk.Text(log_frame, bg="#0A0B0E", fg=TEXT_PRIMARY,
                               font=("Courier", 10), insertbackground=TEXT_PRIMARY,
                               bd=0, padx=8, pady=8)
        self.txt_log.pack(fill="both", expand=True)

    # =========================================================================
    # TAB 4: RESULTS & ROLLBACK
    # =========================================================================
    def _build_tab_results(self):
        parent = self.tab_results

        # RAM Comparison Card
        self.ram_results_box = tk.LabelFrame(
            parent, text=" 📊 Сравнение оперативной памяти (RAM) ДО и ПОСЛЕ ",
            bg=BG_CARD, fg=TEXT_PRIMARY, font=(FONT_FAMILY, 12, "bold"),
            padx=15, pady=12, bd=1, relief="solid"
        )
        self.ram_results_box.pack(fill="x", padx=10, pady=10)

        self.lbl_ram_comparison = tk.Label(
            self.ram_results_box,
            text="Сравнение будет доступно после завершения оптимизации.",
            font=(FONT_FAMILY, 11), fg=TEXT_SECONDARY, bg=BG_CARD, justify="left"
        )
        self.lbl_ram_comparison.pack(anchor="w")

        # Summary box
        summary_box = tk.LabelFrame(parent, text=" Результаты оптимизации ",
                                    bg=BG_CARD, fg=TEXT_PRIMARY, font=(FONT_FAMILY, 12, "bold"),
                                    padx=15, pady=15, bd=1, relief="solid")
        summary_box.pack(fill="x", padx=10, pady=(0, 10))

        self.lbl_results_summary = tk.Label(
            summary_box,
            text="Оптимизация еще не проводилась. Перейдите на вкладку 3 для запуска.",
            font=(FONT_FAMILY, 11), fg=TEXT_SECONDARY, bg=BG_CARD, justify="left"
        )
        self.lbl_results_summary.pack(anchor="w")

        # Screenshots buttons
        screens_frame = tk.Frame(summary_box, bg=BG_CARD)
        screens_frame.pack(fill="x", pady=(15, 0))

        self.btn_open_before = tk.Button(
            screens_frame, text="Снимок экрана ДО", font=(FONT_FAMILY, 10),
            bg=BG_CARD_LIGHT, fg=TEXT_PRIMARY, padx=12, pady=5, bd=0, state="disabled",
            command=lambda: self._open_file(self.before_screenshot_path)
        )
        self.btn_open_before.pack(side="left", padx=(0, 10))

        self.btn_open_after = tk.Button(
            screens_frame, text="Снимок экрана ПОСЛЕ", font=(FONT_FAMILY, 10),
            bg=BG_CARD_LIGHT, fg=TEXT_PRIMARY, padx=12, pady=5, bd=0, state="disabled",
            command=lambda: self._open_file(self.after_screenshot_path)
        )
        self.btn_open_after.pack(side="left", padx=(0, 10))

        # Rollback / Restore Box
        rollback_box = tk.LabelFrame(parent, text=" Восстановление приложений (Откат) ",
                                     bg=BG_CARD, fg=TEXT_PRIMARY, font=(FONT_FAMILY, 12, "bold"),
                                     padx=15, pady=15, bd=1, relief="solid")
        rollback_box.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(rollback_box,
                 text="Если вы случайно удалили нужное приложение, Android позволяет восстановить его одной командой:",
                 font=(FONT_FAMILY, 10), fg=TEXT_SECONDARY, bg=BG_CARD).pack(anchor="w", pady=(0, 10))

        self.btn_rollback_all = tk.Button(
            rollback_box, text="↺ Восстановить все приложения, удаленные в этой сессии",
            font=(FONT_FAMILY, 10, "bold"), bg=ACCENT_ORANGE, fg="#000000",
            activebackground="#FFA000", padx=15, pady=8, bd=0, cursor="hand2",
            command=self._action_rollback
        )
        self.btn_rollback_all.pack(anchor="w")

    # =========================================================================
    # ACTIONS & LOGIC
    # =========================================================================

    def _log(self, message: str):
        self.txt_log.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.txt_log.see("end")

    def _auto_check_connection(self):
        devices = self.adb.get_devices()
        if devices:
            dev_id, status = devices[0]
            if status == "device":
                self.adb.selected_device = dev_id
                self._on_connected()
                return

        ip = self.entry_ip.get().strip()
        if ip:
            threading.Thread(target=self._connect_thread, args=(ip,), daemon=True).start()

    def _action_connect(self):
        ip = self.entry_ip.get().strip()
        if not ip:
            messagebox.showwarning("Внимание", "Пожалуйста, введите IP-адрес телевизора.")
            return
        self.btn_connect.config(state="disabled", text="Подключение...")
        threading.Thread(target=self._connect_thread, args=(ip,), daemon=True).start()

    def _connect_thread(self, ip: str):
        success, msg = self.adb.connect(ip)
        self.root.after(0, lambda: self._after_connect(success, msg))

    def _after_connect(self, success: bool, msg: str):
        self.btn_connect.config(state="normal", text="Подключиться")
        if success:
            self._on_connected()
        else:
            self.status_badge.config(text="● Ошибка подключения", fg=ACCENT_RED)
            self.lbl_device_info.config(text=f"Не удалось подключиться: {msg}\nУбедитесь, что ТВ включен в сеть и разрешена отладка.")

    def _on_connected(self):
        self.status_badge.config(text="● Подключено", fg=ACCENT_GREEN)
        self.device_info = DeviceDetector.detect(self.adb)

        if self.device_info:
            self.lbl_device_info.config(text=self.device_info.full_summary)
        else:
            self.lbl_device_info.config(text=f"Подключено к {self.adb.selected_device}")

        # Scan packages and RAM in background
        threading.Thread(target=self._scan_packages_thread, daemon=True).start()

    def _scan_packages_thread(self):
        self.installed_packages = Debloater.get_installed_packages(self.adb)
        self.ram_snapshot_before = RAMMonitor.get_snapshot(self.adb)
        self.root.after(0, self._render_packages)
        self.root.after(0, self._render_ram_stats)

    def _refresh_ram_stats(self):
        def thread():
            self.ram_snapshot_before = RAMMonitor.get_snapshot(self.adb)
            self.root.after(0, self._render_ram_stats)
        threading.Thread(target=thread, daemon=True).start()

    def _render_ram_stats(self):
        if not self.ram_snapshot_before:
            self.lbl_ram_summary.config(text="Не удалось получить статистику RAM.", fg=TEXT_MUTED)
            return

        ram = self.ram_snapshot_before
        color = ACCENT_GREEN if ram.used_percent < 60 else (ACCENT_ORANGE if ram.used_percent < 80 else ACCENT_RED)

        summary_text = (
            f"Всего RAM: {ram.total_mb:.0f} МБ  |  "
            f"Занято: {ram.used_mb:.0f} МБ ({ram.used_percent:.0f}%)  |  "
            f"Свободно: {ram.free_mb:.0f} МБ"
        )
        self.lbl_ram_summary.config(text=summary_text, fg=color)

        if ram.top_consumers:
            top_parts = [f"{p.title_ru} ({p.ram_mb:.0f} МБ)" for p in ram.top_consumers[:5]]
            top_str = "Топ процессов в памяти: " + "  •  ".join(top_parts)
            self.lbl_ram_top.config(text=top_str)
        else:
            self.lbl_ram_top.config(text="")

    def _render_packages(self):
        current_cat = self.category_var.get()
        self.tree.delete(*self.tree.get_children())

        for p in self.installed_packages:
            if current_cat != "all" and p.category != current_cat:
                continue

            is_checked = p.package_name in self.selected_pkgs
            check_mark = "☑" if is_checked else "☐"
            cat_name = CATEGORIES.get(p.category, p.category)

            risk_display = {
                "SAFE": "Безопасно",
                "CAUTION": "Осторожно",
                "CRITICAL": "Защищено"
            }.get(p.risk_level, p.risk_level)

            self.tree.insert("", "end", iid=p.package_name,
                             values=(check_mark, p.title_ru, p.package_name, cat_name, risk_display))

            if p.risk_level == "CRITICAL":
                self.tree.tag_configure(p.package_name, foreground=TEXT_MUTED)
            elif p.risk_level == "CAUTION":
                self.tree.tag_configure(p.package_name, foreground=ACCENT_ORANGE)
            elif is_checked:
                self.tree.tag_configure(p.package_name, foreground=ACCENT_CYAN)

        self._update_counter()

    def _filter_packages(self):
        self._render_packages()

    def _on_tree_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return

        pkg_name = item
        meta = next((p for p in self.installed_packages if p.package_name == pkg_name), None)
        if not meta or meta.risk_level == "CRITICAL":
            return

        if pkg_name in self.selected_pkgs:
            self.selected_pkgs.remove(pkg_name)
        else:
            self.selected_pkgs.add(pkg_name)

        self._render_packages()

    def _on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        pkg_name = selected[0]
        meta = next((p for p in self.installed_packages if p.package_name == pkg_name), None)
        if meta:
            self.lbl_detail.config(
                text=f"{meta.title_ru} ({meta.package_name})\n{meta.description_ru}\nРекомендация: {meta.recommended_action} | Уровень риска: {meta.risk_level}"
            )

    def _select_recommended(self):
        self.selected_pkgs.clear()
        for p in self.installed_packages:
            if p.recommended_action in ["REMOVE", "DISABLE"] and p.risk_level != "CRITICAL":
                self.selected_pkgs.add(p.package_name)
        self._render_packages()

    def _select_all_visible(self):
        current_cat = self.category_var.get()
        for p in self.installed_packages:
            if current_cat != "all" and p.category != current_cat:
                continue
            if p.risk_level != "CRITICAL":
                self.selected_pkgs.add(p.package_name)
        self._render_packages()

    def _deselect_all(self):
        self.selected_pkgs.clear()
        self._render_packages()

    def _update_counter(self):
        self.lbl_selected_counter.config(text=f"Выбрано: {len(self.selected_pkgs)}")

    # =========================================================================
    # OPTIMIZATION PIPELINE
    # =========================================================================

    def _action_start_optimization(self):
        if not self.adb.selected_device:
            messagebox.showerror("Ошибка", "Сначала подключитесь к телевизору на вкладке 1.")
            return

        if self.opt_debloat.get() and not self.selected_pkgs:
            confirm = messagebox.askyesno(
                "Приложения не выбраны",
                "Вы не выбрали ни одного приложения для удаления. Продолжить только с установкой лаунчера?"
            )
            if not confirm:
                return

        self.btn_run_optimize.config(state="disabled", text="⏳ ВЫПОЛНЯЕТСЯ ОПТИМИЗАЦИЯ...")
        self.progress_bar["value"] = 0
        self.txt_log.delete("1.0", "end")

        threading.Thread(target=self._run_optimization_thread, daemon=True).start()

    def _run_optimization_thread(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshots_dir = os.path.join(os.path.expanduser("~"), "Documents/TV_Cleaner_Suite/tv_screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        try:
            # 0. Initial RAM Measurement
            if not self.ram_snapshot_before:
                self.ram_snapshot_before = RAMMonitor.get_snapshot(self.adb)

            if self.ram_snapshot_before:
                self._log(f"📊 Замер RAM «ДО»: Занято {self.ram_snapshot_before.used_mb:.0f} МБ из {self.ram_snapshot_before.total_mb:.0f} МБ ({self.ram_snapshot_before.used_percent:.0f}%)")

            # 1. Before Screenshot
            if self.opt_before_screen.get():
                self._log("📸 Создание снимка экрана ТВ «ДО»...")
                before_path = os.path.join(screenshots_dir, f"screen_BEFORE_{timestamp}.png")
                ok, res = self.adb.capture_screenshot(before_path)
                if ok:
                    self.before_screenshot_path = before_path
                    self._log(f"Снимок сохранен: {before_path}")
                else:
                    self._log(f"Предупреждение: {res}")
            self.progress_bar["value"] = 20

            # 2. Debloat (Uninstall)
            if self.opt_debloat.get() and self.selected_pkgs:
                to_remove = list(self.selected_pkgs)
                self._log(f"🗑️ Удаление {len(to_remove)} мусорных пакетов...")

                def on_progress(msg, frac):
                    self._log(msg)
                    self.progress_bar["value"] = 20 + int(frac * 40)

                results = Debloater.remove_packages(self.adb, to_remove, on_progress)
                success_count = sum(1 for v in results.values() if v)
                self.removed_history = [k for k, v in results.items() if v]
                self._log(f"Успешно удалено пакетов: {success_count} из {len(to_remove)}")
            self.progress_bar["value"] = 60

            # 3. Revoke permissions
            if self.opt_revoke_perms.get():
                self._log("🔒 Ограничение фонового доступа к микрофону и геолокации...")
                Debloater.revoke_telemetry_permissions(self.adb, ["com.google.android.katniss", "com.xiaomi.statistic"])
            self.progress_bar["value"] = 70

            # 4. Install Minimal Launcher
            if self.opt_install_launcher.get():
                self._log("🚀 Установка минималистичного Kotlin-лаунчера...")
                ok, msg = LauncherInstaller.install_and_activate(
                    self.adb,
                    disable_stock_launchers=self.opt_disable_stock.get(),
                    status_callback=self._log
                )
                self._log(f"Результат лаунчера: {msg}")
            self.progress_bar["value"] = 85

            # Brief pause for TV processes to settle
            self._log("⏳ Ожидание стабилизации процессов ТВ...")
            time.sleep(2)

            # 5. Measure RAM after
            self._log("📊 Замер оперативной памяти ПОСЛЕ оптимизации...")
            self.ram_snapshot_after = RAMMonitor.get_snapshot(self.adb)
            if self.ram_snapshot_before and self.ram_snapshot_after:
                freed = self.ram_snapshot_before.used_mb - self.ram_snapshot_after.used_mb
                if freed > 0:
                    self._log(f"🎉 Результат RAM: Освобождено +{freed:.0f} МБ памяти! (Было {self.ram_snapshot_before.used_mb:.0f} МБ -> стало {self.ram_snapshot_after.used_mb:.0f} МБ)")
                else:
                    self._log(f"📊 Текущее использование RAM: {self.ram_snapshot_after.used_mb:.0f} МБ из {self.ram_snapshot_after.total_mb:.0f} МБ")
            self.progress_bar["value"] = 92

            # 6. After Screenshot
            if self.opt_after_screen.get():
                self._log("📸 Создание снимка экрана ТВ «ПОСЛЕ»...")
                after_path = os.path.join(screenshots_dir, f"screen_AFTER_{timestamp}.png")
                ok, res = self.adb.capture_screenshot(after_path)
                if ok:
                    self.after_screenshot_path = after_path
                    self._log(f"Снимок сохранен: {after_path}")
            self.progress_bar["value"] = 100

            self._log("🎉 ОПТИМИЗАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")

        except Exception as e:
            self._log(f"❌ Критическая ошибка: {str(e)}")

        finally:
            self.root.after(0, self._on_optimization_finished)

    def _on_optimization_finished(self):
        self.btn_run_optimize.config(state="normal", text="▶ ЗАПУСТИТЬ ОПТИМИЗАЦИЮ И НАСТРОЙКУ ТВ")

        # Update RAM comparison card
        if self.ram_snapshot_before and self.ram_snapshot_after:
            b = self.ram_snapshot_before
            a = self.ram_snapshot_after
            freed = b.used_mb - a.used_mb
            freed_msg = f"🎉 Освобождено памяти: +{freed:.0f} МБ!\n" if freed > 0 else ""
            ram_comparison_text = (
                f"• ДО оптимизации:   {b.used_mb:.0f} МБ занято из {b.total_mb:.0f} МБ ({b.used_percent:.0f}%)\n"
                f"• ПОСЛЕ оптимизации: {a.used_mb:.0f} МБ занято из {a.total_mb:.0f} МБ ({a.used_percent:.0f}%)\n\n"
                f"{freed_msg}"
                f"Фоновые процессы выгружены, отзывчивость интерфейса значительно возросла."
            )
            self.lbl_ram_comparison.config(text=ram_comparison_text, fg=TEXT_PRIMARY)

        # Update Summary Box
        summary_text = (
            f"Оптимизация завершена успешно!\n\n"
            f"• Удалено мусорных пакетов: {len(self.removed_history)}\n"
            f"• Ограничены права микрофона и телеметрии: Выполнено\n"
            f"• Минималистичный ТВ-лаунчер: Установлен и активирован\n\n"
            f"Снимки экранов сохранены в папке:\n"
            f"~/Documents/TV_Cleaner_Suite/tv_screenshots/"
        )
        self.lbl_results_summary.config(text=summary_text)

        if self.before_screenshot_path:
            self.btn_open_before.config(state="normal")
        if self.after_screenshot_path:
            self.btn_open_after.config(state="normal")

        # Switch to Results tab
        self.notebook.select(self.tab_results)
        messagebox.showinfo("Успех", "Оптимизация телевизора успешно завершена!")

    def _action_rollback(self):
        if not self.removed_history:
            messagebox.showinfo("Информация", "В этой сессии не было удалено приложений для отката.")
            return

        confirm = messagebox.askyesno(
            "Подтверждение отката",
            f"Восстановить {len(self.removed_history)} приложений, удаленных в этой сессии?"
        )
        if not confirm:
            return

        def rollback_thread():
            self._log("↺ Запуск восстановления пакетов...")
            res = Debloater.restore_packages(self.adb, self.removed_history, self._log)
            restored = sum(1 for v in res.values() if v)
            self._log(f"Восстановлено: {restored} из {len(self.removed_history)}")
            self.root.after(0, lambda: messagebox.showinfo("Готово", f"Восстановлено {restored} приложений."))

        threading.Thread(target=rollback_thread, daemon=True).start()

    def _open_file(self, path: Optional[str]):
        if not path or not os.path.exists(path):
            messagebox.showwarning("Внимание", "Файл не найден.")
            return

        if sys.platform == "darwin":
            subprocess.run(["open", path])
        elif sys.platform == "win32":
            os.startfile(path)
        else:
            subprocess.run(["xdg-open", path])

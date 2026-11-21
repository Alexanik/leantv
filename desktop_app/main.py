#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android TV Optimizer & Debloater
Cross-platform Suite (macOS, Windows, Linux)
"""

import os
import sys

# Ensure local packages are resolvable
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    # Check if user explicitly wants GUI mode
    if "--gui" in sys.argv:
        try:
            import tkinter as tk
            from ui.main_window import MainWindow
            root = tk.Tk()
            app = MainWindow(root)
            root.mainloop()
            return
        except Exception as e:
            print(f"Ошибка запуска GUI: {e}. Запуск в терминальном режиме...\n")

    # Default: Interactive Terminal CLI
    from cli import main as cli_main
    cli_main()

if __name__ == "__main__":
    main()

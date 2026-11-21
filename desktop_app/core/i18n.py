#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LeanTV Internationalization (i18n) module.
Supports Russian (ru) and English (en).
"""

import os
import locale

_CURRENT_LANG = "ru"

# Auto-detect language
try:
    loc = locale.getdefaultlocale()[0]
    if loc and not loc.lower().startswith("ru"):
        _CURRENT_LANG = "en"
    elif not loc:
        env_lang = os.environ.get("LANG", "").lower()
        if env_lang and not env_lang.startswith("ru"):
            _CURRENT_LANG = "en"
except Exception:
    _CURRENT_LANG = "ru"

STRINGS = {
    "ru": {
        # Banner & Guide
        "banner_subtitle": "Оптимизация • Разгрузка RAM • Лаунчер LeanHome",
        "guide_title": "┌─── 💡 КАК ПОДГОТОВИТЬ ТЕЛЕВИЗОР (ВКЛЮЧЕНИЕ ADB ОТЛАДКИ) ──────────────────┐",
        "guide_step1": "│ 1. На телевизоре откройте: «Настройки» ➔ «Об устройстве»                 │",
        "guide_step1_sub": "│    (на некоторых ТВ: «Настройки устройства» ➔ «Об устройстве»)          │",
        "guide_step2": "│ 2. Найдите строку «Сборка ОС Android TV» и нажмите на пульте ОК 7 раз     │",
        "guide_step2_sub": "│    (появится надпись: «Вы стали разработчиком!»)                         │",
        "guide_step3": "│ 3. Вернитесь назад ➔ пункт «Для разработчиков»                          │",
        "guide_step3_sub": "│    ➔ включите «Отладка по USB» (или «Отладка по сети»)                    │",
        "guide_step4": "│ 4. При первом подключении на экране ТВ появится окно запроса            │",
        "guide_step4_sub": "│    ➔ поставьте галочку «Всегда разрешать» и нажмите «ОК»                 │",
        "guide_bottom": "└────────────────────────────────────────────────────────────────────────────┘",

        # Step 1: ADB
        "step_check_adb": "[1/4] Проверка окружения ADB...",
        "adb_found": "✔ Найден ADB клиент:",
        "adb_not_found": "✖ ADB не найден в системе!",
        "adb_manual_prompt": "Укажите путь к бинарнику adb вручную:",
        "adb_prompt_path": "Путь к adb: ",
        "adb_success": "✔ ADB успешно подключен!",
        "adb_error": "Ошибка: ADB недоступен. Установите Android platform-tools.",

        # Step 2: Connection
        "step_connect": "[2/4] Подключение к Android TV",
        "active_connections": "Обнаружены активные подключения:",
        "no_connections": "Нет активных подключений к ТВ.",
        "btn_auto_scan": "🔍 Найти другие телевизоры в сети (Автопоиск)",
        "btn_auto_scan_rec": "🔍 Найти телевизоры в сети (Автопоиск) [Рекомендуется]",
        "btn_manual_ip": "⌨️  Подключить по IP вручную",
        "btn_refresh": "↻  Обновить список устройств",
        "btn_check_active": "↻  Проверить USB / активные соединения",
        "btn_guide": "💡 Как включить режим разработчика и отладку по ADB",
        "btn_switch_lang": "🌐 Переключить язык / Switch Language (RU / EN)",
        "btn_exit": "❌ Выход",
        "prompt_choice": "Выберите действие [1]: ",
        "invalid_choice": "Неверный ввод.",
        "device_selected": "✔ Выбрано устройство:",
        "scanning_network": "🔍 Сканирование локальной сети в поисках Android TV...",
        "found_tvs": "Найдены телевизоры в вашей сети:",
        "no_tvs_found": "Телевизоры не обнаружены в сети. Убедитесь, что ТВ включен в ту же сеть Wi-Fi/Ethernet.",
        "enter_ip": "Введите IP-адрес ТВ (например 192.168.1.50): ",
        "connecting_to": "Подключение к",
        "connect_success": "✔ Успешно подключено к",
        "connect_failed": "✖ Не удалось подключиться к",

        # Step 3: Diagnostics & RAM
        "diag_title": "[3/4] Диагностика ТВ и профиль оперативной памяти...",
        "diag_tv": "📺 ТВ:",
        "diag_model": "🏷️  Модель:",
        "diag_os": "🤖 Версия ОС:",
        "diag_ram_total": "Всего RAM:",
        "diag_ram_used": "Занято сейчас:",
        "diag_ram_free": "Свободно:",
        "diag_top_consumers": "🔥 Топ процессов по потреблению памяти:",
        "diag_ram_failed": "Не удалось получить детальную статистику RAM.",

        # Step 4: Main Menu
        "menu_header": "════════════════════ МЕНЮ ОПТИМИЗАЦИИ ════════════════════",
        "menu_opt1": "🌟 Рекомендуемая оптимизация (Всё в 1 клик)",
        "menu_opt1_desc1": "• Снимок экрана ДО",
        "menu_opt1_desc2": "• Удаление рекламы, PatchWall, телеметрии и мусора",
        "menu_opt1_desc3": "• Запрет фоновой записи микрофона и геолокации",
        "menu_opt1_desc4": "• Установка сверхбыстрого лаунчера LeanHome",
        "menu_opt1_desc5": "• Замер RAM ПОСЛЕ и сравнительный отчет",
        "menu_opt1_desc6": "• Снимок экрана ПОСЛЕ",
        "menu_opt2": "🛠️  Ручной выбор приложений для удаления",
        "menu_opt3": "🚀 Только установить / обновить лаунчер LeanHome",
        "menu_opt4": "🔒 Только отозвать права микрофона и геолокации",
        "menu_opt5": "📊 Повторно замерить память (RAM)",
        "menu_opt6": "📸 Сделать снимок экрана ТВ прямо сейчас",
        "menu_opt7": "↩️  Откат / Восстановление удаленных приложений",
        "menu_opt8": "🌐 Переключить язык / Switch Language (RU / EN)",
        "menu_opt0": "❌ Выход",
        "menu_footer": "══════════════════════════════════════════════════════════",
        "menu_prompt": "Выберите пункт [1]: ",
        "menu_invalid": "Неверный пункт меню.",
        "goodbye": "Спасибо за использование LeanTV! Хорошего дня!",

        # Recommended flow
        "rec_all_clean": "✔ Все известные мусорные приложения вендора и реклама уже удалены!",
        "rec_already_clean_prompt": "Телевизор уже очищен. Выполнить выгрузку фоновых процессов и замер памяти? (y/n) [y]: ",
        "rec_prep_title": "Подготовка к рекомендуемой оптимизации:",
        "rec_found_bloat": "• Найдено {count} мусорных приложений для удаления:",
        "rec_confirm_prompt": "Начать оптимизацию телевизора? (y/n) [y]: ",
        "cancelled_by_user": "Отменено пользователем.",

        # Manual debloat
        "manual_cat_title": "Список установленных приложений по категориям:",
        "manual_protected": "[ЗАЩИЩЕНО]",
        "manual_rec_delete": "[РЕКОМЕНДУЕТСЯ УДАЛИТЬ]",
        "manual_prompt": "Введите номера приложений через пробел или диапазон (например: 1, 3, 5-8):",
        "manual_prompt_sub": "(Введите 'all_rec' для выбора всех рекомендуемых или '0' для отмены)",
        "manual_none_selected": "Ничего не выбрано для удаления.",
        "manual_selected_count": "Выбрано для удаления ({count}):",
        "manual_confirm_prompt": "Удалить выбранные приложения ({count} шт.)? (y/n) [y]: ",
        "manual_removing_header": "══════════════ УДАЛЕНИЕ ВЫБРАННЫХ ПРИЛОЖЕНИЙ ══════════════",
        "manual_removing_item": "• Удаление: {title}... ",
        "manual_success": "✔ УСПЕШНО",
        "manual_error": "✖ ОШИБКА",
        "manual_skipped_crit": "Пропущено защищенное приложение: {title}",
        "manual_done": "✔ Удаление завершено. Успешно удалено: {success} из {total} приложений.",
        "press_enter": "Нажмите Enter для возврата в главное меню...",

        # Pipeline
        "pipeline_header": "══════════════ ВЫПОЛНЕНИЕ ОПТИМИЗАЦИИ ══════════════",
        "pipeline_step1": "📸 Создание контрольного снимка экрана ДО...",
        "pipeline_screen_saved": "✔ Снимок сохранен:",
        "pipeline_screen_err": "Предупреждение: не удалось сделать скриншот",
        "pipeline_step2": "🗑️ Удаление выбранного мусора ({count} приложений)...",
        "pipeline_item_removing": "• Удаление: {title}... ",
        "pipeline_item_success": "УСПЕШНО",
        "pipeline_item_skipped": "ПРОПУЩЕНО / ОШИБКА",
        "pipeline_debloat_total": "✔ Всего успешно выгружено: {count} приложений",
        "pipeline_step2_skip": "Удаление пакетов пропущено.",
        "pipeline_step3": "🔒 Отзыв фонового доступа к микрофону и геолокации...",
        "pipeline_perms_done": "✔ Опасные фоновые разрешения отозваны.",
        "pipeline_step3_skip": "Отзыв прав пропущен.",
        "pipeline_step4": "🚀 Установка сверхбыстрого лаунчера LeanHome...",
        "pipeline_launcher_success": "✔ Лаунчер LeanHome установлен и запущен на экране ТВ!",
        "pipeline_launcher_err": "✖ Ошибка: {msg}",
        "pipeline_step4_skip": "Установка лаунчера пропущена.",
        "pipeline_flushing": "⏳ Очистка кэшей и стабилизация памяти ТВ...",
        "pipeline_step5": "📊 Контрольный замер оперативной памяти (RAM) ПОСЛЕ...",
        "pipeline_results_header": "╔═══════════════════════════════════════════════════════════════════╗\n║                  🎉 РЕЗУЛЬТАТЫ ОПТИМИЗАЦИИ ТВ                     ║\n╚═══════════════════════════════════════════════════════════════════╝",
        "pipeline_ram_before": "• Занято ДО очистки:    {used:.0f} МБ из {total:.0f} МБ ({percent:.0f}%)",
        "pipeline_ram_after": "• Занято ПОСЛЕ очистки: {used:.0f} МБ из {total:.0f} МБ ({percent:.0f}%)",
        "pipeline_ram_freed": "• ОСВОБОЖДЕНО ПАМЯТИ:   +{freed:.0f} МБ! Память разгружена на {percent:.1f}%",
        "pipeline_ram_stable": "• Память стабилизирована: {free:.0f} МБ свободно.",
        "pipeline_screen_after_saved": "📸 Снимок экрана ПОСЛЕ сохранен: {path}",
        "pipeline_done": "✔ Оптимизация завершена! Телевизор стал работать ощутимо быстрее.",

        # Actions
        "install_launcher_title": "Установка и активация лаунчера LeanHome:",
        "install_launcher_disable_prompt": "Отключить тяжелые стоковые оболочки (PatchWall/Android TV Home)? (y/n) [y]: ",
        "install_launcher_success": "✔ Лаунчер LeanHome успешно установлен и запущен!",
        "install_launcher_error": "✖ Ошибка установки: {msg}",
        "revoke_perms_title": "Отзыв фонового доступа к микрофону и геолокации:",
        "revoke_perms_done": "✔ Права успешно отозваны.",
        "screenshot_taking": "Снимок экрана...",
        "screenshot_success": "✔ Снимок успешно сохранен: {path}",
        "screenshot_err": "✖ Ошибка снимка: {msg}",

        # Rollback
        "rollback_header": "══════════════ ВОССТАНОВЛЕНИЕ (ОТКАТ) ══════════════",
        "rollback_empty": "История удалений пуста или файл backup_history.json не найден.",
        "rollback_manual_prompt": "Введите имя пакета для восстановления вручную (или Enter для выхода): ",
        "rollback_item_restored": "✔ Пакет {pkg} успешно восстановлен!",
        "rollback_item_err": "✖ Ошибка восстановления пакета {pkg}.",
        "rollback_list_title": "Ранее удаленные приложения ({count}):",
        "rollback_opt_all": "[A] Восстановить ВСЕ приложения",
        "rollback_opt_sel": "[номера через пробел] Восстановить выбранные",
        "rollback_opt_back": "[0] Назад в меню",
        "rollback_action_prompt": "Выберите действие: ",
        "rollback_nothing_sel": "Ничего не выбрано.",
        "rollback_restoring_count": "Восстановление {count} приложений...",
        "rollback_status_restored": "ВОССТАНОВЛЕНО",
        "rollback_status_err": "ОШИБКА",
        "rollback_done": "✔ Процесс отката завершен.",

        "lang_switched": "✔ Язык переключен: Русский"
    },
    "en": {
        # Banner & Guide
        "banner_subtitle": "Optimization • RAM Debloating • LeanHome Launcher",
        "guide_title": "┌─── 💡 HOW TO PREPARE YOUR TV (ENABLE ADB DEBUGGING) ──────────────────────┐",
        "guide_step1": "│ 1. On your TV open: «Settings» ➔ «About»                                 │",
        "guide_step1_sub": "│    (on some TVs: «Device Preferences» ➔ «About»)                         │",
        "guide_step2": "│ 2. Find «Android TV OS build» and press OK on remote 7 times             │",
        "guide_step2_sub": "│    (a toast will say: «You are now a developer!»)                        │",
        "guide_step3": "│ 3. Go back ➔ select «Developer options»                                  │",
        "guide_step3_sub": "│    ➔ enable «USB debugging» (or «Network debugging»)                     │",
        "guide_step4": "│ 4. When connecting, a prompt will appear on your TV screen               │",
        "guide_step4_sub": "│    ➔ check «Always allow from this computer» and press «OK»              │",
        "guide_bottom": "└────────────────────────────────────────────────────────────────────────────┘",

        # Step 1: ADB
        "step_check_adb": "[1/4] Checking ADB environment...",
        "adb_found": "✔ Found ADB client:",
        "adb_not_found": "✖ ADB not found in system!",
        "adb_manual_prompt": "Specify path to adb binary manually:",
        "adb_prompt_path": "Path to adb: ",
        "adb_success": "✔ ADB connected successfully!",
        "adb_error": "Error: ADB is unavailable. Please install Android platform-tools.",

        # Step 2: Connection
        "step_connect": "[2/4] Connecting to Android TV",
        "active_connections": "Active connections detected:",
        "no_connections": "No active connections to TV.",
        "btn_auto_scan": "🔍 Search for TVs in local network (Auto-scan)",
        "btn_auto_scan_rec": "🔍 Search for TVs in network (Auto-scan) [Recommended]",
        "btn_manual_ip": "⌨️  Connect by IP manually",
        "btn_refresh": "↻  Refresh device list",
        "btn_check_active": "↻  Check USB / active connections",
        "btn_guide": "💡 How to enable Developer Options and ADB debugging",
        "btn_switch_lang": "🌐 Switch Language / Переключить язык (EN / RU)",
        "btn_exit": "❌ Exit",
        "prompt_choice": "Select action [1]: ",
        "invalid_choice": "Invalid selection.",
        "device_selected": "✔ Device selected:",
        "scanning_network": "🔍 Scanning local network for Android TVs...",
        "found_tvs": "Found Android TVs in your network:",
        "no_tvs_found": "No TVs found on the network. Make sure your TV is connected to the same Wi-Fi/Ethernet.",
        "enter_ip": "Enter TV IP address (e.g. 192.168.1.50): ",
        "connecting_to": "Connecting to",
        "connect_success": "✔ Successfully connected to",
        "connect_failed": "✖ Failed to connect to",

        # Step 3: Diagnostics & RAM
        "diag_title": "[3/4] TV Diagnostics and RAM Profile...",
        "diag_tv": "📺 TV:",
        "diag_model": "🏷️  Model:",
        "diag_os": "🤖 OS Version:",
        "diag_ram_total": "Total RAM:",
        "diag_ram_used": "Currently used:",
        "diag_ram_free": "Free RAM:",
        "diag_top_consumers": "🔥 Top processes by memory usage:",
        "diag_ram_failed": "Failed to retrieve detailed RAM statistics.",

        # Step 4: Main Menu
        "menu_header": "════════════════════ OPTIMIZATION MENU ════════════════════",
        "menu_opt1": "🌟 Recommended Optimization (All-in-1 Click)",
        "menu_opt1_desc1": "• Screenshot BEFORE",
        "menu_opt1_desc2": "• Remove ads, PatchWall, telemetry & vendor bloat",
        "menu_opt1_desc3": "• Revoke background mic & location permissions",
        "menu_opt1_desc4": "• Install ultra-lightweight LeanHome launcher",
        "menu_opt1_desc5": "• Measure RAM AFTER and produce comparison report",
        "menu_opt1_desc6": "• Screenshot AFTER",
        "menu_opt2": "🛠️  Manual Application Debloating",
        "menu_opt3": "🚀 Install / Update LeanHome Launcher only",
        "menu_opt4": "🔒 Revoke mic and location permissions only",
        "menu_opt5": "📊 Re-measure available memory (RAM)",
        "menu_opt6": "📸 Take TV screenshot now",
        "menu_opt7": "↩️  Rollback / Restore uninstalled applications",
        "menu_opt8": "🌐 Switch Language / Переключить язык (EN / RU)",
        "menu_opt0": "❌ Exit",
        "menu_footer": "══════════════════════════════════════════════════════════",
        "menu_prompt": "Select option [1]: ",
        "menu_invalid": "Invalid menu option.",
        "goodbye": "Thank you for using LeanTV! Have a great day!",

        # Recommended flow
        "rec_all_clean": "✔ All known vendor bloatware and ads are already removed!",
        "rec_already_clean_prompt": "TV is already cleaned. Kill dead processes and measure RAM? (y/n) [y]: ",
        "rec_prep_title": "Preparing for recommended optimization:",
        "rec_found_bloat": "• Found {count} bloatware applications to remove:",
        "rec_confirm_prompt": "Start TV optimization? (y/n) [y]: ",
        "cancelled_by_user": "Cancelled by user.",

        # Manual debloat
        "manual_cat_title": "Installed applications by category:",
        "manual_protected": "[PROTECTED]",
        "manual_rec_delete": "[RECOMMENDED TO REMOVE]",
        "manual_prompt": "Enter application numbers separated by space or range (e.g. 1, 3, 5-8):",
        "manual_prompt_sub": "(Enter 'all_rec' to select all recommended, or '0' to cancel)",
        "manual_none_selected": "Nothing selected for removal.",
        "manual_selected_count": "Selected for removal ({count}):",
        "manual_confirm_prompt": "Remove selected applications ({count} items)? (y/n) [y]: ",
        "manual_removing_header": "══════════════ REMOVING SELECTED APPLICATIONS ══════════════",
        "manual_removing_item": "• Removing: {title}... ",
        "manual_success": "✔ SUCCESS",
        "manual_error": "✖ ERROR",
        "manual_skipped_crit": "Skipped protected application: {title}",
        "manual_done": "✔ Removal complete. Successfully removed: {success} of {total} apps.",
        "press_enter": "Press Enter to return to main menu...",

        # Pipeline
        "pipeline_header": "══════════════ EXECUTING OPTIMIZATION ══════════════",
        "pipeline_step1": "📸 Taking BEFORE reference screenshot...",
        "pipeline_screen_saved": "✔ Screenshot saved:",
        "pipeline_screen_err": "Warning: failed to capture screenshot",
        "pipeline_step2": "🗑️ Removing selected bloatware ({count} applications)...",
        "pipeline_item_removing": "• Removing: {title}... ",
        "pipeline_item_success": "SUCCESS",
        "pipeline_item_skipped": "SKIPPED / ERROR",
        "pipeline_debloat_total": "✔ Successfully removed: {count} applications",
        "pipeline_step2_skip": "Package debloating skipped.",
        "pipeline_step3": "🔒 Revoking background microphone & location access...",
        "pipeline_perms_done": "✔ Insecure background permissions revoked.",
        "pipeline_step3_skip": "Permission revoking skipped.",
        "pipeline_step4": "🚀 Installing ultra-lightweight LeanHome launcher...",
        "pipeline_launcher_success": "✔ LeanHome launcher installed and running on TV screen!",
        "pipeline_launcher_err": "✖ Error: {msg}",
        "pipeline_step4_skip": "Launcher installation skipped.",
        "pipeline_flushing": "⏳ Flushing caches and stabilizing TV memory...",
        "pipeline_step5": "📊 Taking AFTER memory benchmark (RAM)...",
        "pipeline_results_header": "╔═══════════════════════════════════════════════════════════════════╗\n║                  🎉 TV OPTIMIZATION RESULTS                       ║\n╚═══════════════════════════════════════════════════════════════════╝",
        "pipeline_ram_before": "• Used BEFORE: {used:.0f} MB of {total:.0f} MB ({percent:.0f}%)",
        "pipeline_ram_after": "• Used AFTER:  {used:.0f} MB of {total:.0f} MB ({percent:.0f}%)",
        "pipeline_ram_freed": "• MEMORY FREED:  +{freed:.0f} MB! RAM load reduced by {percent:.1f}%",
        "pipeline_ram_stable": "• Memory stabilized: {free:.0f} MB free.",
        "pipeline_screen_after_saved": "📸 AFTER screenshot saved: {path}",
        "pipeline_done": "✔ Optimization complete! TV is noticeably faster and responsive.",

        # Actions
        "install_launcher_title": "Installing and activating LeanHome launcher:",
        "install_launcher_disable_prompt": "Disable heavy stock launchers (PatchWall/Android TV Home)? (y/n) [y]: ",
        "install_launcher_success": "✔ LeanHome launcher successfully installed and started!",
        "install_launcher_error": "✖ Installation error: {msg}",
        "revoke_perms_title": "Revoking background microphone & location access:",
        "revoke_perms_done": "✔ Permissions revoked successfully.",
        "screenshot_taking": "Taking screenshot...",
        "screenshot_success": "✔ Screenshot saved: {path}",
        "screenshot_err": "✖ Screenshot error: {msg}",

        # Rollback
        "rollback_header": "══════════════ ROLLBACK / RESTORE ══════════════",
        "rollback_empty": "Removal history is empty or backup_history.json not found.",
        "rollback_manual_prompt": "Enter package name to restore manually (or Enter to exit): ",
        "rollback_item_restored": "✔ Package {pkg} successfully restored!",
        "rollback_item_err": "✖ Failed to restore package {pkg}.",
        "rollback_list_title": "Previously removed applications ({count}):",
        "rollback_opt_all": "[A] Restore ALL applications",
        "rollback_opt_sel": "[space-separated numbers] Restore selected",
        "rollback_opt_back": "[0] Back to menu",
        "rollback_action_prompt": "Select action: ",
        "rollback_nothing_sel": "Nothing selected.",
        "rollback_restoring_count": "Restoring {count} applications...",
        "rollback_status_restored": "RESTORED",
        "rollback_status_err": "ERROR",
        "rollback_done": "✔ Rollback process finished.",

        "lang_switched": "✔ Language switched to: English"
    }
}

def get_lang() -> str:
    return _CURRENT_LANG

def set_lang(lang: str):
    global _CURRENT_LANG
    if lang in STRINGS:
        _CURRENT_LANG = lang

def toggle_lang() -> str:
    global _CURRENT_LANG
    _CURRENT_LANG = "en" if _CURRENT_LANG == "ru" else "ru"
    return _CURRENT_LANG

def t(key: str, **kwargs) -> str:
    text = STRINGS.get(_CURRENT_LANG, STRINGS["ru"]).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

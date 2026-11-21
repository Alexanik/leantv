# ⚡ LeanTV

> **Кроссплатформенный комплекс для оптимизации Android TV и ультра-легкий лаунчер LeanHome**  
> *Cross-platform Android TV debloater, RAM optimizer, and ultra-lightweight LeanHome launcher.*

[![GitHub Release](https://img.shields.io/github/v/release/Alexanik/leantv?color=brightgreen&label=Release)](https://github.com/Alexanik/leantv/releases)
[![Build & Release](https://github.com/Alexanik/leantv/actions/workflows/build.yml/badge.svg)](https://github.com/Alexanik/leantv/actions)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-orange.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux%20%7C%20Android%20TV-purple.svg)](#)

---

> [!IMPORTANT]
> **⚠️ Внимание: Совместимость и тестирование / Compatibility Note**  
> Проект LeanTV и лаунчер LeanHome разрабатывались и **тестировались исключительно на телевизорах Xiaomi (линейки Mi TV 4S, 4A, PatchWall)** на базе Android TV.  
> *This project has been specifically tested and validated exclusively on Xiaomi Android TVs (Mi TV / PatchWall).*

---

## 🌟 Основные возможности / Key Features

### 📺 1. Лаунчер LeanHome (TV Launcher)
* **Минимализм и скорость:** написан на чистом **Kotlin**, размер APK всего **~765 КБ**, потребление оперативной памяти менее **15 МБ** (в отличие от стоковых 150+ МБ).
* **OLED Pure Black:** фоновый цвет — абсолютно черный (`#000000`), контрастные карточки в стиле Charcoal с плавной фокус-анимацией (scale 1.08x).
* **Мгновенная реакция на события системы:**
  * 🔄 **Живое обновление приложений:** встроенный `BroadcastReceiver` мгновенно обновляет строку приложений при установке, удалении или обновлении любого APK без перезапуска.
  * 🔌 **Динамический опрос ТВ-входов:** аппаратные порты (HDMI 1, HDMI 2 ARC, HDMI 3, AV, Антенна) регистрируются через `TvInputCallback` с защитой от задержки инициализации драйверов при холодном старте ТВ.
* **Кастомизация под пульт:**
  * Удержание клавиши **OK (DPAD_CENTER)** на любой карточке переводит ее в режим перетаскивания и сортировки.
  * Длительное удержание открывает меню скрытия лишних входов и приложений.
  * Настраиваемый размер часов (Стандартный / Крупный / Максимальный).
* **Двуязычный интерфейс:** полная поддержка **Русского** и **Английского** языков.

### 💻 2. Комплекс оптимизации LeanTV (Desktop CLI)
* **Zero-Dependencies & All-in-One:** собирается в единый самодостаточный бинарник для **macOS**, **Windows** и **Linux** со встроенным ADB и APK лаунчера. Пользователю не нужно ничего устанавливать.
* **Умный автопоиск телевизоров в локальной сети:** многопоточный сканер (SSDP/UPnP + сканирование портов 5555, 8009, 6467) автоматически находит ваши ТВ в домашнем Wi-Fi/Ethernet.
* **Инструкция при первом запуске:** пошаговое руководство по включению режима разработчика и отладки по ADB прямо на экране терминала.
* **Глубокий анализ RAM:** чтение физической памяти ядра Linux (`/proc/meminfo`) и вывод ТОП процессов-потребителей оперативной памяти.
* **Рекомендуемая очистка в 1 клик:**
  * Создание контрольного снимка экрана ДО.
  * Удаление рекламы, рекомендаций и телеметрии вендора (Xiaomi PatchWall, Mi Analytics, Mi Legal, промо-каналы).
  * Отключение тяжелых сервисов Google (Google Katniss, постоянный микрофон, Google Play Music/Books/Movies, синхронизации).
  * Отзыв опасных разрешений фоновой записи звука и геолокации.
  * Установка и назначение лаунчера LeanHome по умолчанию с отключением тяжелых стоковых оболочек.
  * Очистка памяти и контрольный отчет с замером освобожденной RAM (+150..350 МБ) и снимком экрана ПОСЛЕ.
* **Менеджер отката (Rollback):** резервное сохранение удаленных пакетов и восстановление любого приложения в один клик.
* **Локализация:** автоопределение языка системы + горячее переключение **RU / EN**.

---

## 📥 Загрузка и запуск готовых версий / Download

Готовые автономные сборки доступны на странице **[GitHub Releases](https://github.com/Alexanik/leantv/releases)**:

| Платформа | Файл | Описание |
|---|---|---|
| **macOS** | `lean-macos.zip` | Автономный бинарник для Apple Silicon & Intel Mac |
| **Windows** | `lean-windows.zip` | Готовый `lean.exe` со встроенным ADB |
| **Linux** | `lean-linux.zip` | Исполняемый бинарник для x86_64 |
| **Android TV** | `lean_home.apk` | Автономный APK лаунчера для прямой установки на ТВ |

### Быстрый запуск на macOS / Linux:
```bash
unzip lean-macos.zip
chmod +x lean
./lean
```

### Быстрый запуск на Windows:
Распакуйте архив `lean-windows.zip` и дважды кликните по `lean.exe`.

---

## 🛠️ Сборка из исходников / Building from Source

### Требования:
* Python 3.8+ (для настольного приложения)
* JDK 17+ и Android SDK (для компиляции лаунчера)

### 1. Сборка Desktop CLI:
```bash
cd desktop_app

# macOS
./build_macos.sh

# Linux
./build_linux.sh

# Windows
build_windows.bat
```
Результат сборки появится в папке `desktop_app/dist/`.

### 2. Сборка лаунчера Android TV (LeanHome):
```bash
cd tv_launcher_source
./build.sh
```
Скрипт автоматически найдет установленные `aapt2`, `kotlinc`, `d8` и `apksigner`, скомпилирует ресурсы, соберет DEX и создаст подписанный `lean_home.apk`.

---

## 📂 Структура репозитория / Repository Structure

```text
leantv/
├── .github/
│   └── workflows/
│       └── build.yml             # GitHub Actions CI/CD (автосборка релизов)
├── desktop_app/                  # Кроссплатформенная утилита оптимизации
│   ├── main.py                   # Точка входа (CLI / GUI)
│   ├── cli.py                    # Интерактивный терминальный интерфейс
│   ├── lean.spec                 # Спецификация сборщика PyInstaller
│   ├── core/
│   │   ├── adb_client.py         # Кроссплатформенная обертка над ADB
│   │   ├── database.py           # База знаний пакетов (Xiaomi, Google, Streaming)
│   │   ├── debloater.py          # Логика деинсталляции и отзыва прав
│   │   ├── device_detector.py    # Определение модели и ОС телевизора
│   │   ├── i18n.py               # Модуль локализации (RU / EN)
│   │   ├── launcher_installer.py # Инсталлятор и активатор LeanHome
│   │   ├── network_scanner.py    # Zero-Config сетевой сканер ТВ
│   │   └── ram_monitor.py        # Анализатор оперативной памяти ядра Linux
│   └── resources/
│       ├── bin/                  # Кроссплатформенные бинарники platform-tools (ADB)
│       └── lean_home.apk         # Скомпилированный APK лаунчера
├── tv_launcher_source/           # Исходный код лаунчера LeanHome на Kotlin
│   ├── AndroidManifest.xml
│   ├── build.sh                  # Скрипт сборки APK
│   ├── res/                      # Векторная графика, разметка и локализация (values, values-ru)
│   └── src/com/minimal/tvlauncher/
│       ├── MainActivity.kt        # Основная логика, приемники событий, D-Pad
│       └── CapitalizedTextClock.kt
├── .gitignore
├── LICENSE
└── README.md
```

---

## 📄 Лицензия / License

Проект распространяется под открытой некоммерческой лицензией **[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](LICENSE)**.

* **Разрешено:** свободное использование, распространение, изучение и модификация кода в личных и некоммерческих целях с указанием авторства.
* **Запрещено:** любое коммерческое использование, перепродажа и монетизация. Производные работы должны распространяться на тех же условиях.

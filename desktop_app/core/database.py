import re
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class PackageMeta:
    package_name: str
    title_ru: str
    category: str          # "vendor_bloat", "google_bloat", "streaming", "safe_system", "other"
    description_ru: str
    recommended_action: str # "REMOVE", "DISABLE", "KEEP"
    risk_level: str        # "SAFE", "CAUTION", "CRITICAL"
    vendor: str            # "xiaomi", "google", "tcl", "sony", "generic"
    title_en: Optional[str] = None
    description_en: Optional[str] = None

    @property
    def title(self) -> str:
        from .i18n import get_lang
        if get_lang() == "en" and self.title_en:
            return self.title_en
        return self.title_ru

    @property
    def description(self) -> str:
        from .i18n import get_lang
        if get_lang() == "en" and self.description_en:
            return self.description_en
        return self.description_ru

CATEGORIES = {
    "vendor_bloat": "Реклама и аналитика ТВ (Xiaomi / TCL / Sony)",
    "google_bloat": "Службы Google (Ассистент, реклама, телеметрия)",
    "streaming": "Предустановленные медиа-приложения",
    "other": "Прочие сторонние приложения",
    "safe_system": "Критические системные компоненты (Защищено)"
}

def get_category_title(cat: str) -> str:
    from .i18n import get_lang
    if get_lang() == "en":
        categories_en = {
            "vendor_bloat": "Vendor Ads & Telemetry (Xiaomi / TCL / Sony)",
            "google_bloat": "Google Services (Assistant, telemetry, bloat)",
            "streaming": "Preinstalled Media & Streaming Apps",
            "other": "Other Third-Party Applications",
            "safe_system": "Critical System Components (Protected)"
        }
        return categories_en.get(cat, cat)
    return CATEGORIES.get(cat, cat)

DATABASE: Dict[str, PackageMeta] = {
    "com.miui.tv.analytics": PackageMeta(
        package_name="com.miui.tv.analytics",
        title_ru="Xiaomi TV Аналитика",
        title_en="Xiaomi TV Analytics",
        category="vendor_bloat",
        description_ru="Постоянный сбор телеметрии, логов и показов рекламы. Сильно грузит слабую память ТВ.",
        description_en="Telemetry, logs, and ad impressions collector.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.xiaomi.statistic": PackageMeta(
        package_name="com.xiaomi.statistic",
        title_ru="Xiaomi Статистика",
        title_en="Xiaomi Statistics",
        category="vendor_bloat",
        description_ru="Фоновый трекер действий пользователя и сетевой активности.",
        description_en="Background user behavior tracker.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.xm.webcontent": PackageMeta(
        package_name="com.xm.webcontent",
        title_ru="Xiaomi Web Content",
        title_en="Xiaomi Web Content",
        category="vendor_bloat",
        description_ru="Загрузчик рекламных баннеров и промо-страниц PatchWall.",
        description_en="Web overlay rendering ads and partner banners.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.xiaomo.tv.milegal": PackageMeta(
        package_name="com.xiaomo.tv.milegal",
        title_ru="Xiaomi Mi Legal",
        title_en="Xiaomi Mi Legal",
        category="vendor_bloat",
        description_ru="Юридическая документация и проверка лицензий Xiaomi.",
        description_en="Legal agreement prompt daemon.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "fusion.android.tv.demo": PackageMeta(
        package_name="fusion.android.tv.demo",
        title_ru="Витринный Демо-режим",
        title_en="Retail Demo Mode",
        category="vendor_bloat",
        description_ru="Рекламный демо-ролик для магазинов электроники. Бесполезен дома.",
        description_en="Store floor video loop demo.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.xiaomi.android.tvsetup.partnercustomizer": PackageMeta(
        package_name="com.xiaomi.android.tvsetup.partnercustomizer",
        title_ru="Партнерский настройщик Xiaomi",
        title_en="Xiaomi Partner Customizer",
        category="vendor_bloat",
        description_ru="Автоустановщик сторонних сервисов и рекламных партнеров.",
        description_en="Installs regional partner apps in background.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.xiaomi.amazon.alexa": PackageMeta(
        package_name="com.xiaomi.amazon.alexa",
        title_ru="Интеграция Amazon Alexa",
        title_en="Amazon Alexa Integration",
        category="vendor_bloat",
        description_ru="Фоновый сервис голосового помощника Alexa от Xiaomi.",
        description_en="Xiaomi Alexa background service.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.mitv.tvhome.atv": PackageMeta(
        package_name="com.mitv.tvhome.atv",
        title_ru="Xiaomi PatchWall",
        title_en="Xiaomi PatchWall",
        category="vendor_bloat",
        description_ru="Тяжелый рекламный рабочий стол Xiaomi. Постоянно подгружает рекламу и рекомендации.",
        description_en="Heavy ad-loaded stock launcher. Consumes 150+ MB RAM.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.mitv.tvhome.mitvplus": PackageMeta(
        package_name="com.mitv.tvhome.mitvplus",
        title_ru="Xiaomi MiTV+",
        title_en="Xiaomi MiTV+",
        category="vendor_bloat",
        description_ru="Витрина бесплатных интернет-каналов и промо-блоков Xiaomi.",
        description_en="Preinstalled ad-based streaming channels.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.mitv.tvhome.michannel": PackageMeta(
        package_name="com.mitv.tvhome.michannel",
        title_ru="Xiaomi Mi Channel",
        title_en="Xiaomi Mi Channel",
        category="vendor_bloat",
        description_ru="Рекламная лента каналов PatchWall.",
        description_en="Xiaomi proprietary FAST TV channels.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.mitv.overseaservice": PackageMeta(
        package_name="com.mitv.overseaservice",
        title_ru="Xiaomi Overseas Service",
        title_en="Xiaomi Overseas Service",
        category="vendor_bloat",
        description_ru="Служба региональной телеметрии и проверки региона для серверов Xiaomi.",
        description_en="Overseas regional cloud sync and telemetry.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.xiaomi.mimusic2": PackageMeta(
        package_name="com.xiaomi.mimusic2",
        title_ru="Xiaomi Mi Музыка",
        title_en="Xiaomi Mi Music",
        category="vendor_bloat",
        description_ru="Предустановленный плеер музыки со встроенными онлайн-рекомендациями.",
        description_en="Stock music player with online banners.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.mitv.videoplayer": PackageMeta(
        package_name="com.mitv.videoplayer",
        title_ru="Xiaomi Mi Видеоплеер",
        title_en="Xiaomi Mi Video Player",
        category="vendor_bloat",
        description_ru="Стоковый плеер Xiaomi со встроенной рекламой контента.",
        description_en="Stock video player with online recommendations.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.mitv.gallery": PackageMeta(
        package_name="com.mitv.gallery",
        title_ru="Xiaomi Галерея",
        title_en="Xiaomi Gallery",
        category="vendor_bloat",
        description_ru="Стоковая галерея фотографий Xiaomi.",
        description_en="Stock image gallery with cloud sync.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.xiaomi.mitv.mediaexplorer": PackageMeta(
        package_name="com.xiaomi.mitv.mediaexplorer",
        title_ru="Xiaomi Медиапроводник",
        title_en="Xiaomi Media Explorer",
        category="vendor_bloat",
        description_ru="Файловый менеджер Xiaomi с рекомендациями контента.",
        description_en="Stock file explorer.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.mitv.dream": PackageMeta(
        package_name="com.mitv.dream",
        title_ru="Xiaomi Заставка / Screensaver",
        title_en="Xiaomi Screensaver",
        category="vendor_bloat",
        description_ru="Рекламная экранная заставка Xiaomi.",
        description_en="Wallpaper screensaver showing partner ads.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.mitv.milinkservice": PackageMeta(
        package_name="com.mitv.milinkservice",
        title_ru="Xiaomi Mi Link",
        title_en="Xiaomi Mi Link",
        category="vendor_bloat",
        description_ru="Служба беспроводной связи устройств экосистемы Mi.",
        description_en="Proprietary screen casting background service.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.mitv.smartshare": PackageMeta(
        package_name="com.mitv.smartshare",
        title_ru="Xiaomi SmartShare",
        title_en="Xiaomi SmartShare",
        category="vendor_bloat",
        description_ru="Служба трансляции экрана с телефонов Xiaomi.",
        description_en="File sharing daemon consuming background RAM.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.xiaomi.wfdsinkhelperservice": PackageMeta(
        package_name="com.xiaomi.wfdsinkhelperservice",
        title_ru="Xiaomi WFD Sink Helper",
        title_en="Xiaomi WFD Sink Helper",
        category="vendor_bloat",
        description_ru="Фоновый сервис Miracast от Xiaomi.",
        description_en="Miracast helper daemon.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="xiaomi"
    ),
    "com.google.android.katniss": PackageMeta(
        package_name="com.google.android.katniss",
        title_ru="Google Ассистент (Katniss)",
        title_en="Google Assistant (Katniss)",
        category="google_bloat",
        description_ru="Голосовой помощник Google. Постоянно держит открытым микрофон и фоновые процессы, вызывает сильные лаги интерфейса.",
        description_en="Voice assistant with background mic listener.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.tvrecommendations": PackageMeta(
        package_name="com.google.android.tvrecommendations",
        title_ru="Google TV Рекомендации и Реклама",
        title_en="Google TV Recommendations",
        category="google_bloat",
        description_ru="Рекламные промо-ленты фильмов и сериалов на стоковом рабочем столе Android TV.",
        description_en="Google TV launcher ad and movie recommendation row.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.play.games": PackageMeta(
        package_name="com.google.android.play.games",
        title_ru="Google Play Игры",
        title_en="Google Play Games",
        category="google_bloat",
        description_ru="Игровой профиль и синхронизация достижений Google Play.",
        description_en="Gaming hub and cloud save service.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.videos": PackageMeta(
        package_name="com.google.android.videos",
        title_ru="Google TV / Google Play Фильмы",
        title_en="Google TV / Play Movies",
        category="google_bloat",
        description_ru="Магазин платной аренды фильмов Google.",
        description_en="Preinstalled Google store for buying movies.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.feedback": PackageMeta(
        package_name="com.google.android.feedback",
        title_ru="Google Feedback / Телеметрия",
        title_en="Google Feedback & Telemetry",
        category="google_bloat",
        description_ru="Сбор логов сбоев и фоновая отправка диагностических данных в Google.",
        description_en="Error reporting daemon and telemetry.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.marvin.talkback": PackageMeta(
        package_name="com.google.android.marvin.talkback",
        title_ru="Google TalkBack",
        title_en="Google TalkBack",
        category="google_bloat",
        description_ru="Голосовое озвучивание интерфейса для слабовидящих. Если не используется — сильно тормозит переключение карточек.",
        description_en="Screen reader for visually impaired.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.youtube.tvmusic": PackageMeta(
        package_name="com.google.android.youtube.tvmusic",
        title_ru="YouTube Music для ТВ",
        title_en="YouTube Music for TV",
        category="google_bloat",
        description_ru="Предустановленное приложение YouTube Music.",
        description_en="Preinstalled YouTube Music application.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.android.printspooler": PackageMeta(
        package_name="com.android.printspooler",
        title_ru="Диспетчер печати",
        title_en="Print Spooler",
        category="google_bloat",
        description_ru="Печать документов на сетевой принтер. На телевизоре совершенно бесполезна.",
        description_en="Printer management daemon (unused on TV).",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.tvlauncher": PackageMeta(
        package_name="com.google.android.tvlauncher",
        title_ru="Стоковый Android TV Launcher",
        title_en="Stock Android TV Launcher",
        category="google_bloat",
        description_ru="Тяжелый официальный рабочий стол с рекламой (тратит 80-120 МБ ОЗУ). Отключается для освобождения памяти и передачи кнопки Домой лаунчеру LeanHome.",
        description_en="Stock launcher consuming 100+ MB RAM.",
        recommended_action="DISABLE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.music": PackageMeta(
        package_name="com.google.android.music",
        title_ru="Google Play Музыка",
        title_en="Google Play Music",
        category="google_bloat",
        description_ru="Устаревший закрытый сервис музыки Google Play Music. Не работает, зря занимает память.",
        description_en="Defunct Google music service.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.books": PackageMeta(
        package_name="com.google.android.books",
        title_ru="Google Play Книги",
        title_en="Google Play Books",
        category="google_bloat",
        description_ru="Приложение чтения книг Google Play Books. Бесполезно на ТВ.",
        description_en="Google digital book store.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.apps.books": PackageMeta(
        package_name="com.google.android.apps.books",
        title_ru="Google Play Книги (v2)",
        title_en="Google Play Books (v2)",
        category="google_bloat",
        description_ru="Приложение чтения электронных книг Google Play Books.",
        description_en="Google digital book store.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.apps.magazines": PackageMeta(
        package_name="com.google.android.apps.magazines",
        title_ru="Google Play Пресса / Новости",
        title_en="Google News & Magazines",
        category="google_bloat",
        description_ru="Устаревший сервис новостей и журналов Google Play Крейсер/Пресса.",
        description_en="Defunct Google newsstand service.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.apps.tachyon": PackageMeta(
        package_name="com.google.android.apps.tachyon",
        title_ru="Google Duo / Meet",
        title_en="Google Duo / Meet",
        category="google_bloat",
        description_ru="Видеозвонки Google Duo. Не нужны на ТВ без веб-камеры.",
        description_en="Video calling app (unused on TV without webcam).",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.syncadapters.calendar": PackageMeta(
        package_name="com.google.android.syncadapters.calendar",
        title_ru="Google Синхронизация Календаря",
        title_en="Google Calendar Sync",
        category="google_bloat",
        description_ru="Фоновая синхронизация календаря Google. Постоянно висит в памяти ТВ.",
        description_en="Background calendar sync adapter.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.syncadapters.contacts": PackageMeta(
        package_name="com.google.android.syncadapters.contacts",
        title_ru="Google Синхронизация Контактов",
        title_en="Google Contacts Sync",
        category="google_bloat",
        description_ru="Фоновая синхронизация телефонной книги Google на ТВ.",
        description_en="Background contacts sync adapter.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.tv.bugreportsender": PackageMeta(
        package_name="com.google.android.tv.bugreportsender",
        title_ru="Google Отправка отчетов об ошибках",
        title_en="Google Error Reporter",
        category="google_bloat",
        description_ru="Служба сбора и отправки отчетов о сбоях в Google.",
        description_en="Background crash dump uploader.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.onetimeinitializer": PackageMeta(
        package_name="com.google.android.onetimeinitializer",
        title_ru="Google One Time Initializer",
        title_en="Google One Time Initializer",
        category="google_bloat",
        description_ru="Служба первичного запуска Google. Бесполезна после первой настройки.",
        description_en="One-time initial setup wizard helper.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.leanbacklauncher.recommendations": PackageMeta(
        package_name="com.google.android.leanbacklauncher.recommendations",
        title_ru="Google Leanback Рекомендации",
        title_en="Google Leanback Recommendations",
        category="google_bloat",
        description_ru="Фоновая служба устаревших рекомендаций Google Leanback.",
        description_en="Recommendations service.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.leanbacklauncher": PackageMeta(
        package_name="com.google.android.leanbacklauncher",
        title_ru="Google Leanback Launcher",
        title_en="Google Leanback Launcher",
        category="google_bloat",
        description_ru="Устаревший стоковый рабочий стол Leanback.",
        description_en="Legacy Android TV home launcher.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.google.android.tungsten.setupwraith": PackageMeta(
        package_name="com.google.android.tungsten.setupwraith",
        title_ru="Google Мастер настройки ТВ",
        title_en="Google TV Setup Wizard",
        category="google_bloat",
        description_ru="Мастер первоначальной настройки ТВ от Google. Не нужен при повседневном использовании.",
        description_en="Initial setup wizard.",
        recommended_action="REMOVE",
        risk_level="SAFE",
        vendor="google"
    ),
    "com.netflix.ninja": PackageMeta(
        package_name="com.netflix.ninja",
        title_ru="Netflix",
        title_en="Netflix",
        category="streaming",
        description_ru="Предустановленный клиент стриминга Netflix.",
        description_en="Official Netflix streaming client for Android TV.",
        recommended_action="KEEP",
        risk_level="SAFE",
        vendor="generic"
    ),
    "com.amazon.amazonvideo.livingroom": PackageMeta(
        package_name="com.amazon.amazonvideo.livingroom",
        title_ru="Amazon Prime Video",
        title_en="Amazon Prime Video",
        category="streaming",
        description_ru="Предустановленный клиент стриминга Amazon Prime Video.",
        description_en="Official Amazon Prime Video streaming client.",
        recommended_action="KEEP",
        risk_level="SAFE",
        vendor="generic"
    ),
    "ru.kinopoisk.tv": PackageMeta(
        package_name="ru.kinopoisk.tv",
        title_ru="Кинопоиск",
        title_en="Kinopoisk TV",
        category="streaming",
        description_ru="Онлайн-кинотеатр Кинопоиск от Яндекс.",
        description_en="Russian movie and series streaming application.",
        recommended_action="KEEP",
        risk_level="SAFE",
        vendor="generic"
    ),
    "ru.rutube.app": PackageMeta(
        package_name="ru.rutube.app",
        title_ru="RuTube для ТВ",
        title_en="RuTube TV",
        category="streaming",
        description_ru="Видеохостинг RuTube.",
        description_en="Russian video streaming platform for Android TV.",
        recommended_action="KEEP",
        risk_level="SAFE",
        vendor="generic"
    ),
    "org.videolan.vlc": PackageMeta(
        package_name="org.videolan.vlc",
        title_ru="VLC Media Player",
        title_en="VLC Media Player",
        category="streaming",
        description_ru="Популярный медиаплеер VLC.",
        description_en="Open source multi-format media player.",
        recommended_action="KEEP",
        risk_level="SAFE",
        vendor="generic"
    ),
    "org.xbmc.kodi": PackageMeta(
        package_name="org.xbmc.kodi",
        title_ru="Kodi Media Center",
        title_en="Kodi Media Center",
        category="streaming",
        description_ru="Медиацентр Kodi.",
        description_en="Home theater software and media hub.",
        recommended_action="KEEP",
        risk_level="SAFE",
        vendor="generic"
    ),
    "com.valvesoftware.steamlink": PackageMeta(
        package_name="com.valvesoftware.steamlink",
        title_ru="Steam Link",
        title_en="Steam Link",
        category="streaming",
        description_ru="Трансляция игр с компьютера через Steam.",
        description_en="Steam game streaming client.",
        recommended_action="KEEP",
        risk_level="SAFE",
        vendor="generic"
    ),
    "com.mediatek.tvinput": PackageMeta(
        package_name="com.mediatek.tvinput",
        title_ru="MediaTek TV Input Service (HDMI & Tuner)",
        title_en="MediaTek TV Input Service",
        category="safe_system",
        description_ru="КРИТИЧЕСКИ ВАЖНО: Аппаратный драйвер входов HDMI и тюнера. Удаление сломает отображение сигнала с HDMI!",
        description_en="Hardware HDMI, AV and tuner input provider.",
        recommended_action="KEEP",
        risk_level="CRITICAL",
        vendor="generic"
    ),
    "com.android.tv.settings": PackageMeta(
        package_name="com.android.tv.settings",
        title_ru="Настройки Android TV",
        title_en="Android TV Settings",
        category="safe_system",
        description_ru="КРИТИЧЕСКИ ВАЖНО: Системное меню настроек Wi-Fi, звука, экрана и Bluetooth.",
        description_en="System TV settings application.",
        recommended_action="KEEP",
        risk_level="CRITICAL",
        vendor="generic"
    ),
    "com.android.bluetooth": PackageMeta(
        package_name="com.android.bluetooth",
        title_ru="Bluetooth стек",
        title_en="Bluetooth Stack",
        category="safe_system",
        description_ru="КРИТИЧЕСКИ ВАЖНО: Отвечает за работу беспроводного пульта дистанционного управления.",
        description_en="Bluetooth device connectivity service.",
        recommended_action="KEEP",
        risk_level="CRITICAL",
        vendor="generic"
    ),
    "com.android.systemui": PackageMeta(
        package_name="com.android.systemui",
        title_ru="System UI",
        title_en="System UI",
        category="safe_system",
        description_ru="КРИТИЧЕСКИ ВАЖНО: Системная оболочка, уведомления и диалоги подтверждения.",
        description_en="Status bar, navigation and system overlay.",
        recommended_action="KEEP",
        risk_level="CRITICAL",
        vendor="generic"
    ),
    "com.android.vending": PackageMeta(
        package_name="com.android.vending",
        title_ru="Google Play Маркет",
        title_en="Google Play Store",
        category="safe_system",
        description_ru="Магазин приложений для установки и обновления софта.",
        description_en="Official Google app repository.",
        recommended_action="KEEP",
        risk_level="CAUTION",
        vendor="google"
    ),
}

def clean_app_title(pkg_name: str) -> str:
    parts = pkg_name.split(".")
    filtered = [p for p in parts if p not in ["com", "google", "android", "xiaomi", "mitv", "tv", "app", "apps"]]
    if filtered:
        words = []
        for part in filtered:
            subwords = re.sub(r"([a-z])([A-Z])", r" ", part).replace("_", " ").replace("-", " ").split()
            words.extend([w.capitalize() for w in subwords])
        if words:
            return " ".join(words)
    return pkg_name

def get_package_info(pkg_name: str) -> PackageMeta:
    if pkg_name in DATABASE:
        return DATABASE[pkg_name]

    friendly_title = clean_app_title(pkg_name)

    lower = pkg_name.lower()
    if any(k in lower for k in ["xiaomi", "miui", "mitv"]):
        return PackageMeta(
            package_name=pkg_name,
            title_ru=friendly_title,
            title_en=friendly_title,
            category="vendor_bloat",
            description_ru="Компонент Xiaomi",
            description_en="Xiaomi Component",
            recommended_action="KEEP",
            risk_level="CAUTION",
            vendor="xiaomi"
        )
    elif "google" in lower:
        return PackageMeta(
            package_name=pkg_name,
            title_ru=friendly_title,
            title_en=friendly_title,
            category="google_bloat",
            description_ru="Компонент Google",
            description_en="Google Component",
            recommended_action="KEEP",
            risk_level="CAUTION",
            vendor="google"
        )
    else:
        return PackageMeta(
            package_name=pkg_name,
            title_ru=friendly_title,
            title_en=friendly_title,
            category="other",
            description_ru="Пользовательское или стороннее приложение",
            description_en="User or third-party application",
            recommended_action="KEEP",
            risk_level="SAFE",
            vendor="generic"
        )

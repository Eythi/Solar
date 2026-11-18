#!/usr/bin/env python3
"""Builds the Solar website into the folder above this one.

Usage:  pip install markdown && python3 tools/build.py

Texts that change often live in content/: TERMS.md, PRIVACY.md and RELEASE-NOTES-*.md.
Edit them (for example, fill in the [placeholders] of the legal texts) and run this again.
Anything in square brackets in the legal texts is highlighted on the page as an unfilled field.
"""
import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / 'content'

# ---- links: change here, every page picks them up -------------------------------------------
DOWNLOAD_URL = 'https://github.com/Eythi/Solar-/releases/latest'
DISCORD_URL = 'https://discord.gg/c7Ptfdhr2p'
TELEGRAM_URL = ''  # e.g. https://t.me/your_channel; empty shows a placeholder
SITE_NAME = 'Solar'
# New product name: every visible "Solar" (texts, legal pages, file names) becomes this.
# Links (GitHub repo URL) keep the old spelling. Set to 'Solar' to switch back.
BRAND = 'Solar'
LATEST = '1.5.0'
APK_VERSION = '1.5.0'  # version of the current Solar.apk build
REPO_URL = 'https://github.com/Eythi/Solar-'  # public repository shown on the site

NAV = [
    ('index.html', 'Главная'),
    ('features.html', 'Возможности'),
    ('download.html', 'Скачать'),
    ('changelog.html', 'Что нового'),
    ('about.html', 'О проекте'),
    ('devparty.html', 'DEV-party'),
    ('community.html', 'Сообщество'),
]

ICONS = {
    'search': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    'queue': '<path d="M4 6h16M4 12h10M4 18h7"/><path d="m16 15 5 3-5 3z"/>',
    'heart': '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
    'wave': '<path d="M2 12c2-4 4-4 6 0s4 4 6 0 4-4 6 0"/><path d="M2 17c2-3 4-3 6 0s4 3 6 0 4-3 6 0" opacity=".5"/>',
    'mic': '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
    'text': '<path d="M4 6h16M4 11h16M4 16h9"/><circle cx="18" cy="18" r="3"/>',
    'down': '<path d="M12 4v11m0 0-4-4m4 4 4-4"/><path d="M5 20h14"/>',
    'stats': '<path d="M5 20V11M12 20V5M19 20v-7"/>',
    'phone': '<rect x="7" y="2" width="10" height="20" rx="2.5"/><path d="M11 18h2"/>',
    'pc': '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/>',
    'sliders': '<path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/>',
    'shield': '<path d="M12 3 5 6v6c0 4.4 3 7.8 7 9 4-1.2 7-4.6 7-9V6z"/><path d="m9 12 2 2 4-4"/>',
    'remote': '<rect x="3" y="5" width="11" height="14" rx="2"/><rect x="16" y="9" width="5" height="10" rx="1.5"/><path d="M8.5 15h0"/>',
    'focus': '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>',
    'chat': '<path d="M4 5h16v11H9l-5 4z"/>',
    'mini': '<rect x="3" y="4" width="18" height="16" rx="2"/><rect x="12" y="12" width="7" height="6" rx="1"/>',
}


def icon(name):
    return (f'<span class="ico" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg></span>')


def telegram_link(label='Telegram-канал', cls=''):
    if TELEGRAM_URL:
        return f'<a class="{cls}" href="{TELEGRAM_URL}" rel="noopener">{label}</a>'
    return f'<a class="{cls}" href="community.html#telegram">{label} <span class="ph">[ссылка]</span></a>'


def page(filename, title, description, body):
    nav = '\n'.join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == filename else ""}>{label}</a>'
        for href, label in NAV)
    full_title = BRAND if filename == 'index.html' else f'{title} · {BRAND}'
    _unused = SITE_NAME if filename == 'index.html' else f'{title} · {SITE_NAME}'
    doc = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(full_title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="theme-color" content="#0c0705">
<meta property="og:title" content="{html.escape(full_title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:type" content="website">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="aurora-3" aria-hidden="true"></div><div class="grain" aria-hidden="true"></div>
<a class="skip" href="#main">К содержимому</a>
<header class="site-head">
  <div class="wrap head-row">
    <a class="brand" href="index.html"><span class="logo" aria-hidden="true"></span>Solar</a>
    <button class="menu-btn" type="button" aria-label="Меню" aria-expanded="false" aria-controls="site-nav"><span></span><span></span><span></span></button>
    <nav class="nav" id="site-nav" aria-label="Разделы сайта">
{nav}
    </nav>
    <a class="head-gh" href="{REPO_URL}" rel="noopener" aria-label="Репозиторий на GitHub" title="Репозиторий на GitHub"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 .5a11.5 11.5 0 0 0-3.64 22.4c.58.1.79-.25.79-.56v-2c-3.2.7-3.88-1.37-3.88-1.37-.52-1.33-1.28-1.690-1.28-1.69-1.05-.71.08-.7.08-.7 1.16.08 1.770 1.19 1.77 1.19 1.03 1.77 2.7 1.26 3.36.96.1-.75.4-1.26.73-1.55-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.170 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.84 1.19 3.1 0 4.42-2.7 5.4-5.26 5.68.41.36.78 1.06.78 2.14v3.17c0 .31.21.67.8.56A11.5 11.5 0 0 0 12 .5z"/></svg></a>
    <a class="btn btn-sun btn-sm head-cta" href="download.html">Скачать</a>
  </div>
</header>
<main id="main">
{body}
</main>
<div class="foot-wave" aria-hidden="true"><svg viewBox="0 0 1440 120" preserveAspectRatio="none"><defs><linearGradient id="fw" x1="0" x2="1"><stop offset="0" stop-color="#ffd166"/><stop offset=".5" stop-color="#ff8a3d"/><stop offset="1" stop-color="#ff4d6d"/></linearGradient></defs><path class="w1" d="M0 60 C 240 10 480 110 720 60 S 1200 10 1440 60 V120 H0Z"/><path class="w2" d="M0 70 C 240 120 480 20 720 70 S 1200 120 1440 70 V120 H0Z"/></svg></div>
<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        <a class="brand" href="index.html"><span class="logo" aria-hidden="true"></span>Solar</a>
        <p class="muted" style="margin-top:12px;max-width:340px">Бесплатный некоммерческий музыкальный плеер для Windows, iPhone и Android. Разработка: QWENTITY TEAM.</p>
      </div>
      <div>
        <h4>Solar</h4>
        <ul>
          <li><a href="features.html">Возможности</a></li>
          <li><a href="download.html">Скачать</a></li>
          <li><a href="changelog.html">Что нового</a></li>
          <li><a href="{REPO_URL}" rel="noopener">Репозиторий на GitHub</a></li>
        </ul>
      </div>
      <div>
        <h4>Помощь</h4>
        <ul>
          <li><a href="install-ios.html">Установка на iPhone</a></li>
          <li><a href="about.html">О проекте</a></li>
          <li><a href="devparty.html">DEV-party</a></li>
          <li><a href="community.html">Сообщество</a></li>
        </ul>
      </div>
      <div>
        <h4>Документы</h4>
        <ul>
          <li><a href="terms.html">Пользовательское соглашение</a></li>
          <li><a href="privacy.html">Политика конфиденциальности</a></li>
        </ul>
      </div>
    </div>
    <div class="disclaimer">
      <p>Solar — независимый проект. Он не связан с ООО «Яндекс», VK, SoundCloud, Google (YouTube Music), Spotify, Apple Inc. и Discord Inc., не одобрен и не спонсируется ими. Названия и товарные знаки этих сервисов принадлежат их владельцам и упоминаются только для описания совместимости.</p>
      <p>Solar не хранит и не раздаёт музыку: каждый пользователь входит в собственные аккаунты и слушает то, что доступно ему по условиям этих сервисов.</p>
      <p>© 2026 QWENTITY TEAM</p>
    </div>
  </div>
</footer>
<script src="assets/site.js"></script>
<script src="assets/anim.js"></script>
<script src="assets/anim2.js"></script>
{'<script src="assets/three.min.js" defer></script><script src="assets/hero3d.js" defer></script>' if filename == 'index.html' else ''}
</body>
</html>
'''
    if BRAND != 'Solar':
        # replace the name everywhere except inside URLs (…/Solar-/releases)
        doc = re.sub(r'(?<![/\w])Solar(?!-/)', BRAND, doc)
    (ROOT / filename).write_text(doc, encoding='utf-8')


def phone(src, alt, cls=''):
    return f'<div class="phone {cls}"><img src="assets/img/{src}" alt="{alt}" width="390" height="844" loading="lazy"></div>'


# ============================================================================================
# Home
# ============================================================================================
def build_home():
    body = f'''
<div class="wrap">
  <section class="hero">
    <div>
      <span class="eyebrow"><span class="eq" aria-hidden="true"><i></i><i></i><i></i><i></i></span>Версия {LATEST}</span>
      <h1>Вся ваша музыка <span class="sun-text">в одном плеере</span></h1>
      <p class="lead">Solar собирает Яндекс Музыку, SoundCloud, VK, YouTube Music и файлы с диска в одну медиатеку, один поиск и одну очередь. Входите в свои аккаунты и слушайте без переключения между приложениями.</p>
      <div class="btn-row">
        <a class="btn btn-sun" href="download.html">Скачать Solar</a>
        <a class="btn btn-ghost" href="features.html">Что умеет Solar</a>
      </div>
      <div class="facts"><span>Бесплатно</span><span>Windows 10/11</span><span>iPhone, iOS 15+</span><span>Android, APK {APK_VERSION}</span></div>
      <div class="viz" aria-hidden="true">{''.join('<i></i>' for _ in range(48))}</div>
    </div>
    <div class="hero-phones" aria-hidden="true">
      <div class="css-sun"></div>
      <canvas id="hero3d"></canvas>
      {phone("ios-home.jpg", "", "p1")}
      {phone("ios-player.jpg", "", "p2")}
    </div>
  </section>

  <div class="marquee" aria-hidden="true"><div class="marquee-track">
    {''.join(f'<span><b>♪</b>{x}</span>' for x in ['Яндекс Музыка','SoundCloud','VK Музыка','YouTube Music','Файлы с диска','Караоке','Волна по треку','Офлайн','Звуковая сфера','«Мой Solar»','Эквалайзер','Мини-плеер'] * 2)}
  </div></div>

  <section class="stats" aria-label="Solar в цифрах">
    <div class="stat"><b data-count="5">5</b><span>источников музыки в одной медиатеке</span></div>
    <div class="stat"><b data-count="10">10</b><span>полос эквалайзера с пресетами</span></div>
    <div class="stat"><b data-count="3">3</b><span>платформы: Windows, iPhone, Android</span></div>
    <div class="stat"><b><span data-count="0">0</span>&nbsp;₽</b><span>стоит Solar, и так останется</span></div>
  </section>

  <section class="section">
    <div class="section-head"><h2>Разделы сайта</h2></div>
    <div class="grid g3">
      <a class="card" href="features.html">{icon("sliders")}<h3>Возможности</h3><p>Общий поиск и очередь, волна, караоке, офлайн, звуковая сфера и статистика «Мой Solar».</p><span class="more">Подробнее →</span></a>
      <a class="card" href="download.html">{icon("down")}<h3>Скачать</h3><p>Установщик и портативная версия для Windows, .ipa для iPhone и .apk для Android.</p><span class="more">К загрузке →</span></a>
      <a class="card" href="install-ios.html">{icon("phone")}<h3>Установка на iPhone</h3><p>Пошаговая инструкция: как поставить Solar без App Store через Sideloadly или Xcode.</p><span class="more">Инструкция →</span></a>
      <a class="card" href="changelog.html">{icon("stats")}<h3>Что нового</h3><p>История версий: от YouTube Music и караоке в 1.2 до «Моего Solar» и мини-плеера в {LATEST}.</p><span class="more">История версий →</span></a>
      <a class="card" href="devparty.html">{icon("mic")}<h3>DEV-party</h3><p>Общий голосовой канал в Discord: общение с разработчиками, идеи, баги и новые функции до релиза.</p><span class="more">Зайти →</span></a>
      <a class="card" href="community.html">{icon("remote")}<h3>Сообщество</h3><p>Сервер в Discord с кодом подтверждения аккаунта, новости в Telegram, отзывы и сообщения об ошибках.</p><span class="more">Присоединиться →</span></a>
    </div>
  </section>

  <section class="section">
    <div class="section-head"><h2>Источники музыки</h2><a href="features.html#sources">Как это работает →</a></div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Сервис</th><th>Статус</th><th>Что доступно</th></tr></thead>
        <tbody>
          <tr><td>Яндекс Музыка</td><td><span class="tag ok">Работает</span></td><td>Вход по коду на странице Яндекса, поиск, лайки, плейлисты, волна. VPN не нужен.</td></tr>
          <tr><td>SoundCloud</td><td><span class="tag ok">Работает</span></td><td>Поиск без входа, после входа видны лайки и плейлисты. В России открывается через встроенный обход на ПК.</td></tr>
          <tr><td>VK Музыка</td><td><span class="tag ok">Работает</span></td><td>«Моя музыка» и плейлисты из VK, песни находятся в Яндекс Музыке или SoundCloud.</td></tr>
          <tr><td>YouTube Music</td><td><span class="tag beta">Бета</span></td><td>Вход через Google, лайки, плейлисты и поиск. Звук берётся из Яндекс Музыки или SoundCloud.</td></tr>
          <tr><td>Файлы с диска</td><td><span class="tag ok">Работает</span></td><td>Папки сканируются автоматически на ПК, на iPhone файлы добавляются из приложения «Файлы».</td></tr>
          <tr><td>Spotify</td><td><span class="tag soon">Скоро</span></td><td>Интеграция готова, но пока закрыта для пользователей.</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="cta-strip">
    <div><h2>Solar {LATEST} уже вышел</h2><p>Звуковая сфера, главная-плеер с «Солнечной волной», жидкое стекло и новая иконка.</p></div>
    <div class="btn-row"><a class="btn btn-ghost" href="changelog.html#v{LATEST.replace(".", "-")}">Что нового</a><a class="btn btn-sun" href="download.html">Скачать</a></div>
  </section>
</div>'''
    page('index.html', 'Главная', 'Solar — бесплатный музыкальный плеер: Яндекс Музыка, SoundCloud, VK, YouTube Music и ваши файлы в одной медиатеке.', body)


# ============================================================================================
# Features
# ============================================================================================
def build_features():
    cards = [
        ('search', 'Один поиск', 'Ищет сразу во всех подключённых сервисах. Одинаковые треки из разных сервисов склеиваются в один.'),
        ('queue', 'Общая очередь', 'Трек из Яндекса, за ним SoundCloud, потом файл с диска. Недоступные треки плеер пропускает сам.'),
        ('heart', 'Единая коллекция', 'Лайки из всех сервисов в одном месте, смешанные плейлисты из разных источников, список дизлайков.'),
        ('wave', 'Солнечная волна', 'Поток музыки по вашему вкусу с выбором настроения, а ещё волна от любого выбранного трека.'),
        ('text', 'Тексты и караоке', 'Слова подсвечиваются ровно тогда, когда их поют. Тексты из нескольких источников, Solar выбирает лучший.'),
    ('wave', 'Звуковая сфера', 'Жидкая сфера на главной двигается под музыку: раздувается на басу, течёт быстрее на громких местах и рябит от высоких частот.'),
        ('down', 'Офлайн на телефоне', 'Скачивайте треки, плейлисты и коллекцию на iPhone и слушайте без интернета.'),
        ('stats', '«Мой Solar»', 'Статистика прослушиваний, любимые треки и артисты, тип слушателя и картинка «Поделиться итогами».'),
    ]
    grid = '\n'.join(f'<div class="card">{icon(i)}<h3>{t}</h3><p>{d}</p></div>' for i, t, d in cards)
    body = f'''
<div class="wrap">
  <section class="page-hero">
    <span class="eyebrow">Возможности</span>
    <h1>Что умеет Solar</h1>
    <p>Один плеер для всех сервисов, где у вас есть аккаунт. Всё, что ниже, есть в версии {LATEST}; различия между ПК и iPhone отмечены отдельно.</p>
  </section>

  <section class="section" style="padding-top:0">
    <div class="grid g4">
{grid}
    </div>
  </section>

  <section class="feature-row" id="sources">
    <div>
      <h2>Все источники в одной медиатеке</h2>
      <ul>
        <li><b>Яндекс Музыка.</b> Вход по коду на странице Яндекса, без VPN. Лайки, плейлисты, дизлайки треков и исполнителей.</li>
        <li><b>SoundCloud.</b> Поиск без входа, после входа видны лайки и плейлисты.</li>
        <li><b>VK Музыка.</b> Solar читает вашу «Мою музыку» и плейлисты и находит те же песни в Яндекс Музыке или SoundCloud. Новое подтягивается само два раза в день.</li>
        <li><b>YouTube Music (бета).</b> Лайки, плейлисты и поиск. Открытый плейлист можно добавить по ссылке без входа.</li>
        <li><b>Файлы с диска.</b> На ПК папки с музыкой сканируются автоматически.</li>
      </ul>
    </div>
    <div class="feature-media">{phone("ios-sources.jpg", "Экран «Источники музыки» в Solar на iPhone")}</div>
  </section>

  <section class="feature-row flip">
    <div>
      <h2>Плеер, который подстраивается</h2>
      <ul>
        <li><b>Волна по треку.</b> Бесконечный поток похожей музыки от выбранного трека, учитывает лайки и пропуски.</li>
        <li><b>Эквалайзер</b> на 10 полос с пресетами и <b>«Атмосфера»</b>: slowed + reverb, speed up, «Ночной» и «Концертный зал» (ПК).</li>
        <li><b>«Сцена»</b>: трек на всё окно с большой обложкой и светом в её цветах (ПК).</li>
        <li><b>«Живой цвет»</b>: фон и плеер окрашиваются в цвета обложки.</li>
        <li><b>Таймер сна</b> и режим <b>«Фокус»</b>: помодоро, во время перерыва музыка плавно затихает (ПК).</li>
      </ul>
    </div>
    <div class="feature-media">{phone("ios-player.jpg", "Полноэкранный плеер Solar на iPhone")}{phone("ios-queue.jpg", "Очередь воспроизведения в Solar")}</div>
  </section>

  <section class="feature-row">
    <div>
      <h2>Медиатека и статистика</h2>
      <ul>
        <li><b>«Моя коллекция»</b> собирает лайки из всех сервисов, смешанные плейлисты Solar можно собирать из треков любых источников.</li>
        <li><b>Раздел «VK Музыка»</b>: «Моя музыка» в её порядке, плейлисты VK и список песен, которые не нашлись.</li>
        <li><b>«Мой Solar»</b>: часы музыки, топ треков и артистов, в какие часы вы слушаете, серия дней подряд. Хранится только на устройстве.</li>
        <li><b>«В этот день»</b>: что вы слушали неделю, месяц, полгода и год назад.</li>
      </ul>
    </div>
    <div class="feature-media">{phone("ios-library.jpg", "Медиатека Solar на iPhone")}</div>
  </section>

  <section class="feature-row flip">
    <div>
      <h2>Удобно на ПК</h2>
      <ul>
        <li><b>Ctrl+K</b>: быстрый переход к страницам, плейлистам, трекам и действиям плеера.</li>
        <li><b>Мини-плеер</b> (Ctrl+M): карточка поверх окон, музыка не прерывается.</li>
        <li><b>Работа в трее</b>, автозапуск с Windows, глобальные горячие клавиши.</li>
        <li><b>Solar Connect</b>: телефон как пульт для компьютера и перенос музыки между устройствами.</li>
        <li><b>Статус в Discord</b> с кнопкой «Скачать Solar».</li>
        <li><b>Оформление</b>: цветовые палитры, обои из картинки или видео, стеклянный интерфейс.</li>
      </ul>
    </div>
    <div class="feature-media">{phone("ios-settings.jpg", "Настройки Solar")}</div>
  </section>

  <section class="section">
    <div class="section-head"><h2>ПК и iPhone: что отличается</h2></div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Функция</th><th>Windows</th><th>iPhone</th></tr></thead>
        <tbody>
          <tr><td>Общий поиск, очередь, коллекция</td><td>Да</td><td>Да</td></tr>
          <tr><td>Тексты и караоке</td><td>Да</td><td>Да</td></tr>
          <tr><td>Скачивание для офлайна</td><td>—</td><td>Да</td></tr>
          <tr><td>Эквалайзер и «Атмосфера»</td><td>Да</td><td>Нет, iOS не даёт обрабатывать такой звук</td></tr>
          <tr><td>Вход в SoundCloud и его лайки</td><td>Да</td><td>Только поиск и прослушивание</td></tr>
          <tr><td>Встроенный обход блокировок</td><td>Да</td><td>Нет</td></tr>
          <tr><td>Трей, автозапуск, горячие клавиши, мини-плеер</td><td>Да</td><td>—</td></tr>
          <tr><td>Экран блокировки и фоновое воспроизведение</td><td>—</td><td>Да</td></tr>
          <tr><td>Автообновление</td><td>Да</td><td>Нет, новая версия ставится заново</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section">
    <div class="card" style="display:grid;grid-template-columns:auto 1fr;gap:18px;align-items:start">
      {icon("shield")}
      <div>
        <h3>Ваши аккаунты остаются у вас</h3>
        <p>Токены музыкальных сервисов хранятся только на вашем устройстве в зашифрованном виде и в аккаунт Solar не попадают. Синхронизируются только коллекция, плейлисты и настройки оформления. Подробности в <a href="privacy.html">Политике конфиденциальности</a>.</p>
      </div>
    </div>
  </section>
</div>'''
    page('features.html', 'Возможности', 'Общий поиск и очередь, волна, караоке, офлайн, звуковая сфера, «Мой Solar» и другие возможности плеера Solar.', body)


# ============================================================================================
# Download
# ============================================================================================
def build_download():
    body = f'''
<div class="wrap">
  <section class="page-hero">
    <span class="eyebrow">Версия {LATEST}</span>
    <h1>Скачать Solar</h1>
    <p>Solar бесплатный. Официальные сборки лежат только на странице релизов и на нашем сервере в Discord: файлы из других мест могут быть изменены.</p>
  </section>

  <section class="section" style="padding-top:0">
    <div class="grid g3">
      <div class="card platform">
        {icon("pc")}
        <h3>Windows <span class="tag ok">Готово</span></h3>
        <ul>
          <li><code>Solar-Setup.exe</code>: установщик, обновляется сам. Рекомендуем.</li>
          <li><code>Solar.exe</code>: портативная версия без установки.</li>
          <li>Windows 10 или 11, x64.</li>
        </ul>
        <div class="btn-row"><a class="btn btn-sun" href="{DOWNLOAD_URL}" rel="noopener">Скачать для Windows</a></div>
      </div>
      <div class="card platform">
        {icon("phone")}
        <h3>iPhone <span class="tag ok">Готово</span></h3>
        <ul>
          <li><code>Solar.ipa</code>, ставится через Sideloadly или Xcode.</li>
          <li>iOS 15 и новее.</li>
          <li>Не из App Store: с бесплатным Apple ID приложение нужно переподписывать раз в 7 дней.</li>
        </ul>
        <div class="btn-row"><a class="btn btn-sun" href="{DOWNLOAD_URL}" rel="noopener">Скачать .ipa</a><a class="btn btn-ghost" href="install-ios.html">Как установить</a></div>
      </div>
      <div class="card platform">
        {icon("phone")}
        <h3>Android <span class="tag ok">APK {APK_VERSION}</span></h3>
        <ul>
          <li><code>Solar.apk</code>, версия {APK_VERSION}: звуковая сфера, главная-плеер, Solar Connect, офлайн. Ставится поверх прошлых версий.</li>
          <li>Не из Google Play: при установке разрешите установку из этого источника.</li>
          <li>Файл берите только со страницы релизов или с нашего Discord.</li>
        </ul>
        <div class="btn-row"><a class="btn btn-sun" href="{DOWNLOAD_URL}" rel="noopener">Скачать .apk</a></div>
      </div>
    </div>
  </section>

  <section class="section">
    <h2>Первый запуск</h2>
    <ol class="steps">
      <li><h3>Установите и откройте Solar</h3><p>На ПК запустите <code>Solar-Setup.exe</code>. На iPhone поставьте <code>.ipa</code> по <a href="install-ios.html">инструкции</a>.</p></li>
      <li><h3>Войдите в аккаунт Solar</h3><p>Через Google или по почте. При регистрации нового аккаунта нужен код подтверждения с нашего <a href="{DISCORD_URL}" rel="noopener">сервера в Discord</a>.</p></li>
      <li><h3>Подключите источники</h3><p>«Настройки → Источники музыки»: Яндекс Музыка, SoundCloud, VK, YouTube Music или папки с файлами.</p></li>
    </ol>
  </section>

  <section class="section">
    <h2>Если Windows или антивирус предупреждает</h2>
    <div class="note"><b>«Неизвестный издатель» в SmartScreen.</b> Сборки пока не подписаны сертификатом. Нажмите «Подробнее» → «Выполнить в любом случае».</div>
    <div class="note"><b>Антивирус ругается на WinDivert.</b> Это драйвер встроенного обхода блокировок (zapret). Многие антивирусы помечают его как riskware, это известное ложное срабатывание. Обход включается только по вашей кнопке в настройках.</div>
    <p class="muted">Исходный код и все релизы: <a href="{REPO_URL}" rel="noopener">репозиторий Solar на GitHub</a>.</p>
    <p class="muted">Устанавливая Solar, вы принимаете <a href="terms.html">Пользовательское соглашение</a> и <a href="privacy.html">Политику конфиденциальности</a>.</p>
  </section>
</div>'''
    page('download.html', 'Скачать', 'Скачать Solar для Windows, iPhone и Android.', body)


# ============================================================================================
# iOS install
# ============================================================================================
def build_ios():
    body = f'''
<div class="wrap">
  <section class="page-hero">
    <span class="eyebrow">Инструкция</span>
    <h1>Установка на iPhone</h1>
    <p>Solar нет в App Store, поэтому он ставится как файл <code>.ipa</code> с подписью вашего Apple ID. Это занимает 10–15 минут один раз и минуту при обновлении.</p>
  </section>

  <section class="section" style="padding-top:0">
    <div class="grid g3">
      <div class="card"><h3>Что нужно</h3><p>iPhone с iOS 15 или новее, кабель, компьютер на Windows или Mac и обычный бесплатный Apple ID.</p></div>
      <div class="card"><h3>Срок работы</h3><p>С бесплатным Apple ID приложение работает 7 дней, потом его нужно переподписать. Данные при этом не пропадают.</p></div>
      <div class="card"><h3>Безопасность</h3><p>Мы никогда не просим ваш пароль Apple ID. Его вводите только в Sideloadly или Xcode на своём компьютере.</p></div>
    </div>
  </section>

  <section class="section">
    <h2>Способ 1. Sideloadly (Windows или Mac)</h2>
    <ol class="steps">
      <li><h3>Скачайте файлы</h3><p><code>Solar.ipa</code> со <a href="download.html">страницы загрузки</a> и программу Sideloadly с её официального сайта. На Windows также нужен iTunes с сайта Apple (не из Microsoft Store).</p></li>
      <li><h3>Подключите iPhone</h3><p>Подключите телефон кабелем, разблокируйте и нажмите «Доверять этому компьютеру».</p></li>
      <li><h3>Установите Solar</h3><p>Откройте Sideloadly, перетащите <code>Solar.ipa</code> в окно, введите свой Apple ID и нажмите Start. Пароль может понадобиться ввести ещё раз и подтвердить кодом.</p></li>
      <li><h3>Разрешите разработчика</h3><p>На iPhone: Настройки → Основные → VPN и управление устройством → ваш Apple ID → «Доверять».</p></li>
      <li><h3>Включите режим разработчика (iOS 16+)</h3><p>Настройки → Конфиденциальность и безопасность → Режим разработчика → Вкл., перезагрузка, подтвердить.</p></li>
    </ol>
  </section>

  <section class="section">
    <h2>Способ 2. Xcode (только Mac)</h2>
    <p class="muted">Подходит, если вы собираете Solar из исходников. Нужен Mac с macOS 14+, Xcode 16+ и Node.js 20+.</p>
    <ol class="steps">
      <li><h3>Соберите веб-часть</h3><p>В папке проекта: <code>npm install</code>, затем <code>npm run ios</code> и <code>npm run ios:open</code>.</p></li>
      <li><h3>Настройте подпись</h3><p>Xcode → Settings → Accounts: добавьте Apple ID. В таргете App на вкладке Signing &amp; Capabilities включите Automatically manage signing, выберите Personal Team и задайте свой Bundle Identifier, например <code>com.yourname.solar</code>.</p></li>
      <li><h3>Запустите на телефоне</h3><p>Выберите iPhone рядом с кнопкой ▶ и нажмите Run (⌘R). Если телефон пишет «Ненадёжный разработчик», разрешите его, как в способе 1.</p></li>
    </ol>
  </section>

  <section class="section">
    <h2>После установки</h2>
    <div class="grid g2">
      <div class="card"><h3>Обновление и продление</h3><p>Каждые 7 дней (или с новой версией) повторите установку тем же способом. Коллекция и плейлисты хранятся в аккаунте Solar.</p></div>
      <div class="card"><h3>Что на iPhone работает иначе</h3><p>Нет эквалайзера, обхода блокировок и входа в SoundCloud. В России для SoundCloud нужен VPN на телефоне. Подробно в <a href="features.html">сравнении</a>.</p></div>
    </div>
    <h3 style="margin-top:28px">Частые проблемы</h3>
    <details><summary>Через 7 дней Solar не открывается</summary><div class="answer"><p>Закончилась подпись бесплатного Apple ID. Подключите телефон и установите <code>Solar.ipa</code> ещё раз.</p></div></details>
    <details><summary>«Ненадёжный корпоративный разработчик»</summary><div class="answer"><p>Настройки → Основные → VPN и управление устройством → ваш Apple ID → «Доверять».</p></div></details>
    <details><summary>Нет звука</summary><div class="answer"><p>Проверьте громкость. Переключатель «без звука» Solar не глушит.</p></div></details>
    <details><summary>Ошибка о занятом Bundle Identifier в Xcode</summary><div class="answer"><p>Бесплатный аккаунт не может взять занятый идентификатор. Поменяйте его на свой уникальный.</p></div></details>
    <p class="muted" style="margin-top:20px">Установка в обход App Store делается на ваш риск: Apple может отозвать подпись, а сам способ может противоречить её условиям. Подробнее в разделе 5 <a href="terms.html">Пользовательского соглашения</a>.</p>
  </section>
</div>'''
    page('install-ios.html', 'Установка на iPhone', 'Как установить Solar на iPhone без App Store: Sideloadly или Xcode, шаг за шагом.', body)


# ============================================================================================
# Changelog (from content/RELEASE-NOTES-*.md)
# ============================================================================================
def inline_md(text):
    text = html.escape(text, quote=False)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def release_html(path):
    raw = path.read_text(encoding='utf-8').split('\n---')[0]
    lines = raw.strip().splitlines()
    version = lines[0].lstrip('# ').replace('Solar ', '').strip()
    out, summary, in_list = [], '', False
    for line in lines[1:]:
        s = line.strip()
        if not s:
            continue
        if s.startswith('## '):
            if in_list:
                out.append('</ul>'); in_list = False
            out.append(f'<h3>{inline_md(s[3:])}</h3>')
        elif re.match(r'^\s*- ', line):
            nested = line.startswith('  ')
            if not in_list:
                out.append('<ul>'); in_list = True
            item = inline_md(s[2:])
            out.append(f'<li style="margin-left:{18 if nested else 0}px">{item}</li>')
        elif not summary and not out:
            summary = inline_md(s)
        else:
            if in_list:
                out.append('</ul>'); in_list = False
            out.append(f'<p>{inline_md(s)}</p>')
    if in_list:
        out.append('</ul>')
    anchor = 'v' + version.replace('.', '-')
    latest = ' <span class="tag ok">Текущая</span>' if version == LATEST else ''
    return version, anchor, f'''<article class="release" id="{anchor}">
  <div class="release-title"><h2>Solar {version}</h2>{latest}</div>
  <p class="summary">{summary}</p>
  {''.join(out)}
</article>'''


def build_changelog():
    files = sorted(CONTENT.glob('RELEASE-NOTES-*.md'),
                   key=lambda p: [int(x) for x in re.findall(r'\d+', p.stem)], reverse=True)
    releases = [release_html(p) for p in files]
    nav = '\n'.join(f'<a href="#{a}">Solar {v}</a>' for v, a, _ in releases)
    arts = '\n'.join(h for _, _, h in releases)
    body = f'''
<div class="wrap">
  <section class="page-hero">
    <span class="eyebrow">История версий</span>
    <h1>Что нового в Solar</h1>
    <p>Установленные копии для Windows обновляются сами. На iPhone новая версия ставится заново из файла <code>.ipa</code>.</p>
  </section>
  <div class="release-layout">
    <nav class="release-nav" aria-label="Версии">{nav}</nav>
    <div>{arts}</div>
  </div>
</div>'''
    page('changelog.html', 'Что нового', 'История версий Solar: новые функции, исправления и изменения на ПК и iPhone.', body)


# ============================================================================================
# About
# ============================================================================================
def build_about():
    body = f'''
<div class="wrap">
  <section class="page-hero">
    <span class="eyebrow">О проекте</span>
    <h1>Solar — <span class="sun-text">одно солнце</span> для всей музыки</h1>
    <p class="about-lead">Solar — бесплатный некоммерческий музыкальный плеер. Он собирает Яндекс Музыку, SoundCloud, VK, YouTube Music и файлы с диска в одну медиатеку, один поиск и одну очередь, чтобы не переключаться между приложениями.</p>
  </section>

  <section class="section" style="padding-top:0">
    <div class="grid g3">
      <div class="card">{icon("heart")}<h3>Зачем мы это делаем</h3><p>Музыка разбросана по разным сервисам, у каждого своё приложение и свои плейлисты. Solar соединяет их в одном месте и делает это красиво.</p></div>
      <div class="card">{icon("shield")}<h3>Ваши данные у вас</h3><p>Входы в сервисы и токены хранятся только на вашем устройстве в зашифрованном виде. Аккаунт Solar нужен лишь для синхронизации коллекции и настроек.</p></div>
      <div class="card">{icon("wave")}<h3>Бесплатно и без рекламы</h3><p>Solar не продаёт подписки и не показывает рекламу. Подписки на сами сервисы, если они нужны, оплачиваются у этих сервисов.</p></div>
    </div>
  </section>

  <section class="section">
    <h2>Коротко о главном</h2>
    <div class="table-wrap">
      <table>
        <tbody>
          <tr><th>Платформы</th><td>Windows 10/11 (x64), iPhone с iOS 15+, Android (APK {APK_VERSION})</td></tr>
          <tr><th>Текущая версия</th><td>{LATEST} для ПК и iPhone, <a href="changelog.html">история версий</a></td></tr>
          <tr><th>Источники</th><td>Яндекс Музыка, SoundCloud, VK Музыка, YouTube Music (бета), файлы с диска</td></tr>
          <tr><th>Музыка</th><td>Solar ничего не хранит и не раздаёт: вы слушаете то, что доступно вам в ваших аккаунтах</td></tr>
          <tr><th>Разработка</th><td>QWENTITY TEAM</td></tr>
          <tr><th>Исходный код</th><td><a href="{REPO_URL}" rel="noopener">{REPO_URL.replace("https://", "")}</a></td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section class="section">
    <h2>Полезно знать</h2>
    <div class="note"><b>SmartScreen и антивирус.</b> Сборки для Windows пока не подписаны сертификатом, а встроенный обход блокировок использует драйвер WinDivert, который антивирусы иногда помечают как riskware. Это известное ложное срабатывание.</div>
    <div class="note"><b>iPhone без App Store.</b> С бесплатным Apple ID приложение нужно переустанавливать раз в 7 дней, данные при этом сохраняются. <a href="install-ios.html">Инструкция по установке</a>.</div>
    <div class="note"><b>VPN.</b> Для Яндекс Музыки и VK не нужен. Для SoundCloud в России на ПК есть встроенный обход, на iPhone нужен VPN.</div>
  </section>

  <section class="cta-strip">
    <div><h2>Хотите поговорить с командой?</h2><p>Заходите в DEV-party, наш общий голосовой канал в Discord.</p></div>
    <div class="btn-row"><a class="btn btn-ghost" href="{REPO_URL}" rel="noopener">GitHub</a><a class="btn btn-sun" href="devparty.html">DEV-party</a></div>
  </section>
</div>'''
    page('about.html', 'О проекте', 'Что такое Solar, зачем он нужен, на каких устройствах работает и кто его делает.', body)


# ============================================================================================
# DEV-party
# ============================================================================================
def build_devparty():
    body = f'''
<div class="wrap">
  <section class="page-hero dp-hero">
    <div>
      <span class="eyebrow"><span class="live-dot" aria-hidden="true"></span>Голосовой канал в Discord</span>
      <h1><span class="sun-text">DEV-party</span></h1>
      <p class="about-lead">Общий голосовой канал на нашем сервере в Discord. Здесь можно поговорить с разработчиками Solar напрямую: задать вопрос, предложить идею, показать баг или просто посидеть в хорошей компании.</p>
      <div class="btn-row"><a class="btn btn-sun" href="{DISCORD_URL}" rel="noopener">Зайти в Discord</a><a class="btn btn-ghost" href="community.html">Все каналы связи</a></div>
    </div>
    <div class="card dp-voice" aria-hidden="true">
      <h3><span class="live-dot"></span>🔊 DEV-party</h3>
      <div class="dp-row talk"><span class="dp-av"></span>Разработчик<small>говорит</small></div>
      <div class="dp-row"><span class="dp-av b"></span>Тестер<small>в канале</small></div>
      <div class="dp-row"><span class="dp-av c"></span>Вы?<small>присоединяйтесь</small></div>
    </div>
  </section>

  <section class="section" style="padding-top:0">
    <h2>Что там происходит</h2>
    <div class="grid g3">
      <div class="card">{icon("chat")}<h3>Общение с разработчиками</h3><p>Спрашивайте о Solar что угодно: как устроена функция, почему сделано так, что будет дальше.</p></div>
      <div class="card">{icon("sliders")}<h3>Идеи и обсуждения</h3><p>Предлагайте функции и голосом обсуждайте их с командой. Многое в Solar появилось именно из таких разговоров.</p></div>
      <div class="card">{icon("focus")}<h3>Баги вживую</h3><p>Покажите ошибку через демонстрацию экрана: так её найдут и исправят быстрее, чем по описанию.</p></div>
      <div class="card">{icon("stats")}<h3>Новое раньше всех</h3><p>Разработчики показывают и обсуждают новые функции до выхода версии.</p></div>
      <div class="card">{icon("phone")}<h3>Помощь с установкой</h3><p>Не получается поставить .ipa или .apk? Разберёмся вместе по шагам.</p></div>
      <div class="card">{icon("heart")}<h3>Просто компания</h3><p>Можно просто зайти, послушать и пообщаться с теми, кто тоже пользуется Solar.</p></div>
    </div>
  </section>

  <section class="section">
    <h2>Как попасть</h2>
    <ol class="steps">
      <li><h3>Зайдите на сервер Solar в Discord</h3><p>По ссылке <a href="{DISCORD_URL}" rel="noopener">{DISCORD_URL.replace("https://", "")}</a>.</p></li>
      <li><h3>Найдите голосовой канал DEV-party</h3><p>Он в списке голосовых каналов сервера.</p></li>
      <li><h3>Подключайтесь</h3><p>Микрофон можно не включать: слушать и писать в чат канала тоже можно.</p></li>
    </ol>
    <p class="muted">Будьте вежливы: в канале действуют правила сервера и <a href="terms.html">Пользовательское соглашение</a>.</p>
  </section>
</div>'''
    page('devparty.html', 'DEV-party', 'DEV-party: общий голосовой канал Solar в Discord для общения с разработчиками.', body)


# ============================================================================================
# Community
# ============================================================================================
def build_community():
    tg_btn = (f'<a class="btn btn-sun" href="{TELEGRAM_URL}" rel="noopener">Открыть канал</a>' if TELEGRAM_URL
              else '<span class="btn btn-ghost" aria-disabled="true">Ссылка <span class="ph">[ссылка на канал]</span></span>')
    body = f'''
<div class="wrap">
  <section class="page-hero">
    <span class="eyebrow">Сообщество</span>
    <h1>Мы на связи</h1>
    <p>Новости, помощь с установкой, сообщения об ошибках и идеи для следующих версий.</p>
  </section>
  <section class="section" style="padding-top:0">
    <div class="grid g2">
      <div class="card big-card discord">
        {icon("chat")}
        <h3>Discord</h3>
        <p>Главное место сообщества: код подтверждения для нового аккаунта, помощь, обсуждения и тестовые сборки.</p>
        <div class="btn-row"><a class="btn btn-sun" href="{DISCORD_URL}" rel="noopener">Присоединиться</a></div>
      </div>
      <div class="card big-card telegram" id="telegram">
        {icon("remote")}
        <h3>Telegram</h3>
        <p>Канал с новостями: выход версий, анонсы и короткие видео о новых функциях.</p>
        <div class="btn-row">{tg_btn}</div>
      </div>
    </div>
  </section>
  <section class="section">
    <h2>Как помочь проекту</h2>
    <div class="grid g3">
      <div class="card"><h3>Сообщить об ошибке</h3><p>Опишите, что делали, что ожидали и что случилось. Укажите версию Solar и устройство.</p></div>
      <div class="card"><h3>Предложить идею</h3><p>Самые полезные идеи попадают в следующие версии, многие функции появились именно так.</p></div>
      <div class="card"><h3>Рассказать друзьям</h3><p>Кнопка «Скачать Solar» в вашем статусе Discord ведёт прямо на загрузку.</p></div>
    </div>
  </section>
  <section class="section">
    <h2>Правообладателям</h2>
    <p class="muted" style="max-width:720px">Solar не хранит и не распространяет музыку. Если вы считаете, что Solar нарушает ваши права, напишите по контактам из раздела 10 <a href="terms.html">Пользовательского соглашения</a>.</p>
  </section>
</div>'''
    page('community.html', 'Сообщество', 'Discord и Telegram Solar: новости, помощь и обратная связь.', body)


# ============================================================================================
# Legal pages (from content/TERMS.md and content/PRIVACY.md)
# ============================================================================================
def slug(text, i):
    return f's{i}'


def build_legal(src, filename, title, description, other_href, other_label):
    md = (CONTENT / src).read_text(encoding='utf-8')
    md = md.replace('(PRIVACY.md)', '([Политика конфиденциальности](privacy.html))')
    md = md.replace('(TERMS.md)', '([Пользовательское соглашение](terms.html))')
    body_html = markdown.markdown(md, extensions=['tables', 'sane_lists'])
    # Number h2 anchors and collect the table of contents
    toc = []

    def add_id(m):
        i = len(toc) + 1
        text = re.sub('<[^>]+>', '', m.group(1))
        toc.append((f's{i}', text))
        return f'<h2 id="s{i}">{m.group(1)}</h2>'
    body_html = re.sub(r'<h2>(.*?)</h2>', add_id, body_html)
    body_html = body_html.replace('<table>', '<div class="table-wrap"><table>').replace('</table>', '</table></div>')
    # Highlight [placeholders] that are not links
    body_html = re.sub(r'\[([^\[\]<>]{1,80})\]', r'<span class="ph" title="Нужно заполнить">[\1]</span>', body_html)
    toc_html = '\n'.join(f'<li><a href="#{a}">{html.escape(t)}</a></li>' for a, t in toc)
    body = f'''
<div class="wrap">
  <div class="page-hero" style="padding-bottom:16px">
    <div class="legal-switch">
      <a class="btn btn-sm {"btn-sun" if filename == "terms.html" else "btn-ghost"}" href="terms.html">Пользовательское соглашение</a>
      <a class="btn btn-sm {"btn-sun" if filename == "privacy.html" else "btn-ghost"}" href="privacy.html">Политика конфиденциальности</a>
    </div>
  </div>
  <div class="legal-layout">
    <nav class="toc" aria-label="Содержание"><p>Содержание</p><ol>{toc_html}</ol></nav>
    <article class="legal">{body_html}
      <p style="margin-top:2.5em"><a href="{other_href}">{other_label} →</a></p>
    </article>
  </div>
</div>'''
    page(filename, title, description, body)


def build_favicon():
    (ROOT / 'assets' / 'favicon.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        '<defs><radialGradient id="g" cx=".38" cy=".35" r=".7"><stop offset="0" stop-color="#ffe08a"/>'
        '<stop offset=".55" stop-color="#ff8a3d"/><stop offset="1" stop-color="#e8455f"/></radialGradient></defs>'
        '<rect width="64" height="64" rx="14" fill="#151019"/>'
        '<circle cx="32" cy="32" r="22" fill="none" stroke="#ff8a3d" stroke-opacity=".45" stroke-width="2"/>'
        '<circle cx="32" cy="32" r="15" fill="url(#g)"/></svg>', encoding='utf-8')


if __name__ == '__main__':
    build_favicon()
    build_home()
    build_features()
    build_download()
    build_ios()
    build_changelog()
    build_about()
    build_devparty()
    build_community()
    build_legal('TERMS.md', 'terms.html', 'Пользовательское соглашение',
                'Пользовательское соглашение Solar.', 'privacy.html', 'Политика конфиденциальности')
    build_legal('PRIVACY.md', 'privacy.html', 'Политика конфиденциальности',
                'Политика конфиденциальности Solar: какие данные обрабатываются и как их удалить.',
                'terms.html', 'Пользовательское соглашение')
    print('Built:', ', '.join(sorted(p.name for p in ROOT.glob('*.html'))))

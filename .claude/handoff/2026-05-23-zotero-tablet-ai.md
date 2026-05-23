# Handoff: Zotero + on-device AI на планшете

**Дата:** 2026-05-23
**Ветка:** `claude/zotero-pdf-reading-29xiX`
**Источник:** сессия Claude Code on the web с планшета
**Адресат:** Claude Code на десктоп-лэптопе, продолжающий эту ветку

---

## Что началось с малого

Запрос был: «убедись, что ты можешь читать PDF книги *Linear Algebra Done Right* — она у меня в Zotero».

Ответ: в облачном контейнере Claude Code on the web доступа к Zotero на планшете нет. Контейнер видит только свежий клон `qraveh/qodeh.com`. Дальше разговор расширился до архитектуры «как вообще дать ИИ полный доступ к планшету и его данным».

---

## Принятые архитектурные решения

### 1. Доступ к Zotero — через Web API, не «клонирование»

- **Включить** в Zotero iOS: `Settings → Account → File Syncing → Sync attachment files using → Zotero`. Бесплатно 300 МБ, дальше — план.
- **Создать API-ключ** на https://www.zotero.org/settings/keys (read access). Записать ключ и `userID`.
- **В environment Claude Code on the web** добавить env vars (переживают пересоздание контейнера):
  - `ZOTERO_API_KEY`
  - `ZOTERO_USER_ID`
- **Session-start hook** ставит `pyzotero`, тянет индекс библиотеки в `/tmp` при старте.
- В работе: `zot.items(q="...")` → найти attachment_key → `zot.file(attachment_key)` → `Read` или `pdftotext`.

**WebDAV-вариант:** если файлы синхронизируются не в Zotero Storage, а в WebDAV (Nextcloud и т.п.), API файлы не отдаст — нужен отдельный путь через `webdavclient3` + WebDAV-креды.

### 2. ИИ, управляющий планшетом — стек из трёх слоёв (Android)

Платформа выбрана: **Android** (Pixel/Samsung). На iPad универсального драйвера UI не получить — Apple запрещает на уровне ОС.

- **Слой 1 — системный:** Gemini как Assistant по умолчанию. Покрывает Gmail/Drive/Calendar/Keep/Maps. «80% повседневности».
- **Слой 2 — UI-агент произвольных приложений:** **DroidRun** (приоритет, лучший UX), альтернативы — Mobile-Agent-v3, AppAgent. Работают через Android Accessibility Service. Мозг — Claude API.
- **Слой 3 — долгие/тяжёлые задачи:** Claude Agent SDK + Computer Use в облачной VM, доступ из чата на планшете. Сюда же — Zotero backend из решения №1.

**Полированного однопродуктового решения «поставил и работает» в мае 2026 нет.** Через 12–18 месяцев это изменит Apple/Google на уровне ОС.

### 3. Финальная схема: настройка через USB с лэптопа, автономная работа на планшете

Решение, к которому пришли в итоге: **bootstrap планшета делается с десктопа через ADB**, дальше планшет живёт сам.

Что Claude Code на лэптопе может через ADB по USB (root не нужен):
- Установка/удаление APK (`adb install`, `pm uninstall --user 0`).
- **Включение Accessibility Service одной командой:**
  `adb shell settings put secure enabled_accessibility_services <pkg>/<service>`
- Выдача runtime-permissions через `pm grant`.
- Подсев конфига: `adb push` или `am start --es <key> <value>`.
- Системные настройки через `settings put`.
- Файлы: `adb push`/`adb pull`.
- UI-автоматизация: `input tap/swipe/text`, `screencap`, scrcpy.
- Диагностика: `logcat`, `bugreport`.

Чего ADB не делает без root: чтение private storage других приложений, обход SafetyNet, гарантия работы в фоне против Doze.

---

## Что НЕ делалось в этой сессии (сознательно отложено)

Я предлагал заготовить под этот сценарий:
- `scripts/tablet/` с bootstrap-скриптами (install-droidrun.sh, enable-accessibility.sh, daily-backup.sh)
- session-start hook + `scripts/zotero_get.py` для слоя 3
- Минимальный relay-сервис между on-device агентом и облачной «головой»

Пользователь решил всё это делать с десктопа напрямую («десктоп сделает лучше тебя»). Поэтому ничего из этого в репо нет — только этот handoff.

---

## Что должен сделать десктопный Claude Code

В порядке приоритета:

1. **Поднять Zotero backend** (решение №1). Шаги:
   - Проверить, что у пользователя файлы синхронизируются именно в Zotero Storage (не WebDAV).
   - Получить от пользователя `ZOTERO_API_KEY` и `ZOTERO_USER_ID`, поместить в `.env` или secure storage лэптопа.
   - Написать `scripts/zotero/get.py` (поиск + скачивание PDF по запросу). Зависимость: `pyzotero`.
   - Smoke test: найти и прочитать первые страницы *Linear Algebra Done Right*. **Это исходный запрос, ради которого всё началось.**

2. **Подготовить bootstrap планшета через ADB.** Каталог `scripts/tablet/`:
   - `00-check-device.sh` — `adb devices`, версия Android, свободное место.
   - `10-install-droidrun.sh` — скачать актуальный релиз с GitHub, поставить.
   - `20-enable-accessibility.sh` — выдать accessibility-права DroidRun из ADB.
   - `30-configure-agent.sh` — подсунуть Anthropic API key в DroidRun (точный механизм зависит от версии DroidRun, посмотреть их docs).
   - `40-smoke-test.sh` — запустить DroidRun, `screencap`, проверить.
   - Перед массовыми `pm uninstall`/`pm disable-user` — всегда показывать список и ждать подтверждения.

3. **Безопасность:**
   - Не коммитить ключи (`.env` в `.gitignore`).
   - После настройки выключить USB Debugging на планшете, оставить включённым только когда нужно.
   - DroidRun даёт ему уровень root над UI — обращаться с этим как с sudo.

---

## Контекст репозитория

- Hugo-сайт (`hugo.yaml`, `content/`, `themes/`).
- К AI/ADB/Zotero инфраструктуре никакого отношения сайт не имеет — всё это будет рядом, в `scripts/` и `.claude/`.
- Текущая ветка `claude/zotero-pdf-reading-29xiX` создана специально под эту задачу.

---

## Открытые вопросы к пользователю

- Какой именно Android-планшет (Pixel Tablet / Galaxy Tab S? / другое)? От этого зависит, какие OEM-фичи доступны (Galaxy AI, Pixel Gemini-фичи).
- WebDAV или Zotero Storage для файлов?
- План Zotero (300 МБ хватит? нужен ли paid)?
- DroidRun или сразу Mobile-Agent? (DroidRun проще стартовать.)

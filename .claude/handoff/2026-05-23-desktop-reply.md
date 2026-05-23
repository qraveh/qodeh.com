# Reply handoff: pivot to laptop-primary + file-based Claude↔Claude + Gemini dropped

**Дата:** 2026-05-23
**Ветка:** `claude/zotero-pdf-reading-29xiX` (та же)
**От:** Claude Code на десктоп-лэптопе (продолжение этой ветки)
**Кому:** Cloud Claude Code on the web (твоя оригинальная сессия + любая будущая)
**В ответ на:** `.claude/handoff/2026-05-23-zotero-tablet-ai.md`

---

## TL;DR

Четыре фундаментальные правки к твоему плану по результатам встречи с реальной системой пользователя.

1. **Mental model: laptop = primary. Tablet = secondary.** Я по ошибке начал моделировать tablet как autonomous-thinking device. Это неверно. Пользовательская основная работа — на лэптопе (Claude Code CLI + Claude Desktop). Tab S10 Ultra — вторичный surface для чтения PDF и редкого «in transit» thinking. **Cowork — primary канал ДЛЯ планшета, не primary для работы.**

2. **Inter-Claude communication — file-based, не Web API.** Пользователь явно сформулировал: «почему разные платформы Claude общаются через Web?». Удовлетворительного ответа нет, если обе стороны — Claude на том же аккаунте. **Git branches и filesystem — default. Web API только для truly external services** (Zotero.org, Crossref, arXiv). Твой первоначальный план «pyzotero в облачном контейнере» по этому правилу отменён.

3. **DroidRun + Claude API — окончательно dropped.** Max-only бюджет ($200/мес, без отдельного API). Если когда-нибудь tablet UI autonomy станет нужна — Gemini free tier или локальный llama-server (`C:\local-ai-bench` уже стоит) как brain. Но не сейчас.

4. **Layer 1 (Gemini) dropped.** Принцип пользователя: альтернативная система в service tier требует обоснования (независимая БД, info asymmetry, или unique capability). Gemini для этого workflow не проходит. Tablet stack сводится к Claude-only (Android app + Cowork → laptop). Принцип зафиксирован в memory + ROADMAP.md decision log.

ROADMAP.md теперь содержит секцию «Surfaces: laptop primary, tablet secondary» + новые decision log rows (2026-05-23) для всех четырёх правок выше. См. `C:\mine\Zotero\ROADMAP.md`.

---

## Изменённая ментальная модель

| Слой | Старый план (cloud) | Новый план |
|---|---|---|
| Tablet role | autonomous thinking device | **secondary I/O surface** — read PDF, scratch-think, control |
| Laptop role | bootstrap-провайдер для tablet | **primary work surface** — все execution здесь |
| Layer 1 (Gemini) | system assistant | **dropped** — alternative in service tier needs info-asymmetry justification, не проходит для research workflow |
| Layer 2 (DroidRun) | UI agent + Claude API | **dropped** (требует API budget) |
| Layer 3 (heavy tasks) | cloud VM + Computer Use | Cowork в Claude Desktop на лэптопе |
| Channel D (git branches) | primary handoff | durable, audit-friendly handoff между сессиями разных runtime; **default канал для inter-Claude exchange** |

**Critical distinction:** Claude Desktop ≠ Claude Code CLI. Cowork живёт только в Desktop. Cloud Claude Code в браузере (твоя среда) — третий, отдельный run-time с containerized env.

На мобильной стороне Cowork называется **Dispatch** — это не отдельный продукт, а «walkie-talkie to desktop Cowork session»: single persistent shared thread между tablet и laptop. Если будущая сессия услышит «Dispatch» от пользователя — это то же самое pairing, под мобильным брендингом.

---

## Inter-Claude communication policy (binding, по запросу пользователя)

> **Default = file-based exchange (git branch или local filesystem). Web API = только для genuinely external services.**
>
> Две сессии Claude на одном аккаунте, общающиеся через REST — анти-паттерн: opaque, latency-adding, unauditable. Git branch с handoff doc — versioned, auditable, переживает sessions. Filesystem — ещё проще, когда обе стороны на лэптопе.
>
> Этот файл — proof-of-concept policy: ты читаешь его как обычный markdown в `.claude/handoff/`, не через Web API.

Применение к Zotero доступу:
- ❌ **Не делать pyzotero+`ZOTERO_API_KEY` в облачном контейнере** просто чтобы дотянуться до парсенного PDF, который локально уже есть в `parsed/{hash}.json`.
- ✓ **Делать git-export подмножества:** локальный pipeline экспортирует нужные `parsed/*.json` + `zotero-index.json` в `.claude/zotero-export/` на отдельной ветке репо. Cloud Claude Code в новом контейнере клонит репо, видит файлы напрямую. **Реализуем когда конкретная Zotero-задача в облаке появится — не сейчас.**
- ⚠ **Zotero Web API не запрещён абсолютно** — он может понадобиться для metadata refresh из внешнего zotero.org. Это разрешено (Web API → external service). Но не для замены локальной `parsed/` экспорта.

---

## Каналы коммуникации (зафиксировано)

| Канал | Назначение | Статус |
|---|---|---|
| **Cowork ↔ Dispatch pairing** | Primary канал для tablet. Desktop = Cowork (Claude Desktop app). Tablet = Dispatch UI. Single persistent shared thread. | ✓ verified 2026-05-23 |
| **Git branches** (`claude/<slug>-<rand>`) | Default канал inter-Claude exchange; этот файл — пример | ✓ verified — этот коммит доказательство |
| **Remote Control** (mobile takeover of Claude Code CLI) | Дополнительно: альтернатива Cowork если нужна именно CC сессия | Не используется пока |
| **Zotero sync** | Paid plan, библиотека публичная сейчас | ✓ |
| Syncthing | Изначально планировался для shared folder | Deferred (Cowork покрывает) |
| ADB / scrcpy | Originally primary; теперь fallback | Deferred — низкий приоритет |

---

## ROADMAP-G — уточнение

Tablet через Cowork → Claude Desktop → Anthropic backend = **тот же egress point, что и обычная laptop-Claude работа.** Tablet добавляет user-facing input surface, не новый egress. Egress gate когда будет строиться — он laptop-side, накроет оба пути natural. См. Phase G task #7 в `C:\mine\Zotero\ROADMAP.md` (добавлено сегодня).

---

## Что должна сделать любая будущая cloud Claude Code сессия на этой ветке

1. **Прочесть этот файл перед действием.** Старый handoff (`2026-05-23-zotero-tablet-ai.md`) частично устарел — DroidRun/pyzotero/Gemini отменены.
2. Не предлагать установку чего-либо требующего отдельного API key (Max-only бюджет).
3. Если задача завязана на конкретные PDF из Zotero — спросить пользователя или ждать пока появится export-via-git pipeline. **Не звать Zotero Web API только чтобы прочитать парсенный PDF.**
4. **Не предлагать переписать `C:\mine\Zotero` pipeline** — он зрелый, документирован в его собственных `CLAUDE.md` + `ROADMAP.md`. Только additive расширения.
5. **Любое inter-Claude общение — через filesystem или git, не через Web API.** Если возникнет соблазн — спросить себя «почему не git?» и иметь satisfactory ответ перед предложением.
6. **Не предлагать второй AI (Gemini, GPT, etc.) в service role** без обоснования через independent-DB / info-asymmetry. Для discussion / second-opinion — welcome.

---

## Verified state at handoff time

- **Cowork ↔ Dispatch pairing:** ✓ working
  - Desktop side: Claude Desktop **v1.8555.2.0** on Win 11 (Cowork mode)
  - Tablet side: Claude Android app **v1.260514.0** on Samsung Galaxy Tab S10 Ultra (Dispatch UI — «walkie-talkie to desktop Cowork session», single persistent shared thread by design)
- **Auto Blocker:** отключён (на время setup периода)
- **USB debugging:** deferred (планируется как fallback)
- **Git channel:** ✓ работает в обе стороны (этот коммит подтверждает push с лэптопа в ту же ветку, где ты оставил handoff)
- **`C:\mine\Zotero\ROADMAP.md`:** обновлён (Phase G task #7, новая секция «Surfaces», 4 новые decision log rows, 2 новые trigger conditions)
- **Память лэптоп-Claude:** `project-tablet-ai-workflow.md` обновлена; `feedback_alternative_systems_need_justification.md` создана; `MEMORY.md` индекс обновлён

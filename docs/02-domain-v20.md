# 02. Домен: чарник Vampire: The Masquerade V20

Справочник по анатомии листа персонажа V20 — основа для [модели данных](03-data-model.md),
парсера справочников и валидации создания персонажа. Здесь — **структура и
механика**, без дословных текстов из книг (см. [юридические ограничения](#юридические-ограничения)).

> Терминология: «точки» (dots) — рейтинг трейта, обычно 1–5. «Чарник» — лист
> персонажа. «Квента» — предыстория/описание персонажа.

## 1. Концепция (шапка)

- Name, Player, Chronicle
- **Nature** и **Demeanor** — архетипы (Natura/Demeanor) из списка (Architect,
  Bon Vivant, Caregiver, Director, Survivor, ...). Nature влияет на восстановление Willpower.
- Concept (свободный текст)
- **Clan** — клан вампира
- **Generation** — поколение (по умолчанию 13-е)
- **Sire** — сир (создатель)
- **Sect** — Camarilla / Sabbat / Anarch / Independent

## 2. Атрибуты (Attributes) — 9 трейтов, 1–5 точек

Три категории по три атрибута. Каждый атрибут стартует с 1 «бесплатной» точки.

| Physical | Social | Mental |
|----------|--------|--------|
| Strength | Charisma | Perception |
| Dexterity | Manipulation | Intelligence |
| Stamina | Appearance | Wits |

**Распределение при создании**: категории приоритизируются как **7 / 5 / 3**
дополнительных точек (поверх стартовой 1 в каждом).

## 3. Способности (Abilities) — 0–5 точек

Три группы по 10 способностей.

- **Talents**: Alertness, Athletics, Awareness, Brawl, Empathy, Expression,
  Intimidation, Leadership, Streetwise, Subterfuge
- **Skills**: Animal Ken, Crafts, Drive, Etiquette, Firearms, Larceny, Melee,
  Performance, Stealth, Survival
- **Knowledges**: Academics, Computer, Finance, Investigation, Law, Medicine,
  Occult, Politics, Science, Technology

**Распределение при создании**: группы приоритизируются как **13 / 9 / 5**.
Способность выше 3 точек при создании — обычно требует freebie-очков.
Некоторые способности требуют **специализации** на 4+ (свободный текст).

## 4. Преимущества (Advantages)

### 4.1 Дисциплины (Disciplines) — силы вампира, 1–5 точек

При создании — **3 точки** дисциплин (обычно из клановых). Примеры дисциплин:
Animalism, Auspex, Celerity, Chimerstry, Dementation, Dominate, Fortitude,
Necromancy, Obeah, Obfuscate, Obtenebration, Potence, Presence, Protean,
Quietus, Serpentis, Thaumaturgy, Vicissitude и др.

Каждая дисциплина имеет **силы по уровням** (power per dot). Для MVP достаточно
хранить рейтинг дисциплины; справочник `DisciplinePower` (описания уровней) —
желательная, но не обязательная для MVP деталь.

> Thaumaturgy/Necromancy имеют «пути» и «ритуалы» — это усложнение, помечаем как
> расширение после MVP.

### 4.2 Бэкграунды (Backgrounds) — 1–5 точек, 5 точек при создании

Allies, Alternate Identity, Contacts, Domain, Fame, Generation, Herd, Influence,
Mentor, Resources, Retainers, Status и др.

> **Generation как бэкграунд** может понижать поколение (повышать «крутость»).
> Связь Generation ↔ Blood Pool см. §5.3.

### 4.3 Добродетели (Virtues) — 1–5 точек, 7 точек при создании

- **Conscience** *или* **Conviction** (для путей просветления)
- **Self-Control** *или* **Instinct**
- **Courage**

Стартовое значение каждой — 1, распределяется 7 доп. точек.

## 5. Производные трейты (вычисляемые)

### 5.1 Humanity / Path

- По умолчанию **Humanity = Conscience + Self-Control** (шкала 1–10).
- Персонаж может следовать **Path of Enlightenment** (тогда Conviction + Instinct,
  и свой рейтинг). Для MVP — поддержать Humanity, путь как опцию.

### 5.2 Willpower — шкала 1–10

- Стартовое **Willpower = рейтинг Courage**.
- Имеет «постоянное» значение и «текущий» пул (временные точки).

### 5.3 Blood Pool (пул крови) — зависит от Generation

Максимум пула и трата за ход определяются поколением:

| Поколение | Max Blood Pool | Кровь/ход |
|-----------|----------------|-----------|
| 13th | 10 | 1 |
| 12th | 11 | 1 |
| 11th | 12 | 1 |
| 10th | 13 | 1 |
| 9th | 14 | 2 |
| 8th | 15 | 3 |
| 7th | 20 | 4 |
| ... | ... | ... |

> Таблицу полностью оформить в фикстуре `generation` справочника `rules`.

### 5.4 Health levels (уровни здоровья) — фиксированная шкала со штрафами

Bruised (0), Hurt (−1), Injured (−1), Wounded (−2), Mauled (−2), Crippled (−5),
Incapacitated. Для чарника — состояние каждого уровня (ok/bashing/lethal/aggravated).

## 6. Merits & Flaws (мериты и флоу) — опционально, покупка за очки

Покупаются за freebie-очки (Merit стоит очки, Flaw даёт очки, суммарно Flaws
обычно ≤ 7). Имеют категорию (Physical/Mental/Social/Supernatural) и стоимость.

## 7. Создание персонажа: очки и порядок

1. Концепция (clan, nature, demeanor, concept).
2. Атрибуты: **7/5/3**.
3. Способности: **13/9/5**.
4. Преимущества: Disciplines **3**, Backgrounds **5**, Virtues **7**.
5. Humanity (= Conscience+Self-Control), Willpower (= Courage).
6. **Freebie points: 15** — тонкая настройка. Стоимости:

   | Трейт | Стоимость за точку (freebie) |
   |-------|------------------------------|
   | Attribute | 5 |
   | Ability | 2 |
   | Discipline | 7 |
   | Background | 1 |
   | Virtue | 2 |
   | Humanity | 1 |
   | Willpower | 1 |

7. Merits/Flaws — в рамках freebie/баланса.

**Развитие** идёт за **Experience (XP)** по отдельным таблицам стоимости
(умножители new rating и т.п.) — нужно для трекинга прогресса, не для MVP-создания.

> Валидатор создания (проверка, что игрок не превысил лимиты) — отдельная фича.
> Для MVP допустимо хранить чарник без жёсткой валидации, но правила (числа выше)
> должны жить в `rules` как данные, а не в коде.

## 8. Кланы (V20) — справочник

13 «основных» кланов + независимые + кровные линии. У каждого клана: клановые
дисциплины (обычно 3) и слабость (weakness).

- **Camarilla**: Brujah, Malkavian, Nosferatu, Toreador, Tremere, Ventrue
- **Sabbat**: Lasombra, Tzimisce (+ antitribu-вариации многих кланов)
- **Independent**: Assamite, Followers of Set, Gangrel, Giovanni, Ravnos
- **Bloodlines** (расширение): Baali, Daughters of Cacophony, Gargoyles, Salubri,
  Samedi, Cappadocians и др.

> Слабости и описания кланов — переписывать своими словами (см. ниже). Состав
> клановых дисциплин — механический факт, хранится в `Clan.disciplines`.

## 9. Описательная часть (вход для квенты)

Поля, которые ИИ использует как контекст и которые отражают «лицо» персонажа:
apparent age / true age, date of birth, date of embrace (RIP), hair, eyes,
height, weight, sex, nationality, appearance description, haven, possessions,
coterie, **history / background** (это и есть квента), goals, derangements.

## Контекст города/хроники

Для квенты важен **сеттинг города** (например, классические «Камарилья в …»).
Моделируется в `quenta.CitySetting`: название, краткое описание политической
обстановки, доминирующие секты/кланы, заметные локации, тон. Используется как
контекст RAG. См. [05-ai-quenta-spec.md](05-ai-quenta-spec.md).

## Источник истины по числам

Все числовые правила (приоритеты 7/5/3 и 13/9/5, freebie-стоимости, таблица
поколений, шкала здоровья) **должны жить как данные** (`rules` / фикстуры),
а не быть зашиты в код, чтобы поддержать редактирование и другие линейки.

## Юридические ограничения

- Названия трейтов, кланов, дисциплин, числовые рейтинги и таблицы создания —
  **механические факты**, их хранение допустимо.
- **Описания** кланов, дисциплин, слабостей, архетипов из книг — **не копировать
  дословно**. Хранить либо короткое оригинальное summary, либо ссылку. Парсер из
  [SPEC-004](specs/SPEC-004-rules-data-pipeline.md) обязан помечать источник и не
  тащить большие текстовые блоки как есть.
- Добавить дисклеймер **Dark Pack** в футер/README перед публикацией.

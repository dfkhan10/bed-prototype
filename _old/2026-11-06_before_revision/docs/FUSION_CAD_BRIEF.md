# Fusion / CAD assistant — bed frame v1

Copy the **Prompt block** into Fusion Design Assistant (or give it to Cursor with MCP) after opening a **Design (Solid)** document.

**Source of dimensions:** `design/params.scad`, `docs/HARDWARE_DIMENSIONS.md`  
**Builder script:** `design/fusion/build_bed_frame_environment.py` (run via Scripts and Add-Ins — **not** preview in cloud)

---

## Why “Просмотр недоступен” for the `.py` file

The cloud project stores a **Python script**, not a `.f3d` model. Fusion Web **cannot preview** scripts.

1. Fusion **desktop** → **Design (Solid)** → New Design  
2. **Utilities → Scripts and Add-Ins → Run** `build_bed_frame_environment.py`  
3. **File → Save** → project **bed frame** → `BedPrototype_Frame_v1.f3d`  
4. Open the **`.f3d`** in Web for preview

---

## 1. Зачем зазоры между квадратами (ячейками)

| Что видите | Размер | Зачем |
|---|---|---|
| Расстояние центр–центр | **76 mm** (`cell_pitch`) | Влезает 3×3 на плату **~226 mm** (лимит P2S 256 mm) |
| Окно под кассету | **58 mm** (`well_open`) | Домик TPU + люфт |
| Фланец кассеты | **64 mm** (`flange_seat`) | Сидит на верхней кромке |
| «Просвет» между окнами | **~9 mm** с каждой стороны | Несущие **рёбра 3 mm** (`wall_t`) + место под **канал трубки 10×8 mm** |

**Можно ли без зазоров:** да, если уменьшить `cell_pitch` до **~61 mm** (58 + 3 mm стенка) — deck станет уже (~181 mm), но **каналы трубок** придётся вести в боковых ребрах или снаружи. Для v1 зазор **не декоративный** — это стенки + маршрутизация.

---

## 2. Убрать «ступеньку» (один уровень с платформой электроники)

**Проблема:** в упрощённой Fusion-сборке cell deck и electronics bay были на разных **Z**; в OpenSCAD service-модуль **68 mm**, cell deck **36 mm** → разный верх у стыка.

**Цель:** одна **верхняя load-плоскость** по всей кровати:

- Верх кассет / деки: **Z = deck_top_t + cavity_h = 36 mm** от низа cell deck  
- Электронный отсек **не поднимает** верх service-зоны — он уходит **вниз** под service bay (как в `print_master.scad`: tray + rim + bottom)

Fusion-скрипт v2 выравнивает **верх** cell deck и service cap на **36 mm**.

---

## 3. Трубки — одна на камеру, снизу по центру

| Параметр | Значение |
|---|---|
| Трубка | **4 mm ID / 6 mm OD** (kit) |
| Порт | **Ø6.5 mm** в **центре дна** лунки (сверху не виден) |
| Под полом | **stem pocket** Ø10 + канал **10×8 mm** к **−Y** (service) |

Схема: **`docs/TUBE_ROUTING.md`**. Клапаны в service bay; foot — 3 pass-through в OpenSCAD.

---

## Prompt block (Fusion / CAD assistant)

```text
Project: Bed prototype — closed deck, 3×3 air cells, electronics under service bay.

Use dimensions from params.scad (do not invent new numbers):
- cell_pitch 76, well_open 58, deck_top_t 4, cavity_h 32
- e_bay_x 200, e_bay_y 128, e_bay_cavity_h 52
- tube_od 6, port_d 6.5, channel_w 10, channel_depth 8

Tasks:
1) Cell grid: 3×3 wells; keep 3 mm ribs OR document if pitch is reduced.
2) Coplanar top: cell deck and service deck share top Z = 36 mm (4 mm skin + 32 mm cavity).
3) Electronics bay under service only; 8× pump pocket 68×31 mm; 8× M3 boss; Arduino standoffs.
4) Pneumatic: each cell one Ø6.5 port at bottom-center of well floor; stem pocket + under-deck groove to −Y foot; service bulkhead + valve zone.
5) Mechanical: 2× Ø5 dowel + 2× M3 lap at cell↔service joint (−Y foot).

Run local script: design/fusion/build_bed_frame_environment.py
Save to hub project "bed frame" as BedPrototype_Frame_v1.f3d
Print source of truth remains OpenSCAD print_master.scad.
```

---

## Открытые вопросы (нужны ответы для точной v2)

1. **Шаг сетки:** оставляем **76 mm** (каналы внутри) или ужимаем до **~61 mm** (минимальный зазор)?  
2. **Сolenoid layout:** 9 клапанов в ряд на service deck — есть ли фото/замер **реального** шага на вашей плате?  
3. **Трубка:** подтвердите штангеном **OD = 6 mm** (или другое) — подстроим `port_d` и клипсы.  
4. **Ступенька:** приоритет — **одна плоская верхняя поверхность** под матрас/TPU по всей 3×3 + service, или допустим выступ service на **32 mm** если электроника остаётся монолитом?

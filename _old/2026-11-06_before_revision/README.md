# Bed prototype — handoff для Codex / агентов

Исследовательская **пневматическая дека**: **12 ячеек (3×4)**, трубки скрыты, **надувание вверх**. Печать: **Bambu P2S** (256 mm).

**CAD:** только **Fusion 360** + **`design/bed_params.json`**. OpenSCAD — legacy.

**Debug backlog:** [docs/DESIGN_DEBUG.md](docs/DESIGN_DEBUG.md) — кривой layout v0.9, что чинить первым.

---

## Быстрый старт

| Шаг | Действие |
|-----|----------|
| 1 | `design/bed_params.json` |
| 2 | Fusion → Run `design/fusion/build_bed_frame_environment.py` |
| 3 | `save_and_export.py` → `export/stl/` |
| 4 | Save `BedPrototype_Frame_v1.f3d` → hub **bed frame** |

[START_HERE.md](START_HERE.md) · Cursor MCP: *rebuild + export STL*

---

## Состояние модели (v1.0 script — после первого debug-pass)

| Body | Назначение |
|------|------------|
| `BedFrame_CellDeck` | 3×4, shallow seat 8 mm (6 + **floor 2 mm** + port) |
| `BedFrame_ServiceDeck` | Coplanar top, **12** valve pockets (4×3 layout) |
| `BedFrame_ElectronicsBay` | Pumps, **M2.5 screw bosses** (pilot holes) |
| `BedFrame_BottomPanel` | Отдельная крышка bay, **8× M2.5** |
| ~~Dowel pegs~~ | **Убраны** — только шурупы на стыке |

Deck **~194 × 254 mm** @ `cell_pitch: 60`.

---

## Крепёж: **мелкие шурупы**, не «болт + гайка»

Владелец: **небольшие шурупы** (саморезы в пластик / в **heat-set вставку**), без пар болт-гайка снаружи.

### Стандарт (в JSON → `fasteners`)

| Элемент | Решение |
|---------|---------|
| Размер | **M2.5 × 8–10 mm**, головка под **PH / hex** |
| В пластике | **Heat-set латунная вставка M2.5** (рекомендуется в boss) **или** резьбаформирующий шуруп в **pilot 2.1 mm** |
| Стык cell ↔ service | **4× сквозных** `clearance_d 2.7` на одной **`mate_y`**, **общие X** (`joint_screw_count`) |
| Bottom panel ↔ bay | **8×** в bosses на периметре панели → встречаются с bosses в bay |
| Arduino | M2.5 standoffs (как в kit) |
| Кассеты | без шурупов через камеру |

**Не использовать:** M3 lap, печатные dowel pegs, гайки снаружи (только prototype exception).

```json
"fasteners": {
  "primary": "M2.5",
  "screw_length_mm": 10,
  "clearance_d": 2.7,
  "pilot_d": 2.1,
  "boss_od": 5.5,
  "boss_h": 6,
  "joint_screw_count": 4
}
```

### Checklist стыков (Codex)

- [x] **D2** aligned joint screws (script v1.0)
- [x] **E1** `BedFrame_BottomPanel` body
- [ ] **E2** service ↔ bay rim flange + screws
- [ ] **E7** tube bulkhead at `mate_y`
- [ ] **Fillets** / visual cleanup
- [ ] BOM в [BED_FRAME_CONNECTORS.md](docs/BED_FRAME_CONNECTORS.md)

---

## DFM / DFA (продуманный дизайн)

См. [DESIGN_DEBUG.md](docs/DESIGN_DEBUG.md) + ниже.

### Обязательно

- [ ] **Fillets/chamfers** — `corner_r`, внешний контур деки и bay
- [ ] **Valve layout** — сверить 12× с реальным Taobao kit ([HARDWARE_DIMENSIONS.md](docs/HARDWARE_DIMENSIONS.md))
- [ ] **Tube routing** — cell run → `mate_y` → valve stub (исправить логику Y)
- [ ] **Split** при `cell_pitch: 76` → 2 plates + **M2.5 seam**
- [ ] **Assembly** — [ASSEMBLY.md](docs/ASSEMBLY.md) под Fusion STL и шурупы
- [ ] Export **только** `BedFrame_*` (без `BodyNN`)

### Пневматика (не менять)

Bottom-center port, 1 tube/cell → [TUBE_ROUTING.md](docs/TUBE_ROUTING.md).

---

## Codex: порядок работ

1. README + **DESIGN_DEBUG.md** + `bed_params.json`
2. Rebuild Fusion → разрез на **`mate_y`** (4 отверстия сквозные)
3. Закрыть пункты P0/P1 в DESIGN_DEBUG
4. DFM (fillets, valve view, bulkhead)
5. Export STL, проверка **≤252 mm**
6. Save `.f3d`

**DoD:** нет dowel/M3 legacy; все стыки = **M2.5 screws** + BOM; debug doc пуст по P0.

---

## Репозиторий

```text
design/bed_params.json
design/fusion/build_bed_frame_environment.py
design/fusion/save_and_export.py
export/stl/
docs/DESIGN_DEBUG.md      ← debugging «кривого» дизайна
docs/BED_FRAME_CONNECTORS.md
docs/TUBE_ROUTING.md
docs/ASSEMBLY.md
design/legacy/            ← OpenSCAD, не синхронизировать
```

---

## Ivan

Fusion cloud: **bed frame** · Kit: 370 pumps, 12 valves, 4 mm tube, Uno.

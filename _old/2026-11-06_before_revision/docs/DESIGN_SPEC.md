# Pneumatic bed base — mechanical design spec (prototype v1)

Target printer: **Bambu Lab P2S** — build volume **256 × 256 × 256 mm**.  
Goal: a **closed, serviceable technical deck** with a **3 × 3 TPU cell grid**, **one solenoid valve per cell**, **shared pump(s)**, **Arduino on the bottom access panel**, and **protected tube routing** under the load deck.

This is a **research prototype** layout document, not a clinical device spec.

---

## 1. Design intent (matches your sketch)

| Layer (top → bottom) | Function |
|---|---|
| TPU bladders + printed cassettes | Adaptive support cells, removable |
| Load deck | Smooth top, cell wells, port holes, ribs between cells |
| Routing cavity (~25–35 mm tall) | Tube channels, valve clips, wire looms |
| Bottom service panel (screwed on) | Mounts Arduino; pumps/valves can mount to panel or cavity rails |

**Visible from outside:** only the cell grid (and optional top cover later).  
**Hidden:** tubes, valves, pumps, wiring — inside the cavity, accessed by removing the bottom panel.

---

## 2. System layout

```text
Plan view (example v1 — service bay at foot):

    ┌───┬───┬───┐
    │ 1 │ 2 │ 3 │   ← cell deck (one or two printed sections)
    ├───┼───┼───┤
    │ 4 │ 5 │ 6 │
    ├───┼───┼───┤
    │ 7 │ 8 │ 9 │
    └───┴───┴───┘
    ┌─────────────┐
    │ SERVICE BAY │   ← no cells; pumps, valve bank, manifold
    └─────────────┘

Section view:

    [ Person / test load ]
    ─── optional future cover ───
    ═══ cassettes + TPU cells ═══
    ─── load deck (PLA/PETG) ───
    ··· tubes + valves ···
    ═══ bottom panel + Arduino ═══
```

**Why split prints:** a full single plate larger than **250 mm** on any edge exceeds practical P2S margin (256 mm max). v1 uses a **cell plate** (~240 mm square) plus a **service module** (~240 × 90 mm) joined with **dowel pins + M3 screws**.

---

## 3. Pneumatic architecture (1 valve / cell)

You specified **one valve per cell**. With typical **2/2 solenoid valves** (open/closed):

| Command | Valve | Pump |
|---|---|---|
| Inflate | Open (cell connected to supply) | On |
| Hold | Closed | Off |
| Deflate | Open (cell connected to exhaust branch) *or* separate bleed fitting | Off |

**Prototype v1 plumbing (recommended):**

```text
Pump → T-connector → supply manifold (to each valve IN)
Each valve OUT → cell tube (label A1…A9)
Each valve NC port → common exhaust manifold (open to atmosphere, muffled)

Hold = valve closed (leak rate of cell + valve determines drift — acceptable for v1)
```

**Not in v1:** printed internal air channels (use **commercial 4 mm pneumatic hose** + barbed or push-fit adapters).  
**Isolation:** do **not** tee all cells to one open tube; each cell branch needs its **own valve** before joining manifolds.

Kit reference (your photos): Arduino Uno + sensor shield, **2× DC micro pumps**, **1× valve** in the demo — scale to **9 valves** for 9 cells (or start **Stage 1: 1 cell** on a small single-tile print).

---

## 4. Component envelopes (for cavity height)

Reserve these in the routing cavity and service bay (measure your exact parts when they arrive):

| Part | Approx envelope (L × W × H mm) | Notes |
|---|---|---|
| Arduino Uno | 69 × 53 × 15 | On bottom panel standoffs |
| Sensor shield | +15 mm height | Keep USB/power edge reachable |
| Micro DC air pump (typ.) | 27 × 20 × 30 | 2× in service bay; rubber grommet mounts |
| 2/2 solenoid valve (typ.) | 28 × 15 × 40 | Bank along service bay |
| 4 mm pneumatic tube | 6 mm OD | Min bend radius ≥ 15 mm in channels |
| 12 V adapter | External preferred | Strain relief through panel slot |

**Minimum routing cavity height (`cavity_h` in OpenSCAD):** **32 mm** (comfortable); **28 mm** (tight).

---

## 5. Cell cassette interface

Each cell module (printed **PETG/ABS**, bladder **TPU welded**):

- **Flange clamp** on flat perimeter (no screws through pressurized chamber).
- **Locating recess** in deck well (anti-skew).
- **Single barb port** under deck (push-fit 4 mm tube).
- **ID label** on cassette rim (1…9).

Default well (parametric in `design/params.scad`):

- Pitch: **76 mm** (3 × 76 = 228 mm grid + walls fits P2S)
- Well opening: **58 mm** rounded square
- Flange seat: **64 mm** outer

---

## 6. Print strategy (P2S)

| Part | Material | Process notes |
|---|---|---|
| Load deck + ribs | PETG or ABS | 3–4 perimeters, 25–35% gyroid; **≥ 0.6 mm** top skin over cavity |
| Cell cassettes | PETG | Smooth top surface (ironing optional) |
| Tube clips / valve clips | PETG | Print flat |
| Bottom service panel | PETG/ABS | **M3 heat-set inserts** for Arduino standoffs and panel screws |
| Dowel pins | PLA | 5 mm × 12 mm pegs |

**Orientation:** deck sections print **cavity opening upward** (top surface on build plate) *or* upside-down with heavy supports — default in SCAD is **cavity up** for clean top surface.

**Tolerance:** design **0.25 mm** clearance on cassette slip fit; test one well before printing all nine.

---

## 7. Safety (before human load)

- Backup support when cells deflated (compliant pad or minimum deck web thickness).
- No screw heads / sharp edges in contact path.
- Overpressure: fuse timing on pump + max inflate duration in firmware.
- Power-loss: valves spring-closed (verify your valve default state).
- Label every tube end **at both ends**.

---

## 8. Repository layout

```text
design/
  params.scad          # edit dimensions here
  lib/util.scad
  parts/
    cell_cassette.scad
    deck_cell_section.scad
    deck_service_section.scad
    bottom_panel.scad
    tube_clip.scad
  assemblies/
    prototype_v1.scad  # layout preview + export list
docs/
  DESIGN_SPEC.md       # this file
  ASSEMBLY.md
  PRINT_CHECKLIST.md
```

Open `design/assemblies/prototype_v1.scad` in OpenSCAD → F6 → export STLs per part module comments.

---

## 9. Open decisions (confirm when hardware arrives)

1. **Valve default state** (NC vs NO) → defines safe power-off behavior.  
2. **One pump vs two** (pressure vs vacuum on separate pumps) for faster deflate.  
3. **Final bed footprint** (single region vs full mattress) → scales tile count, not cassette logic.  
4. **Barb size** (4 mm ID tube → 4.5–5 mm barb typical).

When you have calipers on the Taobao kit, update `design/params.scad` pump/valve pockets and re-export.

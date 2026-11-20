# Tube routing — bottom-center per cell

## User-facing rule

- **Top:** only the cell well / cassette — **no holes, no tubes visible**.
- **Bottom-center of each well:** one **Ø6.5 mm** port (`port_d`) for **4 mm ID / 6 mm OD** hose + barb.
- **Below the 4 mm well floor:** printed **infrastructure** (stem pocket + groove) guides the hose to the **service bay** (−Y foot) where **9 solenoids** live.

## Section (one cell)

```text
        [ TPU + cassette ]     ← visible from above
        ═══ well (58 mm) ═══
        ─── deck floor 4 mm ───  ← port in CENTER of floor (hidden from top)
        · stem pocket Ø10 ·      ← barb + bend radius
        ══ groove 10×8 mm ══     ← under ribs, toward service
        ······ toward foot ······
        [ valve / clip / bay ]
```

## Printed parts

| Feature | Module | Notes |
|---|---|---|
| Through-floor port | `cell_bottom_port()` | Center (0,0) in cell coords |
| Stem pocket | `cell_stem_pocket()` | `stem_pocket_d` × `stem_pocket_h` |
| Run to service | `cell_run_to_service()` | Length from `cell_run_len()` |
| Clip slots | `clip_slots()` | Along each run |
| Service bulkhead | `clip_slots()` | 3 columns at foot (one per grid column) |

Source: `design/lib/util.scad`, used in `deck_cell_section.scad`.

## Assembly

1. Insert **barb** or push-fit from **below** into deck port (cassette sits on top; align cassette bottom port to same axis).
2. Route hose in **groove**; snap **tube_clip** in slots.
3. At foot, hoses pass into **service bay** → one valve per cell → pump/manifold.

Fusion: run `build_bed_frame_environment.py` — all routing + **9 valve pockets** + service stub channels. Params: `bed_params.json`.

**Joint bulkhead** (3 columns at cell↔service foot): finish in Fusion with a sketch on the mating face if needed — automated cut is pending (foot geometry).

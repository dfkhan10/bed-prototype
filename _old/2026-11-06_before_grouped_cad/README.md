# Bed prototype

> **Current brief:** [model requirements](work/2026-11-06_model_requirements.md) and [paste-ready text-chat handoff](work/2026-11-06_text_chat_handoff.md). The two-bus circuit is approved. The next model must add supported welded-TPU cells, close-spaced moving caps flush with the cover at the raised stop, a full-length common bottom plane, and screw-connected sections. Cosmetic finishing may hide seams; adhesive alone is not the structural connection. The CAD files below remain the preceding geometry baseline.

Saved Fusion baseline: **12 cells, A–C across and 1–4 down**. It reserves 12 valve envelopes; the approved next circuit requires separate fill/extraction paths for each cell. Pump count is **pending**, not tied to cell count.

All authored dimensions: [`design/bed_params.json`](design/bed_params.json). OpenSCAD files are historical and are not synchronized.

## Current review, 6 November 2026

- [Assembled Fusion archive](export/2026-11-06_BedPrototype_assembled.f3d)
- [Exploded Fusion archive](export/2026-11-06_BedPrototype_exploded.f3d)
- [Interactive inspection](export/2026-11-06_design_review.html), self-contained and usable offline
- [Assembled STEP](export/2026-11-06_BedPrototype_assembled.step) / [exploded STEP](export/2026-11-06_BedPrototype_exploded.step)
- [Assembled image](export/2026-11-06_assembled.png), [exploded image](export/2026-11-06_exploded.png), [underside](export/2026-11-06_underside.png)
- [Actual exported geometry and hole axes](export/2026-11-06_export_manifest.json)

The F3D files contain linked `Assembly_Assembled` and `Inspection_Exploded` occurrences. Their visibility selects the inspection state. **Export STL only from `Assembly_Assembled/BedFrame_*`.** Reference valves and screws are not print parts. The model contains no pump geometry while its construction is unknown.

## Mechanical revision

| Part | Current size, mm | Details |
|---|---|---|
| Cell deck | 192 × 252 × 36 | 3×4 seats; open ribbed underside; hidden hose passages |
| Service cover | 208 × 136 × 36 | Closed top; underside valve guides, 4×3; rim receivers |
| Bay frame | 208 × 136 × 52 | Open both ends; upper screw flange; lower bosses |
| Bottom panel | 208 × 136 × 4 | Full removable panel; 8 holes; ventilation slots |

**60 mm pitch** means centre-to-centre spacing. Each seat is nominally **56 mm wide and 2 mm deep**, with a **separate 2 mm floor** and a centre Ø6.5 mm port. The 56 mm seat leaves a 4 mm web between adjacent cells; verify against the actual cassette before printing.

Four **Y-axis M2.5 × 10 screws** join the cell deck to the service cover at a 0.3 mm butt joint. They enter from the open cell underside, into service-side pilots. There is no overlapping full solid, vertical lap, dowel or exterior nut.

Eight screws inserted upward through the bay's upper flange enter the service cover's receiving bosses. Their heads can be reached through the open bay with its bottom panel removed. Eight more screws attach the bottom panel. One XY table defines both interfaces.

- M2.5 thread-forming screws, Ø2.7 clearance, Ø2.1 blind pilots, 8 mm receivers.
- Panel/rim grip 4 mm; nominal engagement 6 mm; blind depth 7 mm.
- Cell joint grip 3 mm + 0.3 mm gap; engagement 6.7 mm.
- Heat-set inserts need their actual outside diameter and length. **Do not install inserts into the current Ø2.1 pilots.**

## Rebuild and export

1. Edit `design/bed_params.json`.
2. Fusion Design → run `design/fusion/build_bed_frame_environment.py`. This creates a **new document**, preserving open work.
3. Run `design/fusion/save_and_export.py`. It writes local F3D, STEP, STL and a manifest; it does not cloud-save or publish.
4. Inspect [DESIGN_DEBUG](docs/DESIGN_DEBUG.md), then slice the relevant STL files. Old STL files are moved to `_old/` before export.

At pitch 76 the three-column deck becomes 224 × 300 mm and automatically splits into two 2-row modules with a screwed seam. The saved baseline parameters remain pitch 60; the new requirements do not freeze that pitch. A width above 252 mm is rejected; X-axis subdivision is not implemented.

## Pneumatic sizing still required

One shared supply may serve selectable cell groups through individual valves. The actual valve type, exhaust path and pressure/flow control must be established from the kit. A generic 2/2 shutoff valve does not by itself provide a separate exhaust path.

Pump count needs the cell's air demand, maximum simultaneous group, target inflation time, and **pump flow at the operating pressure**. Free-flow ratings alone do not establish this. `pneumatics.pump_count` remains `null`, and no fixed eight-pump tray is generated.

The service module is a provisional enclosure. It may need resizing once the pump, manifold, fittings and controller are laid out. Valve guides use estimated 22 × 12 × 30 mm envelopes; retention straps, actual port orientation, controller mounting and the power-entry cutout are pending hardware measurements.

## Verification boundary

Fusion feature health, frame solid interference, hole axes, STL integrity and print bounds are checked. Hardware fit, tube bend radii at real fittings, slicing/support removal, pressure control, leakage and load capacity are not yet accepted. This is a research prototype, not a load-qualified bed.

Assembly and print details: [ASSEMBLY](docs/ASSEMBLY.md), [connectors](docs/BED_FRAME_CONNECTORS.md), [routing](docs/TUBE_ROUTING.md), [print checklist](docs/PRINT_CHECKLIST.md). The original source files and Fusion archive are preserved in `_old/2026-11-06_before_revision/`.

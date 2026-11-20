# Design debug and acceptance status

Revision: **6 November 2026**. Current master: `design/fusion/build_bed_frame_environment.py`, parameters: `design/bed_params.json`.

## New functional requirements: next revision open

The owner has clarified heat-welded TPU film, simultaneous inflation/deflation, 20–30 mm travel, moving printed caps, a common bottom support plane, and compact visible spacing and top/base sections connected structurally with M2.5 screws, with optional seam finishing. See [current model requirements](../work/2026-11-06_model_requirements.md) and [architecture review](../work/2026-11-06_pneumatic_and_cell_mount_review.md).

The current CAD has not implemented the cell clamps/guides/caps or a common full-length lower support. Its 12-valve reservation is not sufficient evidence of a complete independent inflate/hold/deflate circuit. Pump count and the enlarged valve/housing package need the next design pass. The nominal geometry fixes below remain verified for the previous model.

## P0 / P1 geometry fixes

| ID | Original issue | Implemented and checked |
|---|---|---|
| G1 | Misaligned cell/service screws; overlapping solids | Four horizontal Y-axis holes from one X/Z table, service pilots, 0.3 mm butt gap. Actual Fusion cylinder axes checked coaxial; zero frame interference. |
| G2 | Detached printed dowels and BodyNN artifacts | No pegs generated. Each print component owns exactly one named solid; old STL artifacts archived. |
| G3 | Missing bulkhead | Three 34×12 mm windows through both mating walls; same tunnel profile through cross ribs. Visible in underside inspection. |
| G4 | 12 valves in overlapping 5-column layout | 4×3 bank; 12 separate nominal 22×12×30 envelopes and side guides. Nominal geometry fits; **actual kit fit remains open below**. |
| G5 | Stub channels run away from mating plane | Removed reversed-Y blind grooves. Cell bundles reach the mating wall; service routing continues through an open cavity. Real individual fitting/clip routes remain hardware-dependent. |
| F1 | Bay M3 bosses | M2.5 system throughout the master; service receivers, bay upper clearance flange, bay lower blind pilots. |
| F2 | Mixed lap/dowel hardware | 20 M2.5×10 screws in current assembly; no outside nuts or vertical overlapping lap. Screw-head access checked in inspection. |
| F3 | Bottom-panel name applied to a small stray body | Full 208×136×4 removable panel, eight coaxial holes; one connected solid. |

These entries close the original nominal-geometry defects. They do not establish hardware fit or manufacturing acceptance.

## DFM work implemented

- Outer corners R6, cell-seat corners R3, exterior top edges softened R0.6.
- Open cell underside with 4 mm load webs/ribs; 2 mm seats and independent 2 mm floors.
- Consistent 4 mm bay wall, open frame, accessible upper flange screws and complete bottom access panel.
- Shared eight-point XY pattern for service/bay/panel interfaces; lower bosses have connecting webs.
- Current STL bounds: cell 192×252×36; service 208×136×36; bay 208×136×52; panel 208×136×4 mm.
- **Pitch 76 built in Fusion:** two 224×149.85×36 cell modules, four-screw seam; remaining parts max 224 mm. Zero frame interference and healthy timeline. Validation archive: `export/validation/2026-11-06_pitch76_split.f3d`. The default JSON remains pitch 60.
- Separate assembled/exploded linked Fusion assemblies; local F3D, STEP, filtered STL and offline inspection viewer.

## Verified evidence

- `export/2026-11-06_export_manifest.json`: actual BRep dimensions, volume, cylinder axes; zero frame interference and timeline errors.
- `export/2026-11-06_mesh_validation.json`: four closed, connected, consistently wound STL solids; millimetre bounds; 4 cell-joint pairs, 8 rim pairs, 8 panel pairs, 12 through-floor ports.
- `export/2026-11-06_pitch76_geometry_report.json`: live Fusion build of the split configuration.
- Viewer checked in assembled, exploded and underside views; part visibility and separation controls exercised. PNGs are captures of that actual-mesh viewer. Native Fusion MCP viewport capture is unavailable in this workspace.

## Open before a manufacturing release

1. **Pump/manifold:** user confirmed selectable cell groups. Pump construction/pressure-flow data, cell air demand, target pressure and fill time are missing. Pump count is `null`; fixed eight-pump mounts removed. The provisional bay may need resizing.
2. **Actual valves:** port/exhaust arrangement, fittings, envelope, wiring, retention and drivers unmeasured. Guide rails and reference blocks are provisional; no final clip/strap or hose centre-line acceptance.
3. **Cell/cassette:** nominal seat narrowed to 56 mm to preserve 4 mm webs at 60 mm spacing. Check actual cassette/flange/barb, floor support and tolerance with a coupon.
4. **Fastener coupon:** Ø2.1 pilot suits the intended trial, not every M2.5 screw/material. Validate thread-forming screw retention. Heat-set OD/length must be supplied before adding insert pockets.
5. **Slicer / structural checks:** inspect bridging and supports; test 2 mm floor removal/finish, leakage, repeated service cycles and load. No Bambu Studio slice or structural/pressure validation has been performed.
6. **Controller/power:** actual mounts, connector cutouts, strain relief and power entry await the kit layout. Generic Arduino hole patterns were removed.

X-axis print subdivision is not implemented; oversize widths are rejected. Clip locations and real hose lengths should follow the measured kit. See [PRINT_CHECKLIST](PRINT_CHECKLIST.md), [ASSEMBLY](ASSEMBLY.md), and [HARDWARE_DIMENSIONS](HARDWARE_DIMENSIONS.md).

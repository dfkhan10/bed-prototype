# Grouped CAD verification

6 November 2026. Current parameter schema: `bed.grouped.v1`. [Native geometry manifest](../export/2026-11-06_grouped/2026-11-06_manifest.json) matches the current JSON dimensions. [Mesh report](../export/2026-11-06_grouped/2026-11-06_mesh_checks.json) records the actual exported geometry checks.

| CAD check | Reported issues |
|---|---:|
| interferences | 0 |
| motion interferences | 0 |
| tube interferences | 0 |
| rigid reference interferences | 0 |
| driver access interferences | 0 |
| tube network interferences | 0 |
| tube hardware interferences | 0 |
| feature issues | 0 |

All 18 layout preconditions pass. Checks cover fixed printed parts, raised caps, cap travel sampled every 1 mm through the 25 mm stroke, hose OD envelopes, separate pneumatic networks, bought rigid keep-outs and Ø4 mm driver shafts. Solid intersections smaller than 0.01 mm³ are outside the report threshold. This is a nominal geometry check, not a tolerance-stack or structural calculation.

All 49 printable mesh types (88 full-assembly pieces) are watertight, consistently wound, connected single solids and within 0.1 mm of the native CAD bounding boxes. Largest dimension: 171.875 mm, within the 252 mm allowance. The complete printed assembly measures 344 × 432 × 73 mm. The four one-cell coupon meshes are checked separately. The final PCB tray correction adds four through holes and four head-clearance pockets; its explicit head/driver checks report zero conflicts.

The model contains eight pump envelopes, four group valves, stacked board trays, supported cell ports, hose bends, group crosses, tube clips and section screws. Expected hose/barb insertion overlap and connections within one pneumatic network are intentional. Actual ports, board connectors and hose compliance remain provisional.

Physical acceptance is open: kit measurements, valve function/vacuum compatibility, installed pump flow and required pump count, electrical ratings, TPU weld/port leakage, clamp compression, guide friction, screw strip-out, slicing/support removal and load capacity. Begin with the [one-cell coupon](../export/2026-11-06_grouped/coupon/stl/) and [assembly sequence](ASSEMBLY.md). Eight is packaging capacity, not the proven operating count.

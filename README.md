# Bed prototype

Current CAD: 4 columns × 3 rows, two checkerboard groups of six, and two cells per row branch within each group. Overall enclosure: 344 × 432 × 73 mm. The cell supports are raised 25 mm from the preceding geometry. The soft surface has a nominal lowered datum of 73 mm and a nominal rise of 25 mm. Optional guided caps use lower/upper stops at 73/98 mm.

The 172 mm service bay holds four pressure and four extraction pump positions, four group valves, two slotted electronics trays with open cable access, and separate power and USB-C openings. The space under the cells includes reserve paths for future services. Both service covers are removable from above with recessed M2.5×8 screws. The bottom panels have internal clearance pockets for the lower splice screw heads. Purchased hardware envelopes and TPU shapes are nominal.

## Open the design

- [Editable Fusion master](export/2026-11-08_grouped/2026-11-08_GroupedBed.f3d)
- [Assembled STEP](export/2026-11-08_grouped/2026-11-08_GroupedBed_assembled.step)
- [Interactive review](export/2026-11-08_grouped/2026-11-08_design_review.html), including the open service bay, tubing and reserve corridors
- [Print package](export/2026-11-08_grouped/2026-11-08_print_package.zip), [print BOM](export/2026-11-08_grouped/2026-11-08_print_BOM.csv) and [one-cell STL set](export/2026-11-08_grouped/coupon/stl/)
- [Native check manifest](export/2026-11-08_grouped/2026-11-08_manifest.json) and [mesh checks](export/2026-11-08_grouped/2026-11-08_mesh_checks.json)

## Rebuild

1. Change the [dimension source](design/bed_params.json).
2. In Fusion Scripts, run [BedGroupedPrototype](design/fusion/BedGroupedPrototype/BedGroupedPrototype.py) to export editable solids, STEP and native meshes.
3. Run `.venv/bin/python design/review/2026-11-08_grouped_exports.py` for print orientation, mesh validation, the print package and the offline viewer.

[Assembly](docs/ASSEMBLY.md) · [Screw interfaces](docs/BED_FRAME_CONNECTORS.md) · [Tube routing](docs/TUBE_ROUTING.md) · [Hardware dimensions](docs/HARDWARE_DIMENSIONS.md)

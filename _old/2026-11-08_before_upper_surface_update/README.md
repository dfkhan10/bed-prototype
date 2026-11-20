# Bed prototype

Current CAD: **4 columns × 3 rows**, two fixed checkerboard groups of six. Overall **344 × 432 × 73 mm**, cap travel **25 mm**, cap spacing **2 mm**. The 172 mm service bay reserves eight pump bodies with hose/fitting space, four group valves and stacked controller/driver trays. Eight is capacity, not an established required pump count.

## Open the design

- [Fusion master, editable solids and linked inspection states](export/2026-11-06_grouped/2026-11-06_GroupedBed.f3d)
- [Assembled STEP](export/2026-11-06_grouped/2026-11-06_GroupedBed_assembled.step)
- [Interactive inspection, offline](export/2026-11-06_grouped/2026-11-06_design_review.html)
- [Dimensioned layout](export/2026-11-06_grouped/2026-11-06_dimensions.svg)
- [Validated print package](export/2026-11-06_grouped/2026-11-06_print_package.zip)
- [Print-oriented STL parts](export/2026-11-06_grouped/stl/), [quantity list](export/2026-11-06_grouped/2026-11-06_print_BOM.csv)
- [One-cell fitting coupon](export/2026-11-06_grouped/coupon/stl/), [coupon STEP](export/2026-11-06_grouped/coupon/2026-11-06_OneCellCoupon.step)
- [Actual geometry/check manifest](export/2026-11-06_grouped/2026-11-06_manifest.json), [mesh checks](export/2026-11-06_grouped/2026-11-06_mesh_checks.json)

The Fusion document contains `Assembly_Raised`, linked exploded and alternating states, a cell section and a one-cell coupon. Toggle root occurrences to inspect them. Native geometry uses editable BRep solids in BaseFeatures; dimensions are regenerated from [bed_params.json](design/bed_params.json), rather than a fully constrained sketch history. `Ref_*` bodies represent bought hardware, tubing or TPU and are not print parts.

## Rebuild

1. Edit [the dimension source](design/bed_params.json).
2. In Fusion Scripts, add/run [BedGroupedPrototype](design/fusion/BedGroupedPrototype/BedGroupedPrototype.py). It creates a new document and exports local F3D, STEP, CAD-space meshes and images. No cloud publication.
3. From this project run `.venv/bin/python design/review/2026-11-06_grouped_exports.py`. The postprocessor also regenerates dimensioned drawings and the print ZIP. It validates actual meshes, writes print-oriented STL, BOMs, TPU coupon patterns and the offline viewer.
4. Check [DESIGN_DEBUG](docs/DESIGN_DEBUG.md) and [PRINT_CHECKLIST](docs/PRINT_CHECKLIST.md). Print and test the one-cell coupon before committing to the complete assembly.

[Assembly](docs/ASSEMBLY.md), [screws](docs/BED_FRAME_CONNECTORS.md), [tube routing](docs/TUBE_ROUTING.md), [hardware assumptions](docs/HARDWARE_DIMENSIONS.md). Previous CAD sources and operating documents are preserved under `_old/2026-11-06_before_grouped_cad/`; old root-level exports describe the preceding geometry.

This is a CAD prototype. Actual kit fit, valve function, installed pressure/vacuum flow, TPU welding, slicing, leakage and load capacity remain physical acceptance work. The model does not establish a patient-support rating.

# Grouped prototype print checklist

Use only the current [stl](../export/2026-11-06_grouped/stl/) folder and [print BOM](../export/2026-11-06_grouped/2026-11-06_print_BOM.csv). `meshes/` contains raw CAD-space geometry for inspection, including non-print hardware. Do not print `Ref_*`, TPU envelopes, tubes or the full STEP assembly as one object.

The postprocessor checks each print type for one connected watertight mesh, consistent winding, agreement with its CAD bounding box and the 252 mm machine envelope. See [mesh_checks.json](../export/2026-11-06_grouped/2026-11-06_mesh_checks.json) for current results.

Print the [four-piece one-cell coupon](../export/2026-11-06_grouped/coupon/stl/) first. Check guide friction through the complete stroke, both travel stops, screw pilot fit/strip-out, the supported bought port and TPU clamp/weld fit. Use the separate reinforcement ring with the gusset pattern; the two-sheet pillow naturally has two dry plies.

STL orientations put cups, caps and covers flat-face down; other parts retain a normalized CAD orientation. Inspect actual supports, bridges, boss recesses and overhangs in the slicer. Layer height, material, walls, infill and print settings are not selected or sliced yet. A bounding-box pass alone is not a printability acceptance.

Actual pump/valve/board connectors and hose bends, electrical ratings, sealing, pressure control and load capacity remain unverified. Do unloaded trials before any load test. Full assembly printing follows the successful coupon and hardware fit check.

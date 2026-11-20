# Grouped prototype print checklist

Use only the current [stl](../export/2026-11-08_grouped/stl/) folder and [print BOM](../export/2026-11-08_grouped/2026-11-08_print_BOM.csv). `meshes/` contains raw CAD-space geometry for inspection, including non-print hardware. Do not print `Ref_*`, TPU envelopes, tubes or the full STEP assembly as one object.

The postprocessor checks each print type for one connected watertight mesh, consistent winding, agreement with its CAD bounding box and the 252 mm machine envelope. See [mesh_checks.json](../export/2026-11-08_grouped/2026-11-08_mesh_checks.json) for current results.

Print the stand, cup and clamp ring from the [one-cell coupon](../export/2026-11-08_grouped/coupon/stl/) first. Check the screw fit, supported port, TPU clamp and weld, and deflated cover height. Test guide friction and stops if using the optional cap. Use the separate reinforcement ring with the gusset pattern; the two-sheet pillow naturally has two dry plies.

STL orientations put cups, optional caps and electronics trays flat-face down. Put the flat undersides of the service covers on the bed, with the screw-head recesses facing up. The splice-head pockets in the bottom panels also face up. The chassis frames retain their CAD orientation. Verify that support material can be removed from the revised cover receivers. Check that the inside pockets of the bottom panels clear the installed splice heads. Enable supports for the chassis and review the tool-access holes and service wall openings in the slicer. The three-part coupon and representative chassis and tray parts were sliced for the P2S with a 0.4 mm nozzle, 0.20 mm layers and PLA. The frame checks used automatic tree supports. Before printing, review supports, bridges and recesses with the material and process settings you will actually use.

Actual pump/valve/board connectors and hose bends, electrical ratings, sealing, pressure control and load capacity remain unverified. Do unloaded trials before any load test. Full assembly printing follows the successful coupon and hardware fit check.

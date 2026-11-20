# Print checklist

Use only current `export/stl/BedFrame_*.stl`. Reference hardware is not printed. Old dowel and `BodyNN` exports are archived.

## Geometry checks

- One closed, connected solid per printable STL; millimetre units.
- Every part at most 252 mm on each axis. At pitch 60: cell deck 192×252×36; service 208×136×36; bay 208×136×52; panel 208×136×4.
- M2.5 pilots Ø2.1, clearance Ø2.7; test the chosen screw and material before a full print.
- Actual cassette fits nominal 56 mm seat; recess 2 mm plus separate floor 2 mm.
- Actual valve/fitting envelopes fit; pump/manifold/controller mounting and enclosure size accepted.

## Slicer / physical checks still open

- PETG is a provisional material choice. Select perimeters/infill from the intended load and test results, not this geometry review.
- Inspect support placement and every bridge in Bambu Studio. A 56 mm seat floor over the open underside is not an assumed support-free bridge.
- Candidate cell orientation: seat face down, with removable support limited to the 2 mm recesses; ribs/cavity then grow upward. Verify clean removal without damaging 2 mm floors. Edge printing is another trial option with suitable brim/supports.
- Bay: check the inward upper flange and boss overhangs; panel is a flat print. Do not claim support-free printing until slicing has been examined.
- Print one seat/port coupon and a screw/boss coupon before full parts. Check barb installation, leakage and screw strip-out.
- First fit/pressure trials unloaded; structural capacity and pressure safeguards are separate acceptance work.

A bounding-box pass establishes machine envelope fit only. Full slicing, material, support removal, hardware and load acceptance remain unverified.

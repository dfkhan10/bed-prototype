# CAD strategy: Fusion only

Authored dimensions live in `design/bed_params.json`. `bed_layout.py` derives coordinates and validates limits; `build_bed_frame_environment.py` creates a new Fusion document with feature history. OpenSCAD files are historical and are not a fallback source for current geometry.

`Assembly_Assembled` contains four printable components at pitch 60. `Inspection_Exploded` contains linked instances of the same components. Valve and screw reference components are excluded from print exports.

`save_and_export.py` filters printable component/body names, checks solid interference and timeline health, then writes local assembled/exploded F3D, STEP, per-part STL and a coordinate manifest. It preserves previous STLs in `_old/`; it does not publish or cloud-save.

At pitch 76 the long deck splits by rows, with one four-screw seam. X-axis subdivision is not implemented and oversize widths are rejected.

Native viewport capture is unavailable through the current Fusion MCP workspace. Review PNGs and the interactive viewer use the actual Fusion-exported meshes; they are not image-generated redesigns.

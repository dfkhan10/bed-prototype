# Legacy OpenSCAD (not the active workflow)

The project now uses **Fusion 360** + **`design/bed_params.json`** as the only maintained CAD path.

These files remain as reference / fallback:

- `design/params.scad` — old mirror of dimensions (may drift)
- `design/assemblies/print_master.scad` — batch preview / STL export in OpenSCAD
- `design/parts/*.scad` — individual plates

To print: prefer **STL export from Fusion** after running `build_bed_frame_environment.py`.

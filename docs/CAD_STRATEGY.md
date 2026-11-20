# CAD strategy

The current master is scripted solid CAD in Fusion. [bed_params.json](../design/bed_params.json) contains authored dimensions; [bed_layout.py](../design/fusion/bed_layout.py) derives the coordinate tables and preconditions; [grouped_bed.py](../design/fusion/grouped_bed.py) builds native BRep solids, screw/fitting references, inspection states and exports. [grouped_details.py](../design/fusion/grouped_details.py) produces the cell section and a coupon from the same solids.

The document has editable solid BaseFeatures and TPU-contact fillets. It is not a fully constrained sketch/assembly-joint mechanism. Geometry updates should be regenerated from JSON. STEP exports preserve solid geometry; STL is the print output only. Native PNGs come directly from the Fusion viewport. The offline inspector uses actual exported meshes.

Four-across/three-row grouping, a 172 mm service bay, screw-connected frames, cups, bladder clamps and free moving caps are implemented. Eight frames plus eight bottom panels and two covers keep each print inside the 252 mm allowance. Hardware, hose and TPU references are provisional.

Use [README](../README.md) for opening/rebuilding and [DESIGN_DEBUG](DESIGN_DEBUG.md) for the check boundary. Historical OpenSCAD and old root-level exports are not synchronized dimension sources. CadQuery remains a valid future alternative; Fusion is the current implementation.

# Paste into the next text chat

Continue the compact 12-cell pneumatic bed demonstrator from the current grouped CAD in `export/2026-11-06_grouped/`. Read README and its manifest first. The 4 × 3 CAD and print meshes are implemented; actual kit fit, TPU, slicing and load tests remain open. The following is the approved design intent.

## Fixed decisions

- 12 cells: A–D across, 1–3 down. The approved next layout is four cells across and three rows, with the service section along the four-cell-wide edge. Use two fixed interleaved groups of six: G1 = A1, C1, B2, D2, A3, C3; G2 = B1, D1, A2, C2, B3, D3. Row 1 is nearest the service section. One Arduino/controller with suitable power drivers; I/O expansion is only needed if the actual pin budget requires it. Saved CAD still uses the preceding 3-by-4 layout until rebuilt.
- Cells are heat-welded TPU film bladders. Target moving-cap travel is about 20–30 mm. Smooth movement matters more than speed; timing and working pressure are not frozen.
- A flat printed moving cap over each bladder is approved. At the raised stop, all caps and the fixed pump cover must be on the same top plane. Lowered cells may sit below it.
- Add a real lower structural layer under every cell. Each bladder rests on a supported cup/plate, with ribs/posts down to a common full-length base. The pump section and cell section must have the same bottom level and consistent outer depth: **flat top in the raised state, flat bottom, no Г-shaped stepped underbody**. Do not leave the cell field hanging from the pump box.
- Make neighbouring caps/cells close together. Minimize wide fixed strips, unnecessary borders and gaps. A moving cap may be wider than its bladder and cover the hidden flange/guide area; do not force a wide visible gap just because the bladder needs a mounting flange. Verify cap stiffness and clearance. Package pumps, valves, controller and drivers compactly too. Keep only clearances justified by welds, screws, guides, fittings, tube bends, ventilation and maintenance.
- Connect all printed sections with **M2.5 screws** into rigid receiving features or correctly sized inserts, without exterior bolt/nut pairs. Adhesive alone is not the structural joint. This updates the earlier bonding-only idea. Top split faces must be straight and coplanar, without separately rounded internal edges creating troughs. Finishing can hide seams while preserving service access.
- Each cell has a removable clamp ring with **four M2.5 mounting locations**. Clamp a non-inflating TPU flange outside the airtight weld. Never put mounting holes through the chamber or sealing weld. Support the lower film and air port.
- The fixed upper cell-support structure must also screw to the lower chassis beneath the entire cell field. This is separate from neighbouring section joints, bladder-clamp screws and removable bottom-panel screws. Moving caps stay free to travel on their guides.
- Use guides and stops for the caps. Check the full travel against the bladder, clamps, fittings and tube routes.

## Pneumatics

The latest prototype scope explicitly permits **two fixed interleaved pneumatic groups**, superseding software-selectable independent control of all 12 cells. Keep separate pressure and suction buses. A straightforward circuit uses **two normally closed two-way valves per group**, four valves total. One fills a group; the other extracts air. Both closed means group hold. Never open both for the same group. G1 must be able to rise while G2 lowers, then exchange states. Cells within a group share pressure and can exchange air; equal heights during travel under unequal loads are not guaranteed.

Join the two group valve paths locally to a group tee/manifold and distribute to its six cells. Keep **one bidirectional connection per bladder**, with labelled group trunks and short cell branches. Twelve independent long cell hoses are no longer required. Support cups through ribs/posts around the routing space, rather than solid pedestals that block the ports. Show actual 3D hose/fitting keep-outs, retained bends, strain relief and service loops, and ensure screws/joints cannot pinch them. For planning, interpret the selected 4 mm tubing as nominal internal diameter; 6 mm OD remains a provisional routing allowance until wall thickness is known.

The user's star-shaped connector may be a passive tee joining separately closable paths. Such a tee does not establish that the valve itself is 3/2. A confirmed two-port shutoff in the common hose could provide group hold, but directly joining pressure-pump discharge and extraction-pump inlet also requires inactive-path isolation during operation. Check the actual kit circuit before substituting it for the two shutoff paths per group.

Switch pumps together within each pressure/extraction bank through drivers rated for aggregate running and starting current. Four group valves plus two pump-bank controls require **six switched outputs**, not 32. Individual pump control is unnecessary for this prototype.

Use commercial valves and fittings. A metal hose fitting is fine, but the TPU seal needs a compatible welded port or reinforced, gasketed flange supported by the cassette. Do not thread a fitting into bare unsupported film or block extraction with an unaccounted-for check valve.

Calculate pressure-bank and suction-bank pump counts separately from cell air demand, timing and real installed flow at pressure/vacuum. Do not assume one pump per cell or reuse the old fixed eight-pump layout. The photos show a two-pump kit but do not identify its exact pump curves, valve function or mechanical dimensions. Use adjustable, vibration-isolated mounts until actual hardware is identified/measured.

Check capacity for up to eight pumps in the next layout, together with the four group valves, distribution hardware, controller, six power-driver channels, fittings, wiring and screw access. Eight is a packaging capacity to investigate, not a verified operating count. The supplied pump reference is https://techtonics.in/product/370-micro-dc-air-pump-6vdc/ ; its specification table gives 68 mm length and 24.4 mm diameter, while its prose says 65 mm and 24 mm. It supplies no pressure/vacuum flow curve or complete dimensioned port drawing. Valve and carrier-board documentation still needs identifying.

## Shape and dimensions

Start by evaluating a rounded-square/rounded-rectangle pouch with a controlled gusset or equivalent spare film, supported below, beneath the flat cap. Compare it with a simple welded pillow coupon; measure lift, volume, folding, leaks and repeatability. This is a proposed shape, not a validated optimum.

Do not freeze the old 60 mm pitch, 56 mm opening, pump/valve envelopes or Uno hole pattern. Derive the module pitch from the actual bladder, weld land, four screws, clamp, guides and necessary clearances. Report the active area, cap gap, border widths and resulting overall footprint.

## Model and verification

The full platform may exceed the printer bed. Split it into screw-connected parts with a current maximum envelope of 252 mm for the project's Bambu P2S allowance. Keep one dimension source in `design/bed_params.json` if using the existing local project.

Prefer editable parametric solids, currently Fusion plus scripted exports; code-first solid CAD is an acceptable alternative if it provides equivalent accuracy and checks. STL is a print output, not sufficient design evidence. Deliver assembled/exploded views, top/bottom/side sections, tube routing, individual print parts, STEP/editable model, and a screw/connector BOM.

First show a compact assembly layout and a single-cell section proving the common base, cap travel, clamp/port geometry and screw access. Then develop the complete model using the approved architecture. Do not reopen confirmed choices or mistake previous geometry checks for validation of the new design. Separate modeled/checked geometry from assumed hardware and physical tests still needed.

## Useful prior calculations, not frozen specifications

The old 56 mm active-width scenario gives about 31–94 mL/cell for 20–30 mm rise, with a central 55 mL estimate. At an assumed 10 kPa and 50% reserve, six cells filling over 20 s need about 1.65 L/min ambient-equivalent flow in the pressure bank. A similar extraction budget is only preliminary and must use the actual vacuum curve. Two pumps total could suffice if one pump per bank delivers enough installed flow; four or more may be needed with lower flow or faster/larger groups. Pressure, volume, timing, margin and final count are not verified.

## Files, if the receiving chat has access

Local project: `/Users/ivanyalov/Desktop/Bed prototype`.

- Current requirements: `work/2026-11-06_model_requirements.md`.
- Circuit and calculations: `work/2026-11-06_pneumatic_and_cell_mount_review.md` and `work/2026-11-06_pump_sizing_scenarios.json`.
- Original kit and geometry-feedback images: `inputs/2026-11-06_*`.
- Existing builder/exports: `design/fusion/`, `design/bed_params.json`, `export/`.

These paths do not grant access in another chat. If the files are unavailable, use this self-contained brief and ask for only the specific attachment needed. Do not claim to have read the local project or generated CAD unless you actually have.

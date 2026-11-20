# Pneumatic bed prototype: model requirements

6 November 2026. Historical brief for the first grouped CAD build. The [8 November assembly](../README.md) supersedes the raised top datum and mandatory cap in this brief. The common datum is now 73 mm in the lowered state, and the rigid caps are optional. The latest assembly uses two shared pump lines, pairs of cells within each group, and reserved passages under the cell field. Physical hardware acceptance remains open.

## 1. Intended result

Create a compact 12-cell pneumatic demonstrator with a continuous rectangular housing, a flat common base, and a level upper surface when all cells are raised. Each cell uses a heat-welded TPU bladder to move a flat printed cap. The latest prototype scope uses two fixed interleaved groups of six cells, including one group rising while another lowers. This supersedes the earlier requirement for software-selectable independent control of every cell.

The model must explain the actual assembly: cell supports, bladder clamps, cap guidance, screws, fittings, tube routes, pumps, valves, controller and access panels. A clean exterior must follow from that construction.

## 2. Confirmed requirements

### R1. Cell grid and motion

- Use **12 air cells**, labelled **A–D across and 1–3 down**, controlled in fixed pneumatic groups. Four cells across and three rows is the approved next layout, with the pump/valve service section along the four-cell-wide edge. The current grouped CAD implements this layout.
- Use a checkerboard group map: **G1 = A1, C1, B2, D2, A3, C3; G2 = B1, D1, A2, C2, B3, D3**. Row 1 is nearest the service edge; row 3 is farthest. Each group has six cells and every horizontally/vertically adjacent pair belongs to different groups.
- Provide approximately **20–30 mm of vertical cap travel**. A 25 mm nominal design point is acceptable within that range; it is not a measured bladder capability.
- Prioritize smooth movement. Exact timing is adjustable; the earlier 20 s stroke is a calculation scenario, not a frozen user requirement.
- Provide lower and upper stops and guidance against excessive tilt or jamming. A lowered cap must have a defined mechanical support position.

### R2. Flat top and bottom; no Г-shaped section

- Give the entire assembly, including the cells and pump/electronics section, a **common bottom datum** and a consistent outer housing depth.
- Extend the lower structural layer under **all** cells. Do not place the deeper box only under the pumps and leave the cell section suspended above the table.
- Support each bladder on a rigid lower cup/plate, with ribs/posts carrying loads to the full-length base. The cell field must not be a long cantilever supported by a few cell-to-service screws.
- Keep space beneath each cup for its supported air port and hose bend. Carry loads around that space through ribs/posts; do not fill the under-cup routing region with a solid pedestal down to the base.
- At the upper stop, every moving cap and the fixed pump cover must share **one top datum**. Adjacent fixed sections must also be coplanar.
- Lowered cells may sit below the upper datum. The fixed cover cannot follow the cells through their travel.
- The outer envelope must read as one continuous rectangular platform in side view, with flat assembled bottom panels. Local holes/vents are acceptable; a stepped or Г-shaped underbody is not.

### R3. Compact spacing and packaging

- Bring neighbouring moving caps/cells close together. Avoid the wide fixed bands, oversized borders and gaps visible in `inputs/2026-11-06_spacing_and_section_feedback.png`.
- Minimize exposed non-inflatable area between cells and between the cell field and pump cover.
- Do not unnecessarily make the cap the same width as the active bladder. A wider cap may cover the hidden dry flange, clamp and guide area, allowing a narrow visible gap while retaining room below for reliable seals and screws. Verify its stiffness and full swept clearance. Report moving-cap coverage separately from the actual bladder footprint.
- Also package pumps, valves, controller and driver boards compactly. Every retained space must serve a real need: weld land, clamp screws, guides, fittings, tube bends, ventilation, vibration isolation, electrical clearance or assembly access.
- Derive cell pitch from the complete cell module, including the weld flange and fasteners. **60 mm pitch and 56 mm opening are previous placeholders, not requirements to preserve at any cost.**
- Do not shrink active cell area or enlarge pitch silently to make the layout fit. Report the resulting active area, inter-cap gap, border width and overall dimensions, with the reason for the chosen spacing.
- Minimize the service section after checking complete component and connector envelopes, rather than filling a large box with loosely spaced body blocks.

### R4. Section joints must use screws

- Connect printed housing/deck/base sections with **M2.5 screws** into printed receiving features or properly sized inserts. Exterior bolt-and-nut pairs and loose printed dowels are not the chosen system.
- Explicitly screw the fixed upper cell-support structure to the lower chassis/support structure beneath the entire cell field, as well as connecting neighbouring print sections and removable bottom panels. These are distinct structural interfaces; bottom-panel screws alone do not satisfy the upper-to-lower connection. Keep the moving caps free to travel on their guides.
- Screws are the structural section connections. **Adhesive alone is not an acceptable replacement.** This updates the earlier bonded-top discussion.
- Concealed joint flanges or underside splice plates are acceptable. Each joint needs a shared coordinate table for its matching holes, adequate receiving material and a reachable screwdriver path.
- Choose screw length from the actual grip and engagement. M2.5×10 is the current nominal stock size, not a demand to use the wrong length everywhere.
- Size a thread-forming pilot for the selected screw/material. A heat-set pocket must instead match the actual insert OD/length; the existing Ø2.1 pilot is not an insert pocket.
- Join visible top sections on straight, coplanar internal split faces. Do not round each internal tile edge and create a trough/notch between otherwise adjacent pieces. Keep decorative fillets on the exterior perimeter.
- Surface finishing may reduce visible seams, but it must not replace the screws or make required service access depend on breaking the enclosure apart.

### R5. Welded TPU cell and four-point retention

- Make the airtight cells from **heat-welded TPU film/sheet**.
- Provide a non-inflating mounting flange **outside the complete airtight weld**.
- Clamp that flange with a removable rigid ring and **four M2.5 mounting locations per cell**, 48 locations across the grid. Their holes must not intersect the air chamber or the sealing weld.
- Use smooth edges and controlled clamp compression so the ring does not cut or excessively deform the film.
- Support the lower bladder surface and its port. Do not allow the bladder to hang unsupported between upper frame edges.
- Show the TPU as reference geometry in raised/lowered states, plus its cut/weld/flange pattern. Do not treat those reference shapes as a validated soft-body simulation.

### R6. Flat moving caps

- Fit one flat printed cap over each bladder. The cap distributes contact force and gives a level surface at the raised stop.
- Guides and stops must coexist with the weld land, clamp ring, screws and tube port throughout the full stroke.
- Keep moving gaps small but sufficient for print tolerance and operation. Check the full swept volume, including cap undersides, guide features and fittings.
- A soft cover may be added, provided it does not mechanically tie all cells together so tightly that independent motion is lost.

### R7. Pneumatic architecture: latest fixed-group prototype scope

- Use separate **pressure and suction/extraction buses**.
- Provide inflate, hold and deflate control **per fixed group**, including simultaneous inflation and deflation of different groups. Individual control within a group is no longer required for this prototype.
- A straightforward implementation is **two normally closed two-way valves per group**, one fill and one extraction valve: **four valves total** for G1 and G2. The actual kit valve function remains unresolved; this quantity assumes suitable shutoff valves in the two group paths, not an unidentified three-port valve.
- Hold closes both group paths. Never open both paths of the same group together; use close-before-open sequencing.
- Join the two paths at a group tee/manifold, then branch to the cells assigned to that group. Keep one bidirectional air connection per bladder. Group trunks and short cell branches replace the previous requirement for 12 independent long hoses.
- Fixed group manifolds are now permitted. Cells in a group share pressure and exchange air; equal cap height during travel under unequal loads is not guaranteed. Mechanical stops still define the raised/lowered geometry.
- The user's star-shaped tee description may mean a shutoff valve in the common group line. A verified two-port shutoff there can isolate the group for hold. Permanently joining pressure-pump discharge and extraction-pump inlet also requires isolation of the inactive pump path during flow; do not assume stopped pumps provide that isolation. Confirm the actual circuit before substituting this for the two-valve-per-group implementation.
- Valve pressure/vacuum compatibility and flow direction must be established from the actual component.

### R8. Pumps, controller and fittings

- Use **one Arduino/controller assembly** with suitable power drivers for the pumps and valve coils. Reserve driver boards, wiring and power distribution as well as the Arduino footprint. Add I/O expansion only if the actual pin budget requires it; it is not a requirement for the basic six-output grouped circuit.
- Determine pressure-bank and extraction-bank pump counts separately from measured installed flow at the required operating conditions, cell air demand, largest moving group and timing.
- Do not assume one pump per cell, reuse the old fixed eight-pump tray, or label a provisional count as verified.
- Use modular, vibration-isolated pump cradles; preserve the ability to adjust the hardware layout when actual dimensions are known.
- Check packaging capacity for **up to eight pumps** in the next layout, including mounts, nozzle bends, wires, ventilation and access. This is a packaging capacity to investigate, not a verified operating count or a requirement to install eight pumps. Check the selected group valves, distribution hardware, controller and drivers in the same assembly.
- Pumps within each pressure/extraction bank may be switched together through a driver rated for their combined running and starting current. Separate control of every pump is not required. The straightforward circuit needs 2G valve outputs plus two pump-bank outputs; two groups would need six switched outputs. Do not retain the previous maximum 32-output reservation as a requirement.
- Use commercial fittings/valves. A supported metal hose fitting is acceptable. The airtight TPU connection needs a compatible welded port or a reinforced, gasketed mechanical connection.
- Do not screw a fitting directly into unsupported thin film. Do not place a self-closing check valve in the bidirectional cell hose unless the circuit deliberately opens or bypasses it during extraction.
- Actual pump, valve, carrier-board and hose dimensions remain unverified. The listing photos must not be treated as dimensioned drawings, and the pictured carrier must not be assumed to have Uno mounting holes.

### R9. Tube routes and access

- Route the fixed-group trunks and cell branches beneath the supported cups, labelled by group and cell ID. Keep one bidirectional port per bladder. Determine trunk/manifold positions after selecting the fixed cell-to-group mapping.
- For preliminary layout, interpret the user's selected "4 mm tubing" as 4 mm nominal **internal diameter**. The existing 6 mm OD remains a routing placeholder until wall thickness/actual tubing is confirmed; do not confuse bore with outside diameter or barb crest diameter.
- Model hose centre-lines and full outside diameters, including fittings, tees, bends and necessary service loops. Respect the actual hose's minimum bend radius.
- Provide removable clips and strain relief, and smooth passages across module joints. A tightened housing joint must not pinch a hose.
- Separate tube routes from screw axes, cap/guide travel, sharp edges, hot components and wiring where needed.
- Arrange valve pairs and distribution by fixed group, with labelled branches to cell IDs. Show both pressure and extraction distribution, not just empty grooves or unexplained holes.
- Retain underside service panels so pumps, valves, controller, tubing and cell modules can be serviced.

### R10. Fabrication and model outputs

- Target the Bambu P2S envelope from the project: 256 mm machine size, **252 mm maximum part envelope** as the current design allowance. The complete platform may be larger and must split into screw-connected print sections.
- Maintain a single authored dimension source in `design/bed_params.json`.
- Preserve editable solid geometry. For the current workflow, keep the Fusion master and export STEP plus per-part STL/3MF as appropriate. A code-first solid-CAD alternative is acceptable if it preserves equivalent geometry and checks; STL alone is not the design master.
- Deliver assembled and exploded assemblies, top/bottom/side views, a cell section, tube-routing view, per-part print files, a screw/connector BOM and a dimensions/assumptions table.
- Keep printable solids separate from reference TPU, pumps, valves, fittings and other purchased hardware. Export only intended print parts.

## 3. Recommended inflatable shape

**Starting recommendation: a rounded-square/rounded-rectangular box pouch with a controlled side gusset or equivalent extra film, a supported lower panel and an external dry flange.** It matches the square cap grid and can reserve the extra membrane needed for vertical travel. The cap, not unsupported film, provides the flat contact surface.

This is an engineering recommendation for this package, not a universally optimal bladder shape. Spherical/balloon-like shapes waste corner area under a square cap; long cylindrical chambers make a different row-actuator architecture. A simple two-sheet pillow is useful as a fabrication/leak-test coupon, but its bulging, footprint contraction and required film strain must be measured before relying on it for 20–30 mm lift.

Compare at least a simple rounded pillow and a gusseted version at the same intended footprint. Check rise versus volume/pressure, tilt under the cap, weld repeatability, folding during extraction, leakage and port durability. Do not choose a complicated bellows purely for appearance.

Research on heat-bonded sheet pouches supports using deliberate pouch geometry and fabrication patterns; it does not validate the exact shape, material or operating pressure proposed here. [Niiyama et al., Pouch Motors](https://dspace.mit.edu/entities/publication/99faf708-0640-43aa-aa39-57472996abfc).

## 4. Acceptance checks

| Check | Evidence required |
|---|---|
| Flat assembled envelope | Dimensioned side/section views showing common base and raised-cap/cover top datums; no Г-shaped section |
| Supported cells | Section through a bladder, cup, structural supports and lower base |
| Compactness | Active area, cap gaps, borders and fitting/access keep-outs dimensioned and justified |
| Four-point clamps | 48 cell mounting locations, outside the weld/chamber, with matching ring/base coordinates |
| Screw-connected sections | Joint drawings, screw lengths/engagement and tool access; no adhesive-only structural joint |
| Complete motion | Clearance/interference checks at both stops and intermediate travel for caps, guides and reference bladders |
| Pneumatic function | Fixed group map and per-group state table, two buses, selected group valves, trunk/branch routes and interlock logic; verify inactive-pump isolation if using a common pump tee |
| Pump count | Explicit volume/timing assumptions plus actual installed pressure/vacuum performance, or an honest provisional sizing result |
| Print files | One intended connected solid per part; millimetre dimensions checked against CAD; ≤252 mm envelope; no stray/reference bodies |
| Physical fit | One cell/port/clamp/guide coupon and a real pump/valve/hose trial before treating the full assembly as print-ready |

Working pressure, final bladder pattern, film thickness, screw/insert details, actual hardware models, timing, measured pump count, final footprint and rated load remain open. Earlier 10 kPa, shape factor 0.7 and 50% flow reserve were calculation assumptions, not accepted operating specifications. The earlier mesh and interference checks apply only to the old model.

## 5. Modeling workflow recommendation

Use parametric solid CAD for this assembly, with mesh files generated from it for printing. **Fusion is the recommended current master** because the project already has a functioning scripted solid-model/export workflow. Scripted CAD such as CadQuery can also produce editable solids and STEP/STL without operating a desktop CAD UI; it is an alternative CAD workflow, not proof that an STL-only design is superior. [CadQuery documentation](https://cadquery.readthedocs.io/en/latest/intro.html), [Fusion mesh export](https://help.autodesk.com/cloudhelp/ENU/Fusion-Mesh/files/MESH-SAVE-AS-MESH.htm).

An unspecified built-in 3D/CAD capability should be evaluated by whether it preserves real editable solids, dimensions, assemblies, reliable booleans/fillets and STEP export. A rendered preview or a valid triangle mesh alone does not establish those capabilities. No equivalent built-in CAD kernel has been verified for this chat.

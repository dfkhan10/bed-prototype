# Hardware dimensions and open measurements

6 November 2026. Authored CAD dimensions live in `design/bed_params.json`. Its current values describe the preceding model, not the approved next 4-by-3 layout. Use [current requirements](../work/2026-11-06_model_requirements.md) for that next layout. Historical kit estimates are preserved in `_old/2026-11-06_before_revision/docs/HARDWARE_DIMENSIONS.md`.

| Item | Current nominal envelope | Evidence / status |
|---|---|---|
| Cell / cassette | 56 mm seat, 2 mm recess, Ø6.5 bottom port | Mechanical placeholder; actual cassette not measured |
| Valve body | 22 × 12 × 30 mm | Prior photo estimate; ports, wires and retention not measured |
| Tube | 4 mm ID / 6 mm OD | Prior kit assumption; verify actual hose and bend radius |
| Pump | Baseline reserves 68 mm axis length, Ø31 head; a newly supplied seller reference lists 68 mm length, Ø24.4 | Baseline estimate and seller reference are different evidence. Exact kit match, nozzle locations and installed performance remain unverified; **operating count unknown**; no mount generated |
| Controller | Carrier envelope unidentified; photo appears to show a Nano-format board on a carrier | One Arduino confirmed; no Uno mounting pattern is established by the photo |

Confirmed next layout: 12 cells A1–D3, four across and three rows, with the service section along the four-cell-wide edge. Keep caps close together over hidden flanges/guides. Screw the fixed upper structure to the lower chassis, keep routing space beneath the supported cups, and retain removable underside access. The old 2 mm seat is baseline geometry, not a validated welded-cell interface.

## Hardware evidence received

The [Techtonics 370 pump listing](https://techtonics.in/product/370-micro-dc-air-pump-6vdc/) specifies 6 V, 0.15 A, 68 mm length, 24.4 mm diameter and 30 g. Its description instead says 65 mm and 24 mm. These are supplier reference values, not measured kit values or a dimensioned mounting/port drawing. No pressure-flow curve or vacuum performance is supplied there. Do not silently replace the old CAD reference with a claim of verified fit.

The user also supplied a generic hardware description based on similar-looking breathing-simulation kits, without an exact component datasheet or seller identification. It proposes 370-series pumps, a possible 3/2 solenoid, an Arduino carrier, tubing and a 1–2 A adapter. Its voltage alternatives, flow/pressure/vacuum ranges, current, noise and life figures are **unverified comparison ranges**. They do not select this kit's ratings, dimensions or pneumatic connections. Absence of publicly available exact datasheets has not been established by that description.

## Next assembly capacity and interfaces

| Assembly item | Design basis | Remaining check |
|---|---|---|
| Pumps | Investigate space for up to eight, on replaceable, vibration-isolated cradles | Actual pressure/extraction counts, body and nozzle envelope, hose bends, wire exits, cooling and removal access |
| Group valves | Four normally closed two-way valves: one fill and one extraction for each of two fixed groups | Exact valve model, low-pressure/vacuum compatibility, flow direction, leakage, ports, coil voltage/current and connector clearance |
| Group/cell hoses | Two fixed group networks, each branching to six cells; one bidirectional connection per bladder | 4 mm nominal ID is the planning interpretation of the user's selection; actual OD/wall thickness, material, bend radius, barb compatibility, retainers and service loops remain to check |
| Cell port | One supported bottom connection per bladder; tee/manifold beside each group's valve pair | Weld-compatible or reinforced gasketed seal, pull resistance, fitting geometry and leak test |
| Controller and drivers | One Arduino plus six power-driver outputs: four valves and two pump banks; no mandatory I/O expansion or individual pump switching | Actual driver/board sizes, terminals, cable exits, heat and screwdriver access; each bank driver must handle aggregate pump current |
| Power distribution | Size for the selected components, active loads and motor starting | Exact rail voltages, running/starting current, driver ratings, suppression and adapter capacity; the kit's proposed 1–2 A supply is not accepted for the expanded assembly |

The latest user-approved simplification is two fixed interleaved groups of six: G1 = A1, C1, B2, D2, A3, C3; G2 = B1, D1, A2, C2, B3, D3. Row 1 is nearest the service edge. Each group may energize at most one valve of its pair, so at most **two group-valve coils** are active. Hold de-energizes both valves of that group. Cells within a group share pressure and exchange air; they are not independently position-locked. Actual power sizing also includes the operating pumps, electronics, transients and component duty ratings.

A standard 3/2 valve selects between two paths; it has no separate third closed position. [Bürkert's operation explanation](https://www.burkert.com/en/service-support/knowledge-center/glossary/Plunger-type-solenoid-valves-3-2-way) shows these states, but does not identify the photographed kit valve. A passive star-shaped tee joining separately closable branches is a different component arrangement and can support hold when the branches close. A two-port shutoff in the common group hose can also isolate the group, but a direct pressure-pump/extraction-pump tee needs inactive-path isolation during flow. Verify this circuit rather than assuming either that the kit valve is 3/2 or that stopped pumps seal their forward flow paths.

Do not identify the carrier as a MOSFET driver solely from its appearance. Arduino logic pins must drive suitable power stages; the [classic Nano pinout](https://content.arduino.cc/assets/Pinout-NANO_latest.pdf) specifies 20 mA maximum per I/O. Nano PCB dimensions do not establish carrier dimensions or mounting holes.

The generic claim of 4–6 mm-ID tubing is not a fit specification for a roughly 4 mm-OD nozzle. Match a fitting's stated tubing-ID range to the actual tube material and dimensions; keep tube OD separate for routing/clips. [Nordson's barb guide](https://fluid-components.nordsonmedical.com/files/fluid-components-nordsonmedical-com/Technical%20Information/Barb%20Information/barb-styles.pdf) distinguishes barb dimensions from tube internal diameter.

Eight listed 68 × 24.4 mm reference envelopes can be placed in two rows of four within a 272 × 48.8 mm rectangle, ignoring mounts, fitting/wire envelopes and all spacing. This is **body-envelope arithmetic only**, not a completed service-bay or print-fit check.

## Operating count and release boundary

Pump sizing needs: target pressure, initial/final cell volume (or measured air demand), largest simultaneous group, fill time, leakage allowance, and installed pressure/vacuum flow in the intended circuit. Determine each bank separately. Eight is a capacity to check, not an operating requirement. Neither generic free-flow ranges nor maximum pressure/vacuum values establish usable flow during the stroke. Power-rail voltage must follow the actual motor/driver ratings.

Use a common flow reference for demand and pump ratings. For a first isothermal estimate, air demand expressed at atmospheric pressure is `(P_final_abs × V_final − P_initial_abs × V_initial) / P_atm`, summed over the simultaneously inflated cells. Required flow is demand divided by fill time plus leakage. A preliminary parallel-pump count is `ceil(required flow / available flow per pump at pressure)`. Pressure varies during filling, and manifold/valve losses matter; verify with the real circuit. No numeric count is justified by the current inputs.

Proceed with adjustable mounts and replaceable hardware trays for provisional layout work; exact manufacturer datasheets are not the only possible evidence. Measurements, a fit coupon and a real pump/valve/hose trial can establish the necessary interfaces. Until then, distinguish reserved envelopes from verified hardware fit, and do not release the complete assembly as print-ready.

Latest analysis: [pneumatic and cell-mount review](../work/2026-11-06_pneumatic_and_cell_mount_review.md).

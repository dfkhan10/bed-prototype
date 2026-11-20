# Hardware dimensions and open measurements

Current grouped CAD: 4 × 3 cells, overall 344 × 432 × 73 mm. Dimensions are authored in [bed_params.json](../design/bed_params.json). Native solid checks establish fit of these provisional envelopes, not measured fit of the actual kit.

| Item | Modelled reference / interface | Status |
|---|---|---|
| Cell | 56 mm active area; 80 mm dry-flange cup; optional 82 mm cap; 25 mm nominal lift | TPU shape, weld and lift require coupon testing |
| Pump | 68 mm axis length, Ø24.4 body, two provisional +X port envelopes; eight adjustable cradles | Seller body reference; actual ports/wires/flow unverified |
| Valve | 12 × 22 × 30 mm body, two provisional X-axis barbs; four valves | Exact NC 2/2 model, ports, flow and vacuum function unverified |
| Tube | 4 mm ID, 6 mm OD, R12 assumed minimum centreline bend | Actual hose and fittings need trial |
| Controller/driver | Two 90 × 45 mm board references on stacked 136 × 68 mm slotted trays with open rear relief | Actual board/connector envelopes not measured |
| Bladder port | Supported Ø20 weld flange, Ø14 cup passage | Select a weld-compatible bought fitting; seal is not an FDM nozzle |

## Hardware evidence received

The [Techtonics 370 pump listing](https://techtonics.in/product/370-micro-dc-air-pump-6vdc/) specifies 6 V, 0.15 A, 68 mm length, 24.4 mm diameter and 30 g. Its description instead says 65 mm and 24 mm. These are supplier reference values, not measured kit values or a dimensioned mounting/port drawing. No pressure-flow curve or vacuum performance is supplied there. Do not silently replace the old CAD reference with a claim of verified fit.

The user also supplied a generic hardware description based on similar-looking breathing-simulation kits, without an exact component datasheet or seller identification. It proposes 370-series pumps, a possible 3/2 solenoid, an Arduino carrier, tubing and a 1–2 A adapter. Its voltage alternatives, flow/pressure/vacuum ranges, current, noise and life figures are **unverified comparison ranges**. They do not select this kit's ratings, dimensions or pneumatic connections. Absence of publicly available exact datasheets has not been established by that description.

## Current assembly capacity and interfaces

| Assembly item | Design basis | Remaining check |
|---|---|---|
| Pumps | Eight provisional envelopes on replaceable, vibration-isolated cradles | Actual pressure/extraction counts, body and nozzle envelope, hose bends, wire exits, cooling and removal access |
| Group valves | Four normally closed two-way valves: one fill and one extraction for each of two fixed groups | Exact valve model, low-pressure/vacuum compatibility, flow direction, leakage, ports, coil voltage/current and connector clearance |
| Group/cell hoses | Two fixed group networks, each branching to six cells; one bidirectional connection per bladder | 4 mm nominal ID is the planning interpretation of the user's selection; actual OD/wall thickness, material, bend radius, barb compatibility, retainers and service loops remain to check |
| Cell port | One supported bottom connection per bladder; tee/manifold beside each group's valve pair | Weld-compatible or reinforced gasketed seal, pull resistance, fitting geometry and leak test |
| Controller and drivers | One Arduino plus six power-driver outputs: four valves and two pump banks; no mandatory I/O expansion or individual pump switching | Actual driver/board sizes, terminals, cable exits, heat and screwdriver access; each bank driver must handle aggregate pump current |
| Power distribution | Size for the selected components, active loads and motor starting | Exact rail voltages, running/starting current, driver ratings, suppression and adapter capacity; the kit's proposed 1–2 A supply is not accepted for the expanded assembly |

The latest user-approved simplification is two fixed interleaved groups of six: G1 = A1, C1, B2, D2, A3, C3; G2 = B1, D1, A2, C2, B3, D3. Row 1 is nearest the service edge. Each group may energize at most one valve of its pair, so at most **two group-valve coils** are active. Hold de-energizes both valves of that group. Cells within a group share pressure and exchange air; they are not independently position-locked. Actual power sizing also includes the operating pumps, electronics, transients and component duty ratings.

A standard 3/2 valve selects between two paths; it has no separate third closed position. [Bürkert's operation explanation](https://www.burkert.com/en/service-support/knowledge-center/glossary/Plunger-type-solenoid-valves-3-2-way) shows these states, but does not identify the photographed kit valve. A passive star-shaped tee joining separately closable branches is a different component arrangement and can support hold when the branches close. A two-port shutoff in the common group hose can also isolate the group, but a direct pressure-pump/extraction-pump tee needs inactive-path isolation during flow. Verify this circuit rather than assuming either that the kit valve is 3/2 or that stopped pumps seal their forward flow paths.

Do not identify the carrier as a MOSFET driver solely from its appearance. Arduino logic pins must drive suitable power stages; the [classic Nano pinout](https://content.arduino.cc/assets/Pinout-NANO_latest.pdf) specifies 20 mA maximum per I/O. Nano PCB dimensions do not establish carrier dimensions or mounting holes.

The generic claim of 4–6 mm-ID tubing is not a fit specification for a roughly 4 mm-OD nozzle. Match a fitting's stated tubing-ID range to the actual tube material and dimensions; keep tube OD separate for routing/clips. [Nordson's barb guide](https://fluid-components.nordsonmedical.com/files/fluid-components-nordsonmedical-com/Technical%20Information/Barb%20Information/barb-styles.pdf) distinguishes barb dimensions from tube internal diameter.

Eight listed 68 × 24.4 mm reference envelopes can be placed in two rows of four within a 272 × 48.8 mm rectangle, ignoring mounts, fitting/wire envelopes and all spacing. This earlier arithmetic is superseded by the grouped CAD envelope check; actual kit fit remains open.

## Operating count and release boundary

Pump sizing needs: target pressure, initial/final cell volume (or measured air demand), largest simultaneous group, fill time, leakage allowance, and installed pressure/vacuum flow in the intended circuit. Determine each bank separately. Eight positions are part of this prototype layout, four per bank; installed flow and timing still require measurement. Neither generic free-flow ranges nor maximum pressure/vacuum values establish usable flow during the stroke. Power-rail voltage must follow the actual motor/driver ratings.

Use a common flow reference for demand and pump ratings. For a first isothermal estimate, air demand expressed at atmospheric pressure is `(P_final_abs × V_final − P_initial_abs × V_initial) / P_atm`, summed over the simultaneously inflated cells. Required flow is demand divided by fill time plus leakage. A preliminary parallel-pump count is `ceil(required flow / available flow per pump at pressure)`. Pressure varies during filling, and manifold/valve losses matter; verify with the real circuit. No numeric count is justified by the current inputs.

The current CAD includes adjustable mounts, replaceable hardware trays and eight-pump capacity; exact manufacturer datasheets are not the only possible evidence. Measurements, a fit coupon and a real pump/valve/hose trial can establish the necessary interfaces. The full print set is a nominal prototype. Begin with the mechanical coupon and fit the actual components before printing the complete assembly.

Latest analysis: [pneumatic and cell-mount review](../work/2026-11-06_pneumatic_and_cell_mount_review.md).

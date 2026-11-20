# Hardware shopping list · 8 November 2026

## Current decision · six pumps, hardware first

Keep one complete two-pump kit. Change the extra two-pump kit quantity from one to **two**, for **six pumps total**. Plan three inflation and three extraction pumps if the measured parts suit those roles. Keep eight positions in the service bay and leave one position per bank empty.

Increase the standalone MOSFET quantity from four to **six**, covering four valve channels and two pump-bank channels without relying on the kit switches. The pictured Zave board lists 5–18 V input and 0–60 V switched load. Flyback protection and usable current with a 5 V Arduino output still need verification. At the screenshot prices, the extra HK$68.51 kit and two HK$5.03 modules bring the estimate from HK$409.24 to **HK$487.81** before any quantity discount or checkout changes.

Order the hardware first. After it arrives, measure the pump bodies, hose barbs and wire exits, the valve bodies and ports, each fitting with hose installed, and the controller with its shield and plugs attached. Verify pump ratings and current, valve pinout and switch compatibility before wiring the six-pump assembly. Mock up one valve pair and one under-cell cross to determine the clip and carrier locations. Use those measurements to revise the cell port, hose routing and mounts, then print one cell and the affected fit-test parts before the full set.

## CAD changes after the hardware arrives

Baseline for this revision is the existing 4 × 3 soft-surface field, two groups of six, 84 mm cell pitch and 25 mm nominal travel. Use the six-pump configuration while retaining eight usable mounting positions. The 4 × 2 field remains an option for a separate layout decision.

| CAD area | Change to make or fit to verify |
| --- | --- |
| Pump layout and cradles | Model three installed pumps per bank and one reserved position per bank. Choose the occupied positions from the actual body and nozzle dimensions. Fit the cradle saddles, isolation pads and strap slots to the pump bodies. Keep room at all eight positions for both nozzles, hoses, wires, ventilation, fasteners and removal. |
| Pump headers | Route separate inflation and extraction headers for three pumps each. Use a closed end or a removable sealed termination at the expansion point. Locate the installed tees and elbows from the measured barb and hose envelopes. Leave a clear path to add the fourth pump per bank. Confirm which nozzle connects to the header and which stays open to ambient. |
| Valve carrier and service tees | Place four actual valves in two pairs. Revise the slot positions, retaining straps and wire exits from the measured valve bodies and barbs. The 28.1 mm tee leaves about 2 mm of nominal tip-to-tip gap at the current locations. Offset the tee or stagger the valves if the assembled hose segments cannot be fitted or removed. |
| Under-cell fittings, routing and clips | Replace the nominal fitting solids with the measured tees, crosses and elbows. Keep one bidirectional branch per bladder. For the 12-cell field, each group has two crosses and one terminal tee. Move the clips onto straight bare hose outside the barbs. Redraw branch lengths and bends, then check the assembled envelopes against the ribs, splice plates, screws, panels and adjacent hoses. Add local clearances only where the fit check shows a conflict. |
| Cell cup and TPU port | Adapt the existing Ø14 mm cup opening for a replaceable, mechanically sealed through-fitting. Model a smooth backing face, gasket seat and controlled compression against the film, plus a barb for the actual 4 mm ID hose and clearance underneath for the hose bend and strain relief. Keep the air passage open both ways and the seal separate from the perimeter clamp. If the port itself is printed, leak-test its body as well as the film-to-gasket joint. |
| TPU clamp and soft surface | Revise the cup and clamp for the [cap-free surface](#10-november--soft-tpu-surface-without-rigid-caps). Check the clamp gap against the welded film stack and keep screw holes outside the airtight seam. Update the TPU cut and weld template with the actual port hole and reinforcement if needed. Check deflated height, lift and cover clearance on two adjacent cells. |
| Controller and driver trays | Model the kit controller and shield as one installed stack with their actual mounting holes and plugged-in cables. Fit an adapter plate or revise the tray slots. Lay out six switch channels using the verified kit and standalone modules. Give the boards standoffs, room for terminals and wiring, and access for replacement. |
| Power, USB and harness | Fit the DC inlet and USB opening to the real plugs and their insertion paths. Add strain relief and tie points where needed. Keep wires away from hose bends, panel screws and cover fasteners. Use the existing service passages where the assembled harness fits. |
| Frame, service covers and underside panels | Resolve confirmed conflicts locally. Preserve the shared bottom datum and structural screw joints. Check that covers and bottom panels can be removed, screwdrivers can reach the M2.5 heads, and removing a pump, valve or board does not pull on a bladder hose. |

For the later pressure-sensing review, keep access to each group's line downstream of its fill/extraction tee and to the existing reserve passages. That gives us a place to measure each group's air pressure if selected. Sensor model, bracket, tap size and wiring are separate decisions.

After the revision, regenerate the Fusion assembly, fit-test STLs, hardware and print BOMs, hose cut list, and routing and assembly views. Check the fitted envelopes and tool access in CAD. Then print one cell and representative fitting/clip and valve-carrier pieces. Check hose fit, port sealing, the cell stroke and service access before releasing the full print set. [Current CAD parameters](../design/bed_params.json) · [Tube routing](../docs/TUBE_ROUTING.md) · [Assembly](../docs/ASSEMBLY.md)

### 10 November · soft TPU surface without rigid caps

Use the 4 × 3 field of TPU bladders under a removable, loosely fitted fabric cover. Choose the bladder shape for the weld, clamp and clearance between cells. Rigid caps can tilt and bind under a load shared across two cells, even in a circular guide.

- **Cell cups and clamps.** Remove the moving caps and their cap-specific guide bores, sleeves and stops from the final CAD and print set. Retain the four corner screws on each cell's TPU clamp and the cup-to-frame fasteners. Redesign the cup and clamp around the bladder shape and dry flange. Keep the sealed port and round the edges that the film or cover can touch. Check the real film stack, port and lowered height before fixing the dimensions.
- **Cover attachment.** Use four sewn loops on rounded hooks, one at each outer corner of the fixed frame outside the moving cell field. Leave enough slack in the removable cover to follow the full height difference between adjacent cells.
- **Motion test.** Test two adjacent cells from opposite groups under the fabric cover. Place an object across their seam and alternate which cell is raised and lowered. Check that both complete the cycle under load, that the film clears the cup edges, and that the cover has enough slack to follow the height difference.
- **Sensor insert trial.** Sew pockets into a removable fabric liner, aligned with the bladder centres. Start with two pockets. A pocket should keep the FSR from sliding or turning without pressing on its active area. Test a small, smooth backing to keep the FSR head flat and guide its tail into a sewn wire channel. Leave wire slack between pockets and bring the harness to one detachable connector at the cover edge. Check for pocket shift and signal changes during unloaded cycling, then apply the same load at the centre, edge and seam. Use the results to choose the sensor and decide whether to extend the liner to three rows of four.

## Selected cart · fit review

The cart screenshot before the pump decision shows **HK$409.24** before any pressure-measurement parts. It includes one ready-to-use kit, one additional two-pump kit with switches, four separate 5 V NC valves, four separate MOSFET modules, 10 m of 4 mm ID × 6 mm OD silicone tube, 15 tees, four crosses, ten elbows and two units of 0.20 mm double-matte TPU film. Each film unit is 0.50 × 1.37 m, or 0.685 m². One is enough for the estimated 0.5 m² allowance, and the second is spare material. Verify that the film can be heat-sealed.

| Area | Check and print implications |
| --- | --- |
| Hose and fittings | The hose matches the nominal CAD size. The tees, crosses and elbows are the right nominal type. Their listing dimensions are 28.1 mm across, 30 × 30 mm and approximately 22.6 × 22.6 mm respectively. The diagram for the elbow specifies 3–5 mm hose ID. The cut list is 3.64 m before assembly allowance. |
| Crosses under the cells | The CAD cross is 16 × 16 mm. The cart cross reaches 15 mm either side of its centre. At the current clip positions, its stem overlaps the nominal clip span by 8 mm in G1 and 3 mm in G2 along the trunk. Move clips to straight bare-hose sections away from the barbs and check the fitting and its attached hoses against frame webs and bottom panels. Retain the existing clip profile if the hose fits the 6.8 mm bore. |
| Service tees and elbows | At the current valve centres the 28.1 mm tee leaves about 2 mm from its tip to each nominal valve-barb tip. Mock up with the actual hoses. Offset the tee and stagger the valve pair if needed, then move the valve slots or clips to match. The header uses 8 mm cubes as junction placeholders. Model the actual 22.6 mm elbows in place and check the space around the pump outlets and front service passage before cutting local clearances. |
| TPU and cell port | The 0.20 mm film matches the design thickness per ply. The outer clamp and frame can be used to test a welded pillow. The current cup has a 14 mm centre passage intended for a purchased flanged port. For a printed alternative, revise the cup centre for a replaceable through-fitting and gasket with a backing face. Check clearance underneath for the hose and strain relief. Test the seal and the connector itself on the one-cell print. The cart includes the film. The gasket and sealing method are still to be selected. |
| Pumps and valves | The revised cart supplies six pumps. Their body sizes, barb diameters and orientations are unverified. Measure before resizing the 27 mm strap cradle or moving the branch headers. Check the four valves against their nominal 12 × 22 × 30 mm bodies and actual wired/hosing envelope before changing the slotted valve carrier. |
| Controller and wiring | The tray is 136 × 68 mm. The nominal board model is 90 × 45 mm. An official Uno Rev3 is 68.6 × 53.4 mm and uses USB-B, so a board of that size fits the tray in plan. Verify the kit board, shield stack, mounting holes, USB plug and power pigtail. Use a board adapter or revise the tray and cable openings if needed. Four standalone MOSFETs leave two channels to cover using verified kit switches or two more standalone channels. [Uno Rev3 dimensions](https://store.arduino.cc/products/arduino-uno-rev3) |

After measuring the hardware, print the single-cell stand, cup and clamp ring for the port trial. Check whether any frame or bottom panel needs a local clearance change before printing the full set. CAD fit conclusions above use listing dimensions and nominal CAD positions. No geometry or print exports were changed. [CAD parameters](../design/bed_params.json) · [One-cell assembly](../docs/ASSEMBLY.md#first-print)

## Order together · assembly deadline

Use one purchasing round with spares. Test parts from the batch as soon as it arrives. The M2.5 screws are already in transit, and the RC servo extensions were removed from the cart.

- Order the complete two-pump kit plus two compatible extra pairs for six pumps total.
- Order six 5 V, 2/2 normally closed air valves, four installed plus two spares. Ask the seller to confirm suction capability and the Four-Wire variant pinout. A spare of the same model covers part failure, so confirm compatibility before choosing the batch.
- Order eight single-channel MOSFET modules if buying independent of the kit electronics, six installed plus two spares. Confirm 5 V control and load compatibility. Include 12 suitably rated flyback diodes if the load circuits lack them, allowing one per pump or valve and two spare at six pumps. Include stranded wire, terminals, heat-shrink, a switch and a fuse holder if unavailable on the bench. Select the fuse and pump-bank drivers against actual combined starting and operating current.
- Keep the 10 m coil of 4 mm ID × 6 mm OD hose, 15 tees, four crosses and 10 elbows. Add one pressure/vacuum manometer with its tubing adapter, a 4 mm manual vent valve, 5–10 removable plugs for 4 mm ID hose and a few straight barbed unions. Choose reducers after checking actual pump and valve ports. Check mechanical fit of the tees and crosses against the chassis before full printing.
- If TPU assembly has the same deadline, order compatible weldable film and ports together. Allow about 0.5 m² of 0.20 mm trial-grade film. Buy 14 verified ports for 12 cells or 10 for eight cells, two spare either way. Include access to a compatible sealing setup. Weld one cell first using parts from the batch.

## Cart audit

Baseline: current CAD has 12 cells in two groups, four group valves and space for eight pumps. The first hardware order targets six pumps. An eight-cell build keeps both groups and all four valves. It needs eight bladder ports and two crosses if the second row ends in tees. No eight-cell CAD revision has been selected.

| Cart item | Audit |
| --- | --- |
| Ready-to-use kit, HK$230.01 × 1 | Keep for the balloon test. The packing photo shows two pumps, one valve, wiring, an Uno-style board with shield and a 5 V / 5 A adapter. Verify plug, demo files and wiring/air routing. |
| Extra self-assembly kit with switches, HK$68.51 × 2 | This is the Qing Yu listing, from a different seller. The photo shows two pumps, a valve, three harnesses and tube per kit. Check pump ratings and the function and ratings of the electronic switches. Identical appearance does not establish compatible pumps or harnesses. |
| 5 V NC valves, HK$4.65 each | Correct advertised type, 2/2 normally closed. Ask for the Four-Wire with Terminals pinout, port diameters, flow direction, low-pressure operation, vacuum suitability, coil current and duty rating. Test one valve from the batch under positive pressure and suction before installing the rest. Count an included valve only if it passes the same checks. |
| MOSFET module, HK$5.02 each | Check switching of a 5 V load from a 5 V Arduino GPIO, OFF at reset, flyback protection and real continuous/starting current. Six working channels total for the bed, including any verified kit channels. |
| Servo extension, 30 cm, 5 per pack | Removed. The pictured cable is a three-contact RC servo extension. Revisit only if a kit harness uses that connector with the same pinout. |
| Silicone hose, 4 mm ID × 6 mm OD, 10 m | Matches the nominal hose dimensions and covers the 3.64 m geometric cut list with spare. Test on the actual barbs and at the tightest bends with the suction pump running. |
| 4 mm tees, 3 packs × 5 | Correct nominal hose size, 15 pieces for 12 CAD positions plus spares. Actual tee is 28.1 mm across with a 2.5 mm bore. Recheck fit and flow. |
| 4 mm crosses × 4 | Correct nominal hose size and 12-cell count. Actual cross is 30 × 30 mm with a 2.3 mm bore. Recheck fit and flow. |
| 4 mm elbows, pack of 10 | Correct nominal type and count for eight CAD positions, subject to the seller's tubing ID and assembled fit. |

The service tee and field crosses were represented by 16 mm CAD spans between tips. Compared with those references, the cart's tee adds 12.1 mm and the cross adds 14 mm. Keeping the cart tee centered between the existing valve references leaves about 2 mm of tip-to-tip separation on each side before allowing for the tube and installation access. This is a nominal geometry check. Trial fit the actual fittings and valve barbs, especially between the valves and under the cell field. The small bores also warrant a flow test before adding pumps. [Design parameters](../design/bed_params.json)

## First order · one complete kit

Original purchase images were recovered from the 8 November ordering chat on 13 November: [selected HK$230.01 variant](../inputs/2026-11-08_selected_kit_variant.jpg) and [packing list plus Mind+ code](../inputs/2026-11-08_selected_kit_contents.jpg). The example is labelled `uno`, includes `DFRobot_Servo.h`, and attaches three Servo objects to D8, D9 and D10. Its loop alternates `angle(abs(180))` and `angle(abs(0))`. This is evidence for servo-pulse control of the included inline electronic switches; do not treat them as verified ordinary HIGH/LOW MOSFET inputs. The screenshot does not establish the exact main-chip marking. Current bench assignments D3/D5/D6 require our own matching firmware rather than running the seller example unchanged.

Choose one **“Completely Equipped and Ready to Use” kit** from the friend-recommended listing. The selected variant is **HK$230.01** in the screenshot, HK$36.71 above the control-panel variant. Its packing list shows two pumps, one wired valve, an Uno-style board with a shield, three short harnesses, a USB cable, tubing, a balloon, and a **5 V / 5 A adapter** with a barrel-jack pigtail. The listing shows a Mind+ upload and a generated sketch controlling two pumps and the valve. It advertises a tutorial video. Confirm the exact board model and whether the seller supplies the editable demo project or sketch, the wiring and hose-routing diagrams, and an HK-compatible plug.

Test the two kit pumps on the supplied balloon before connecting the welded TPU cells. The 5 V / 5 A marking applies to the included adapter. Suitability for the full bed depends on the actual pump and valve loads. Prices and pictured contents come from the supplied screenshots.

## Next order · separate parts

Ask both sellers for the exact pump models, their inflation and extraction roles, rated voltage, and running and starting current. Check the kit valve's port count and whether it is normally closed before counting it toward the four needed.

The kit packing photo shows no separate tee or Y hose fittings. A tee or Y is a passive three-way junction. In the bed, one tee per group joins the hoses from that group's fill and extraction valves to its cell line. The two wired valves open and close those paths so the group can inflate, extract or hold. Use the fitting counts below for the full routing. Match the barbs to the actual tubing ID. [Tube routing](../docs/TUBE_ROUTING.md)

Test the kit on the supplied balloon and verify the controller, supply and pump behavior. The full-build CAD quantities below account for all eight pump positions. The first build targets six pumps.

| Item | Full build | What to order |
| --- | ---: | --- |
| Arduino | 1 | Use the kit board if it is programmable and can control six driver inputs. For a separate purchase, Arduino Nano R4 is a compact 5 V logic option with USB-C. [Arduino specs](https://docs.arduino.cc/hardware/nano-r4/) |
| DC diaphragm air pumps | 8 positions | 4 inflation + 4 extraction. Start with one for each role. The CAD uses an approximately 68 × Ø24 mm pump body as its reference. Check exact model, voltage, running and starting current, pressure and suction flow, duty cycle, and body and port dimensions before buying the balance. [CAD hardware notes](../docs/HARDWARE_DIMENSIONS.md) |
| Solenoid air shutoff valves | 4 | 2-port, 2-position, normally closed (2/2 NC). Each group gets one fill and one extraction valve. Choose direct-acting valves rated for air, low differential pressure and the required vacuum, with compatible hose barbs. Count the kit valve toward the four only after confirming its function. |
| MOSFET power drivers | 6 switched channels | 2 pump-bank channels and 4 valve channels. Match the logic level and load voltage, include flyback protection, and rate each bank channel and its wiring for four pumps starting together. |
| Power and wiring | 1 set | Regulated DC supply, matching panel inlet, switch, fuse and holder, power distribution, wire and connectors. Choose supply voltage and current after checking both banks running together, up to two valve coils, the controller and motor startup. Include a controller regulator if the chosen supply and board require one. |
| Pneumatic hose | 5 m to start | Flexible air hose nominally 4 mm ID × 6 mm OD. The CAD cut list totals 3.64 m before service allowance. Check barb fit and that the tube stays open under suction. [Hose cut list](../export/2026-11-08_grouped/2026-11-08_hose_cut_list.csv) |
| Barbed fittings | 12 tees, 4 crosses, 8 elbows | Sizes to suit the selected hose. The 12 tees include 2 terminal tees. Add adapters if pump or valve barbs need a different tube size. |
| M2.5 screws | 200 × 10 mm, 40 × 8 mm, 14 × 6 mm | CAD counts for the soft-surface build. Suggested pack quantities are 250 / 50 / 20 after testing a sample screw in the printed pilot. Match the head profile to the recesses. |
| Mounting hardware | 1 set | 32 pump isolation washers, 16 pump straps or ties, 4 valve straps and 8 board spacers/retainers to suit the selected boards. |

## Missing from the pressure test

- **One compound pressure/vacuum gauge or differential manometer for air**, with a low-kPa range, a tee and an adapter to 4 mm ID hose. One port references atmosphere if the instrument is differential. Size it for the expected pressure and suction and verify the overpressure rating. Tap the line downstream of the group's fill/extraction junction. A second instrument is useful for simultaneous measurements. For automatic feedback, plan one bidirectional pressure sensor per group. [Honeywell differential pressure ranges](https://automation.honeywell.com/content/dam/honeywell-edam/sps/common/en-us/industries/healthcare-and-life-sciences/medical-equipment/documents/sps-medical-abp-series.pdf)
- **Test fittings and sealing supplies.** A few removable 4 mm hose plugs, spare tees, and straight or reducing barbs once the pump/valve port sizes are known. Small hose retainers if needed after a pull and leak test. Use a plugged test segment and pressure decay to distinguish manifold leaks from cell leaks.
- **Pressure limit and a way to vent.** Provide a controlled means to stop inflation and manually vent during testing. Establish the permitted positive and negative pressure from the real components and bladder coupon. If the pump can exceed the permitted pressure, use an independent low-pressure limit or relief sized for the pump flow. Check placement against both isolatable groups and any pressure trapped when their valves close. Select a device after setting the limits.
- **Electrical bench items, if unavailable.** Multimeter, suitably rated current measurement or current-limited bench supply, power terminals, stranded wire, heat-shrink, fuse and holder, switch and rated flyback protection per load where absent. Check the rail during simultaneous startup. The 5 V / 5 A adapter is the demo kit supply. Evaluate it with the expanded load before reusing it.
- **Optional after testing.** Inline check valves only if pump branches need isolation after a backflow test. Keep any check valve out of the common bidirectional bladder line. Filters or mufflers can be evaluated on the ambient sides if needed and checked for restriction.

## Later · TPU and soft surface

| Item | Full build | What to order |
| --- | ---: | --- |
| Bladder hose ports | 12 installed, 14 suggested | One open, bidirectional weld-compatible TPU port per bladder. CAD assumes a nominal Ø20 mm weld flange and Ø14 mm cup passage. Start with 2–3 samples. Verify that the port flange and film can be welded with the same process and that the barb fits the hose. A reinforced bulkhead fitting with gasket is a second option if adapted to the cup. [Weldable flange example](https://www.carmo.dk/en/technical-components/valves/threaded-flange/) |
| TPU bladder film and welding | 12 cells + trial pieces | Roughly 0.5 m² of weldable film is a purchasing allowance. The CAD assumes 0.20 mm per ply. Get a sample of film and ports together. Use a temperature/pressure-controlled sealing setup or a fabrication service that can seal both the perimeter and flange. Allow material for the dry-flange reinforcement rings on the gusseted pattern. [Film welding](https://solutions.covestro.com/en/highlights/articles/theme/processing-technology/welding-films) · [Gusset pattern](../export/2026-11-08_grouped/coupon/2026-11-08_TPU_gusset_pattern.svg) |
| Soft top layer | 1 | Flexible cover for the cell field. The CAD reserves 4 mm of thickness at the lowered position. Check that it flexes enough for adjacent cells to move in opposite directions. |

## Build order

1. Run the two-pump kit on the supplied balloon. Check pump polarity/port direction, driver behavior, power and the hose fit. Record ratings and measurements for the actual parts.
2. Test a standalone valve for low-pressure flow, vacuum and hold, with a manometer and a known sealed test segment. Assemble the real tees, crosses and valves in a fit trial before printing the full chassis.
3. Weld and fit one TPU cell. Check for leaks, pressure decay, port retention, rise and suction collapse. Establish operating limits before cycling cells under load. The one-cell coupon uses eight M2.5 × 10 screws.
4. Connect both groups and confirm that one can inflate while the other extracts, followed by a hold test. Record rise/fall time and supply voltage during pump startup. Use those results to decide whether the four-pump trial is sufficient.

[CAD hardware BOM](../export/2026-11-08_grouped/2026-11-08_hardware_BOM.csv) · [One-cell assembly](../docs/ASSEMBLY.md#first-print)

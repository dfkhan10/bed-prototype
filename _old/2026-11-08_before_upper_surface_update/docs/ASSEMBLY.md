# Grouped prototype assembly

Use the current [print BOM](../export/2026-11-06_grouped/2026-11-06_print_BOM.csv) and [hardware BOM](../export/2026-11-06_grouped/2026-11-06_hardware_BOM.csv). STL units are mm; quantities refer to the full model. Bought reference fittings are generic envelopes, not selected catalogue parts.

## First print: one cell

Print the four files in [coupon/stl](../export/2026-11-06_grouped/coupon/stl/): stand, production cup, clamp ring and G1 cap. Use eight M2.5×10 screws (four cup/frame, four flange clamp), two M2.5×6 guide-stop screws and two M2.5-clearance OD8 × 1 mm washers. The stand has underside access bores.

For a dry motion trial, fit the cap guide shafts through the ring and cup, then attach their underside stop washers/screws. Remove the cap again before fitting the bladder and tightening the four top clamp screws; the cap covers their tool path. Confirm free 25 mm motion, both stops, screw engagement and 1 mm minimum low-stop clearance above the base. The Ø4 shafts/Ø4.8 bores and Ø2.1 pilots are starting tolerances; do not force a binding cap or substitute a heat-set insert without redesigning its pocket.

Fit a supported, weld-compatible bought bladder port through the Ø14 cup opening; the Ø20 flange supports it at the floor. This is not an airtight printed nozzle. Test the two [TPU patterns](../export/2026-11-06_grouped/coupon/): simple pillow first, then gusset pouch. Gusset version needs its separate dry reinforcement ring to produce two 0.2 mm dry plies at the 0.35 mm clamp gap. Clamp/guide holes remain outside the airtight weld. Neither pattern is a proven 25 mm actuator. Test port pull resistance, sealing and motion unloaded.

## Full assembly sequence

1. Leave bottom panels off. Join the eight lower frames using the seventeen four-screw splice plates and the shared joint coordinate table. Install the two elevated service-centre splice plates before trays and pumps; those screws are not intended for access through installed equipment.
2. Subassemble each upper cell outside the chassis: support the port, place the bladder/dry reinforcement and ring, then tighten four M2.5×10 clamp screws with the cap removed. Insert the cap guide shafts and attach underside stop washers/screws. Mount this complete cell on the hollow chassis columns using four M2.5×10 screws from below, through the Ø6.4 bores. Keep moving caps free of fixed structural screws.
3. Build and label G1/G2 networks. Pre-attach the six clips to their bottom panels, one screw per clip from below. Snap the two-height trunks into them as the panels are offered up to the chassis. Fit branches, six four-way crosses and two end plugs. Inspect passages across frame seams before tightening panels.
4. Fit pump cradles, compliant pads and retaining straps. Preassemble the two PCB trays outside the chassis, using four M2.5×10 screws through the lower tray into the upper legs. The lower feet have head-clearance pockets. Then fit the boards, attach the tray stack to its bottom panel and fit the four valves on their adjustable carrier. Confirm actual connectors and wire exits before tightening. Route pressure and extraction headers as shown in the routing view, preserving hose bend space.
5. Fit removable bottom panels, then service covers. Check that screw tips and heads cannot touch hoses. Covers and fully raised caps share z73; cap tops at the lowered stop are z48.

Four NC 2/2 valves serve the two fixed groups. Both valves closed holds a group; fill and extraction for the same group must never open together. Verify the actual valve ports, polarity, vacuum compatibility and bank isolation with an unloaded bench circuit before connecting bladders. Six power outputs are reserved: four valves and two pump banks. Electrical drivers, aggregate starting current, suppression and power supply ratings still need selection.

Do not smooth seams with adhesive as a substitute for screws. Test material, thread stripping, guide friction, pressure, leaks and structure before loading the prototype.

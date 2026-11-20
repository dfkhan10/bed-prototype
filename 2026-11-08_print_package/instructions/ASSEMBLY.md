# Grouped bed prototype assembly

Use the 8 November print BOM. Standard print files are in `stl/`. The rigid caps are in `optional_caps/`, separate from the soft-surface build. The full chassis is 344 × 432 mm, with a common top datum at 73 mm above the bottom.

## First print

Print the one-cell stand, cup and clamp ring from `coupon/stl/`. Attach the cup to the stand with four M2.5×10 screws. Use four M2.5×10 screws to clamp the dry TPU flange outside the airtight weld. The weld-compatible port goes through the Ø14 cup opening and has a nominal Ø20 flange footprint. Match the port and hole to the actual fitting.

The cup support is at z63. The CAD reserves 6 mm for the lowered TPU envelope and 4 mm for the soft cover to reach z73. These are nominal allowances. Check the real cover and chamber height in the deflated state, the rise under load, and the weld and port for leakage. The modelled rise is 25 mm. The optional guided cap has a lower stop at z73 and an upper stop at z98. If testing the cap, fit two M2.5×6 stop screws and two M2.5-clearance OD8 × 1 mm washers. The soft cover and rigid cap represent separate surface configurations.

## Full layout

1. Leave the bottom panels off while joining the printed frame sections with the splice plates and M2.5 screws. Install the elevated service-centre splices before fitting the pumps and the G1 hose. Their drivers approach from below.
2. Assemble the cups, TPU and clamp rings, then secure the cups to the taller chassis columns with M2.5×10 screws from below. Check driver reach and screw fit on the coupon.
3. Attach the separate pump cradles, valve carrier and two electronics trays. Both trays have an open rear notch for cables. Route and clip the electrical harness separately from the pneumatic lines. Use the round wall opening for power and the separate rectangular opening to access a USB-C plug or panel coupler. Match its mounting to the selected hardware.
4. Connect the four pressure pumps, four extraction pumps, group valves, tees and cell branches as shown in [Tube routing](TUBE_ROUTING.md). Check second-port access, connector engagement, bends and removal clearance using actual parts.
5. Fit the removable bottom panels with the Ø6 head pockets facing inward over the lower splice screws. Install the service covers from above with four recessed M2.5×8 screws per cover. The covers can then be opened with the bed on the bench. Inspect slicing, print the coupon, and check physical hardware fit before producing the full set.

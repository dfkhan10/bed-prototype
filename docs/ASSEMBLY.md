# Grouped bed prototype assembly

Use the [10 November print set and fit-check guide](../export/2026-11-10_bed_print_stl/2026-11-10_READ_FIRST.md). It contains six pump cradles, twelve cups and twelve clamps, without rigid moving caps. The full chassis is nominally 344 × 432 mm, with a common top datum at 73 mm above the bottom. The 8 November print BOM and standalone coupon are earlier references.

## Bench electronics · 13 November 2026

The user reports six pumps and three small metal air valves available. The first wired test assembly has two pumps and one valve, each with a three-wire cable and an inline module under heat-shrink. The proposed assignments are D3 = pump 1, D5 = pump 2 and D6 = valve 1. These are chosen software labels, not electrically verified device identities or the seller's recovered pin map.

The [recovered seller example](../inputs/2026-11-08_selected_kit_contents.jpg) is labelled `uno`, includes `DFRobot_Servo.h`, and attaches its three channels to D8, D9 and D10. It controls them with servo-angle endpoints 0 and 180, which generate timed servo pulses. Use that interface for the included inline switches; a plain digital HIGH/LOW interface has not been established. Standard Arduino Servo 1.3.0 is installed for a future matching implementation. The present D3/D5/D6 assignments can be used with matching firmware; they are not the seller example's original pin numbers. The exact chip is not legible in the purchase image, so Uno remains a working profile rather than a validated device identity.

In the supplied top-down shield photo, the digital header columns are marked **S, +, −** from left to right, with the pin numbers beside S. Each cable spans all three columns at one digital pin number. Match the module's actual signal, supply and ground to these markings; wire colours alone do not confirm its pinout.

Use the complete kit's specified 5 V supply for the initial kit test, after checking the input connection and cable orientation. Do not substitute the available 12 V supply directly for a 5 V rail. The full bed's supply capacity, pump-bank starting current, driver capacity and flyback protection remain unverified. The grouped design uses two pump-bank driver channels and four independent valve channels. With three valves, the full two-group fill/extract/hold circuit is incomplete. Do not parallel three pumps on an unqualified driver.

For initial USB diagnosis, isolating actuator loads helps distinguish USB supply problems from bootloader problems. Opening the serial port can reset the board and restart the installed sketch. USB alone may also energize shield supply pins, so removing the barrel supply does not establish that connected loads have no power. The user has explicitly chosen to retain the three attached loads during the current USB-only diagnosis and authorized firmware replacement. No actuator-start command is authorized by that diagnostic step.

The Mac currently enumerates `/dev/cu.usbserial-10` with USB VID/PID `1A86:7523`. This identifies the USB interface, not the microcontroller or attached loads. Arduino AVR Boards 1.8.8 is installed. On 13 November, bounded read-only STK500/Arduino probes at 115200 and 57600 baud did not establish a bootloader connection or return a validated chip signature. No firmware was uploaded. Read the main chip marking or establish the correct reset/bootloader procedure before another upload attempt.

The [USB diagnostic sketch](../build/2026-11-13_arduino/BedUsbDiagnostics/BedUsbDiagnostics.ino) compiles for `arduino:avr:uno` (2932 bytes of flash, 262 bytes of static RAM); this build target is provisional until the controller/bootloader is confirmed. The sketch provides `INFO`, `STATUS` and `HELP` at 115200 baud, and has no actuator commands. D3/D5/D6 remain INPUT with pull-ups disabled. High impedance is not a verified OFF state for an unknown driver, and reported input levels cannot identify pumps or validate wiring. Compilation is checked; on-board operation is not yet checked.

## First print

For the current cell geometry, start with one each of Cup_AC, Clamp_AC, Cup_BD and Clamp_BD from the 10 November set and follow its fit-check guide. The standalone stand and dimensions below describe the earlier 8 November coupon; do not assume that stand fits the later cups without a fit check.

Print the one-cell stand, cup and clamp ring from `coupon/stl/`. Attach the cup to the stand with four M2.5×10 screws. Use four M2.5×10 screws to clamp the dry TPU flange outside the airtight weld. The weld-compatible port goes through the Ø14 cup opening and has a nominal Ø20 flange footprint. Match the port and hole to the actual fitting.

The cup support is at z63. The CAD reserves 6 mm for the lowered TPU envelope and 4 mm for the soft cover to reach z73. These are nominal allowances. Check the real cover and chamber height in the deflated state, the rise under load, and the weld and port for leakage. The modelled rise is 25 mm. The optional guided cap has a lower stop at z73 and an upper stop at z98. If testing the cap, fit two M2.5×6 stop screws and two M2.5-clearance OD8 × 1 mm washers. The soft cover and rigid cap represent separate surface configurations.

## Full layout

1. Leave the bottom panels off while joining the printed frame sections with the splice plates and M2.5 screws. Install the elevated service-centre splices before fitting the pumps and the G1 hose. Their drivers approach from below.
2. Assemble the cups, TPU and clamp rings, then secure the cups to the taller chassis columns with M2.5×10 screws from below. Check driver reach and screw fit on the coupon.
3. Attach the separate pump cradles, valve carrier and two electronics trays. Both trays have an open rear notch for cables. Route and clip the electrical harness separately from the pneumatic lines. Use the round wall opening for power and the separate rectangular opening to access a USB-C plug or panel coupler. Match its mounting to the selected hardware.
4. Fit three inflation pumps and three extraction pumps, retaining one empty reserved position per bank. Connect the four group valves, tees and cell branches as shown in [Tube routing](TUBE_ROUTING.md). Complete this circuit only when the fourth suitable valve is available. Check second-port access, connector engagement, bends and removal clearance using actual parts.
5. Fit the removable bottom panels with the Ø6 head pockets facing inward over the lower splice screws. Install the service covers from above with four recessed M2.5×8 screws per cover. The covers can then be opened with the bed on the bench. Inspect slicing, print the coupon, and check physical hardware fit before producing the full set.

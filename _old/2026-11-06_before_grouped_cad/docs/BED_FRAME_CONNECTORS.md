# Mechanical connectors

Current revision: 6 November 2026. M2.5 **thread-forming screws into plastic**. No dowels or exterior nuts. Heat-set insert pockets are deferred until insert OD/length is known.

| Joint | Qty | Clearance / receiver | Assembly access |
|---|---:|---|---|
| Cell → service | 4 | Ø2.7 / Ø2.1 blind pilot; Y-axis | Open underside of cell deck, before hoses; short hex driver |
| Bay upper flange → service | 8 | Ø2.7 flange / service Ø2.1 pilot | Upward driver from inside open bay; panel off |
| Bottom panel → bay | 8 | Ø2.7 panel / bay Ø2.1 pilot | From below panel |
| Extra seam at pitch 76 | 4 | Ø2.7 / Ø2.1 pilot; Y-axis | Open underside, before routing |

Current purchase quantity: **20 M2.5 × 10 mm screws**, plus spares. Generic screw references in the exploded model show placement, not a specific head/thread product. Verify the chosen screw's recommended pilot in a PETG coupon.

Boss OD 5.5 mm, receiver depth 8 mm, pilot depth 7 mm. Inward-set bottom bosses have short webs to the shell. Both eight-point interfaces use the same XY coordinates from `bed_layout.layout()`; their screw directions differ to preserve driver access.

Cell-joint X = −84, −22, 22, 84 mm; Z = 26 mm. The shared mating plane is `mate_y = −deck_length/2`; service starts 0.3 mm farther toward −Y. Both sets of holes have the same X/Z axis. This replaces the previous vertical lap-hole arrangement.

Cassette fasteners must not penetrate the pressurized chamber. Cassette clamps, controller standoffs, pump mounts, actual valve retention and heat-set pockets remain hardware-dependent; they are not represented as finished interfaces.

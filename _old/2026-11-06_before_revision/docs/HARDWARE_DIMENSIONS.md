# Hardware dimensions — Taobao kit (photo + 370 pump datasheets)

Sources: your assembly screenshot, product listing photo, and common **370 micro DC air pump** specs (same motor family as the kit).

## Photo scale check (assembly screenshot)

Reference: **Arduino Uno PCB** = **68.6 × 53.4 mm** (official).

| Feature | Visual vs Uno | Estimated size |
|---|---|---|
| Pump motor cylinder | ~⅓ Uno width | **~24–25 mm Ø** |
| White pump head | wider than motor | **~30–32 mm Ø** |
| Pump body length (motor + head, axis horizontal) | ~1× Uno width | **~65–70 mm** |
| Solenoid valve (blue) | small vs pump | **~20 × 12 × 28 mm** |
| Uno + yellow sensor shield stack | — | **~28 mm** tall |
| Tubing on nozzle | — | **4 mm ID / 6 mm OD** typical |
| Pump wires + JST | exit motor end | reserve **≥ 35 mm** gutter per row |

The listing photo matches the common **370-6V aquarium / blood-pressure micro pump** (not a large box pump).

## Catalog numbers (use in CAD until you caliper your batch)

| Part | Parameter keys in `params.scad` | Nominal (mm) |
|---|---|---|
| 370 pump motor OD | `pump_motor_d` | 24.5 |
| Pump head OD | `pump_head_d` | 31 |
| Pump axis length | `pump_axis_l` | 68 |
| Nozzle bump above head | `pump_nozzle_h` | 8 |
| Outlet OD (for tube) | `pump_port_od` | 4.2 → use **6 mm** routing |
| Solenoid valve body | `valve_l/w/h` | 22 × 12 × 30 |
| Arduino Uno | `ctrl_board_l/w` | 69 × 54 |
| Shield stack height | `arduino_stack_h` | 28 |
| Pump count (target) | `pump_count` | 8 (6–8 supported in layout) |

Electrical (for wire gauge / fuse planning, not CAD):

- ~**0.15–0.32 A** per pump at 6 V (datasheets vary).
- **8 pumps** peak **~2.5 A** if all run together → **12 V 3 A** brick or separate pump power rail recommended.

## Closed electronics bay (8 pumps + Arduino)

Layout in CAD: **2 rows × 4 columns** pump cradles, Arduino in a dedicated pocket **beside** the pump block (same bay), wire gutter between.

| Envelope | Size (mm) |
|---|---|
| Internal bay floor | **200 × 128** (`e_bay_x` × `e_bay_y`) |
| Internal height | **52** (`e_bay_cavity_h`) — fits shield + nozzle clearance |
| Split line (optional) | Left/right pump tray at **100 mm** (`e_bay_split_x`) for two P2S prints |

## Multi-plate screw stack (see `design/lib/joints.scad`)

```text
deck_service_section (top — valves / solid deck)
        ↕ M3 perimeter + corner bosses
electronics_bay_rim (short wall + flange)
        ↕ M3 grid (e_bay_tray_boss_h)
electronics_bay_tray (8× pump cradles, wire channels)
        ↕ M3 standoffs
electronics_bottom_panel (Arduino mount, vents, USB notch)
```

**Fusion 360:** Autodesk MCP was not connected in this session. Parametric source remains OpenSCAD; import STLs to Fusion for fillets/chamfers if needed.

When parts arrive: measure **head OD**, **axis length**, and **nozzle height**, then edit only `design/params.scad` and re-export.

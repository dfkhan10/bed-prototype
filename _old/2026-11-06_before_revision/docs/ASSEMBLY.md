# Assembly — pneumatic deck (Fusion / 3×4)

## Printed STLs (`export/stl/`)

| Part | Qty |
|------|-----|
| `BedFrame_CellDeck` | 1 |
| `BedFrame_ServiceDeck` | 1 |
| `BedFrame_ElectronicsBay` | 1 |
| `BedFrame_BottomPanel` | 1 |

## Hardware — **M2.5 screws** (шурупы, не болт+гайка)

| Item | Qty (typ.) | Use |
|------|------------|-----|
| **M2.5 × 10 mm** screw | 4 | Cell deck ↔ service (`mate_y`) |
| **M2.5 × 10 mm** | 8 | Bottom panel ↔ bay bosses |
| **M2.5 heat-set insert** | 8–16 | Press into printed bosses (recommended) |
| **M2.5 standoff + screw** | 4 | Arduino |
| 4 mm pneumatic tube | 12 runs | Cell ports (bottom-center) |
| 2/2 solenoid valves | 12 | Service pockets |
| 370 micro pumps | 8 | Electronics bay |

Optional: **thread-forming** M2.5 for PETG bosses without inserts (prototype only).

## Order of assembly

1. **Electronics bay** — mount pumps, route wires; bay sits under service deck (already positioned in model).
2. **Service deck** — install **12 valves** in pockets; route stub channels toward **`mate_y`**.
3. **Cell deck** — lay **12 tubes** in underdeck channels; barbs at **bottom-center** ports (from below).
4. **Join cell + service** at **`mate_y`**: align **4× M2.5** clearance holes; tighten screws into **service-side bosses** or inserts (no printed dowel pins).
5. **Bottom panel** — Arduino on standoffs; **8× M2.5** through panel into bay bosses; USB toward future notch.
6. **Cassettes** — TPU bladders; drop into shallow seats (inflate **upward**).
7. **First test** — no load on deck; one cell inflate/deflate; check leaks at **2 mm floor** ports.

## Tubes

Label cells **A1–A3 … D3** (3 wide × 4 long). One tube per cell from valve OUT → foot routing → cell port. See [TUBE_ROUTING.md](TUBE_ROUTING.md).

## Legacy OpenSCAD names

Old table (`deck_cell_section`, M3, dowels) — **obsolete**; do not use for this branch.

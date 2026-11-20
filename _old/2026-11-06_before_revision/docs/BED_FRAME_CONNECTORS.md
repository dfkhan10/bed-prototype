# Mechanical connectors — Fusion target

**Fastener policy:** **M2.5 screws (шурупы)** into **printed bosses** or **heat-set inserts** — **no bolt+nut**, no printed dowel pegs.

Params: `bed_params.json` → `fasteners`. Debug: [DESIGN_DEBUG.md](DESIGN_DEBUG.md).

## A. Electronics bay

| ID | Joint | Spec | Status |
|---|---|---|---|
| E1 | Bottom panel ↔ bay | 8× M2.5, bosses on panel + bay | **Modeled** (verify insert depth) |
| E2 | Service ↔ bay rim | M2.5 flange | **Target** |
| E3 | Bay split print | 3× M2.5 flange | **Target** |
| E4 | Arduino | M2.5 standoffs | **Modeled** |
| E5 | Pump pockets | 8× | **Modeled** |
| E6 | USB / vent | bottom panel | **Target** |
| E7 | Tubes ↔ cell deck | bulkhead @ `mate_y` | **Target** |

## B. Cell deck ↔ service (3×4)

| ID | Joint | Spec | Status |
|---|---|---|---|
| D1 | Alignment | screw holes only (no Ø5 dowel) | **Modeled** v1.0 |
| D2 | Joint | **4× M2.5** shared X @ `mate_y` | **Modeled** v1.0 |
| D3 | Print size | 194×254 @ pitch 60 | **OK** P2S |

## C. Cassettes

| ID | Spec | Status |
|---|---|---|
| C1–C3 | Shallow seat, bottom port | **Modeled** |

## D. Pneumatic

12× valve / 12× cell tube / 8× pump — external manifolds.

## BOM summary (buy)

| Screw | ~Qty |
|-------|------|
| M2.5 × 10 | 20+ |
| M2.5 heat-set insert | 16+ |

Cloud: **bed frame** / `BedPrototype_Frame_v1.f3d`

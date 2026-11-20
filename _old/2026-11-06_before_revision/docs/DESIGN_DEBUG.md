# Design debug — known issues (script v0.9)

Codex: **fix these before new features**. Owner wants **small screws (шурупы)**, not bolt+nut; cleaner industrial design.

## P0 — geometry / assembly wrong

| ID | Symptom | Cause | Fix |
|----|---------|-------|-----|
| G1 | Cell ↔ service screws **don’t line up** | Lap holes use `deck_x/3` on cell but `service_x/3` on service (`service_x` ≥ `deck_x`) | One **`joint_screw_x[]`** in JSON; same X on both parts at **`mate_y`** |
| G2 | **Dowel pegs** as separate STL bodies | `NewBodyFeatureOperation` pegs + duplicate names → stray `Body39`/`Body45` | **Remove printed pegs**; use **2× pilot holes Ø3** + **4× M2.5** screws only |
| G3 | **Tube bulkhead** missing | Foot pass-through cut fails in API when only cell exists | Cut after both decks exist; or model as **slot in service flange** |
| G4 | **12 valves** in 5-column layout | Rows overlap service bay footprint | Re-layout **4×3** or **6×2** from real valve envelope; verify in top view |
| G5 | Valve stub channels aim wrong | `vy - foot_y` mixes service-local Y with cell foot | Route: cell run ends at **`mate_y`**; valve stubs start there |

## P1 — fastener mess

| ID | Issue | Fix |
|----|-------|-----|
| F1 | **M3** bosses on bay (`boss_d` 8, `m3_hole_d`) | Migrate to **`fasteners` M2.5** bosses + pilot for **heat-set** or **plastic thread-forming screw** |
| F2 | Mixed **dowel Ø5 + M3 lap** | Single system: **M2.5 × ~10 mm screw** into **printed boss** or **insert** |
| F3 | No **bottom panel** body | Add **`BedFrame_BottomPanel`** + screw grid into bay floor |

## P2 — DFM / print / looks “crooked”

| ID | Issue | Fix |
|----|-------|-----|
| D1 | Sharp outer corners | Apply **`corner_r`** on deck footprint (chamfer/fillet pass in Fusion or script) |
| D2 | Blocky bay shell | Rim flange, consistent **`panel_t`**, align outer walls to **`e_bay_x/y`** |
| D3 | Pitch 76 → deck **>256 mm** | **`cell_pitch` 60** or **split cell deck** + screwed seam |
| D4 | Export junk bodies | Export filter: only names **`BedFrame_*`** |

## P3 — pneumatic clarity

| ID | Issue | Fix |
|----|-------|-----|
| P1 | Deep wells (old) | Keep **`cell_seat_depth`** shallow; **`cell_floor_t` 2** + port center |
| P2 | Clips not aligned to route length | Place slots at ⅓, ⅔ of **`cell_run_len`** |

---

## Verification after fix

1. Fusion rebuild → **only** `BedFrame_*` bodies (no `BodyNN`).
2. Section view: **mate_y** one plane; **4 screw holes** coaxial through cell + service.
3. Bottom panel separates bay; **≥8× M2.5** from panel into bosses.
4. STL bbox: cell deck **≤252 mm** on longest edge.
5. Update [BED_FRAME_CONNECTORS.md](BED_FRAME_CONNECTORS.md) + [ASSEMBLY.md](ASSEMBLY.md).

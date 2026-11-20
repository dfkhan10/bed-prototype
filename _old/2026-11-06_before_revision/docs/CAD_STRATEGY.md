# CAD strategy — Fusion only

## Single stack

| Piece | Location |
|---|---|
| **Dimensions** | `design/bed_params.json` |
| **3D model** | Fusion — run `design/fusion/build_bed_frame_environment.py` |
| **Cloud project** | Hub **`bed frame`** → `BedPrototype_Frame_v1.f3d` |
| **Print** | Export STL from Fusion → **Bambu P2S** |

Do **not** maintain a second dimension set elsewhere. Change **`bed_params.json`**, rerun the script, save, export.

## Model contents (one rebuild)

- **BedFrame_CellDeck** — 3×3 wells, ribs, bottom-center ports, underdeck runs, clip slots, foot bulkhead
- **BedFrame_ServiceDeck** — coplanar top, 9× valve pockets + stub channels to foot
- **BedFrame_ElectronicsBay** — pumps, M3 bosses, Arduino standoffs, tube pass-throughs
- **BedFrame_DowelPeg** — mating pins at cell↔service joint

## OpenSCAD

Legacy exports under `design/parts/` and `design/assemblies/`. Use only if you cannot export from Fusion; params may be stale vs `bed_params.json`.

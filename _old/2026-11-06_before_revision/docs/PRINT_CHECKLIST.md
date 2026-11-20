# P2S print checklist

## Before slicing

- [ ] Updated `design/params.scad` if hardware measured
- [ ] Chosen material: **PETG** (default) or ABS for deck
- [ ] Layer height 0.2 mm (structural) or 0.16 mm (cassettes)
- [ ] Walls ≥ 3, top/bottom ≥ 5 layers

## Fit tests (print first)

1. **`cell_cassette`** × 1 — must slip into well with slight wiggle
2. **`tube_clip`** × 2 — snap into one channel slot
3. **`deck_cell_section`** — only after cassette fits

## Full batch

- [ ] `deck_cell_section` — ~240×240 mm footprint, check bed placement
- [ ] `deck_service_section` — ~240×90 mm
- [ ] `bottom_panel`
- [ ] `cell_cassette` × 9
- [ ] `tube_clip` × 24

## Post-processing

- [ ] Drill/clean port holes if stringing
- [ ] Install heat-set inserts for bottom panel
- [ ] Dry-fit bottom panel — verify pump height clearance

## Bambu Studio tips

- Use **brim** on large deck parts if corner lifting
- **Avoid** ironing on cassette seating surfaces (dimension creep)
- For tall cavity walls, enable **slow outer wall** on last layers

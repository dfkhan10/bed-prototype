// Export: electronics_bay_rim.stl — short wall between tray and service deck
include <../lib/util.scad>
include <../lib/joints.scad>

module electronics_bay_rim() {
  difference() {
    union() {
      difference() {
        rounded_rect_3d(e_bay_x, e_bay_y, e_bay_rim_h, corner_r);
        translate([0, 0, 2])
          rounded_rect_3d(e_bay_x - 6, e_bay_y - 6, e_bay_rim_h, corner_r - 2);
      }
    }
    // bolt through rim into tray bosses
    perimeter_boss_grid(e_bay_x, e_bay_y, -eps, e_bay_rim_h + 2, deck_rim);
    // tube pass-through to cell deck (forward edge = +Y toward cells)
    for (sx = [-60, 0, 60])
      translate([sx, e_bay_y / 2 - 8, -eps])
        cylinder(h = e_bay_rim_h + 2, d = 10, $fn = 24);
  }
}

electronics_bay_rim();

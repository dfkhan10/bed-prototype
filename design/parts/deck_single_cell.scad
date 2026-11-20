// Export: deck_single_cell.stl — Stage 1: one cell + mini service bay (fits one P2S plate)
include <../lib/util.scad>

module deck_single_cell() {
  x = well_open + deck_rim * 2 + 80;
  y = well_open + deck_rim * 2 + service_len;

  difference() {
    rounded_rect_3d(x, y, deck_top_t + cavity_h, corner_r);
    translate([0, 20, deck_top_t])
      well_cut(well_open, cavity_h + eps);
    translate([0, 20, deck_top_t])
      cell_underdeck_plumbing(20, y);
    // pump + 1 valve pocket
    translate([-20, -y / 2 + 35, deck_top_t])
      rotate([90, 0, 0])
        cylinder(h = pump_l, d = pump_d + 2, $fn = 48);
    translate([20, -y / 2 + 35, deck_top_t])
      cube([valve_w + 2, valve_l + 2, valve_h], center = false);
    translate([0, 0, deck_top_t + 2])
      rounded_rect_3d(x - deck_rim * 2, y - deck_rim * 2, cavity_h - 4, corner_r - 2);
  }
}

deck_single_cell();

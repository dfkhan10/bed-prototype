// Export: electronics_bay_tray.stl (+ optional electronics_bay_tray_left/right if split)
// Mid plate: 8× pump cradles, wire gutter, M3 bosses to bottom panel and rim
include <../lib/util.scad>
include <../lib/joints.scad>
include <../lib/pumps.scad>

module tray_body(x, y, t) {
  rounded_rect_3d(x, y, t, corner_r);
}

module electronics_bay_tray(half = "full") {
  x = half == "full" ? e_bay_x : e_bay_split_x + split_flange_t / 2;
  x_off = half == "left" ? -e_bay_x / 2 + x / 2 : half == "right" ? e_bay_x / 2 - x / 2 : 0;

  difference() {
    union() {
      translate([x_off, 0, 0])
        tray_body(x, e_bay_y, e_bay_tray_t);
      if (half == "left" || half == "right")
        translate([x_off + (half == "left" ? x / 2 : -x / 2), 0, 0])
          split_flange_seam(0, e_bay_y - deck_rim * 2, e_bay_tray_t);
    }
    translate([x_off, 0, -eps])
      pump_block_cradles("cut");
    translate([x_off, 0, -eps])
      wire_gutter_cut();
    // Arduino keep-out (tray only — board mounts on bottom panel below)
    translate([arduino_pocket_x + x_off, arduino_pocket_y, -eps])
      rounded_rect_3d(ctrl_board_l + 6, ctrl_board_w + 6, e_bay_tray_t + 2, 4);
    // split seam holes
    if (half == "left" || half == "right")
      translate([x_off + (half == "left" ? x / 2 : -x / 2), 0, 0])
        split_flange_holes_z(e_bay_tray_t, e_bay_y - deck_rim * 2, 3);
  }

  translate([x_off, 0, e_bay_tray_t])
    perimeter_boss_grid(x, e_bay_y, 0, e_bay_cavity_h - e_bay_tray_t - panel_t - 4, deck_rim);

  translate([x_off, 0, 0])
    pump_block_cradles("solid");
}

electronics_bay_tray("full");

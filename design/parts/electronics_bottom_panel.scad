// Export: electronics_bottom_panel.stl — closes bay; Arduino standoffs on inside face
include <../lib/util.scad>
include <../lib/joints.scad>

module arduino_standoffs() {
  hole_spacing_x = 61;
  hole_spacing_y = 46;
  for (dx = [-1, 1])
    for (dy = [-1, 1])
      translate([dx * hole_spacing_x / 2, dy * hole_spacing_y / 2, panel_t])
        difference() {
          cylinder(h = arduino_standoff_h, d = 6, $fn = 32);
          m3_clearance_hole(arduino_standoff_h + 2, 2.4);
        }
}

module electronics_bottom_panel() {
  difference() {
    rounded_rect_3d(e_bay_x, e_bay_y, panel_t, corner_r);
    perimeter_boss_grid(e_bay_x, e_bay_y, -eps, panel_t + 2, deck_rim);
    // USB / power edge toward +X outer
    translate([e_bay_x / 2 - deck_rim - 8, 0, -eps])
      cube([arduino_usb_slot_w, arduino_usb_slot_h + 6, panel_t + 2], center = false);
    // pump intake vents
    for (ix = [0 : pump_cols - 1])
      for (iy = [0 : pump_rows - 1])
        if (ix * pump_cols + iy < pump_count) {
          ox = (ix - (pump_cols - 1) / 2) * pump_col_pitch + pump_block_x0 + pump_axis_l / 2;
          oy = (iy - (pump_rows - 1) / 2) * pump_row_pitch + pump_block_y0;
          translate([ox, oy, -eps])
            cylinder(h = panel_t + 2, d = 10, $fn = 24);
        }
  }
  translate([arduino_pocket_x, arduino_pocket_y, 0])
    arduino_standoffs();
}

electronics_bottom_panel();

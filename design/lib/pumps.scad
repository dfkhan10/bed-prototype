include <../params.scad>

// 370 micro pump — axis +X, motor at -X, head/nozzle at +X, cradled from below

module pump_cradle_cut() {
  translate([-pump_axis_l / 2, 0, pump_cradle_z])
    rotate([0, 90, 0]) {
      // motor body
      cylinder(h = pump_axis_l - 8, d = pump_motor_d + slip_fit + 2, $fn = 48);
      // head pocket (slightly larger)
      translate([0, 0, 0])
        cylinder(h = pump_axis_l + 2, d = pump_head_d + slip_fit + 2, $fn = 48);
    }
  // nozzle pocket
  translate([pump_axis_l / 2 - 2, 0, pump_cradle_z + pump_head_d / 2])
    cylinder(h = pump_nozzle_h + 4, d = 8, center = true, $fn = 24);
}

module pump_cradle_solid() {
  wall = 2.5;
  translate([-pump_axis_l / 2 - wall, -pump_head_d / 2 - wall, pump_cradle_z - wall])
    cube([pump_axis_l + 2 * wall, pump_head_d + 2 * wall, wall]); // floor
  // retain clips at head
  for (dy = [-1, 1])
    translate([pump_axis_l / 2 - 6, dy * (pump_head_d / 2 + 1), pump_cradle_z])
      cube([8, 3, pump_head_d / 2 + 2], center = false);
}

module pump_at(ix, iy) {
  ox = (ix - (pump_cols - 1) / 2) * pump_col_pitch;
  oy = (iy - (pump_rows - 1) / 2) * pump_row_pitch + pump_block_y0;
  translate([ox, oy, 0])
    children();
}

module pump_block_cradles(mode = "cut") {
  for (ix = [0 : pump_cols - 1])
    for (iy = [0 : pump_rows - 1])
      if (ix * pump_cols + iy < pump_count)
        pump_at(ix, iy)
          if (mode == "cut")
            pump_cradle_cut();
          else
            pump_cradle_solid();
}

module wire_gutter_cut(depth = wire_gutter_d) {
  translate([pump_block_x0, pump_block_y0 - pump_row_pitch, pump_cradle_z])
    cube([pump_block_w, pump_block_h + pump_row_pitch * 2, depth], center = false);
}

// Export: deck_cell_section.stl — 3×3 cell deck with routing cavity
include <../lib/util.scad>

function cell_origin(i, j) = [
  (i - (grid_n - 1) / 2) * cell_pitch,
  (j - (grid_n - 1) / 2) * cell_pitch
];

module deck_solid_block(x, y) {
  rounded_rect_3d(x, y, deck_top_t + cavity_h, corner_r);
}

module single_cell_well(i, j) {
  pos = cell_origin(i, j);
  translate([pos[0], pos[1], deck_top_t]) {
    well_cut(well_open, cavity_h + eps);
    // one tube per cell: bottom-center of well → stem → channel to service (−Y)
    cell_underdeck_plumbing(pos[1], deck_cell_y);
  }
}

module rib_walls() {
  span = grid_span(grid_n, cell_pitch) + well_open;
  for (i = [0 : grid_n - 2]) {
    x = (i - (grid_n - 2) / 2) * cell_pitch;
    translate([x, 0, deck_top_t])
      cube([wall_t, span, cavity_h - channel_depth], center = true);
  }
  for (j = [0 : grid_n - 2]) {
    y = (j - (grid_n - 2) / 2) * cell_pitch;
    translate([0, y, deck_top_t])
      cube([span, wall_t, cavity_h - channel_depth], center = true);
  }
}

module clip_slots() {
  foot = service_foot_y(deck_cell_y);
  for (i = [0 : grid_n - 1]) {
    for (j = [0 : grid_n - 1]) {
      pos = cell_origin(i, j);
      run = cell_run_len(pos[1], deck_cell_y);
      for (k = [1 : 2]) {
        translate([
          pos[0] - 6,
          pos[1] - run * k / 3,
          deck_top_t - channel_depth - 0.5
        ])
          cube([12, 4, 2], center = false);
      }
    }
  }
  // service bulkhead: 3 columns × tube pass-through toward valves
  for (i = [0 : grid_n - 1]) {
    px = cell_origin(i, 0)[0];
    translate([px, foot + 6, deck_top_t - channel_depth / 2])
      cylinder(h = channel_depth + 2, d = port_d + 3, $fn = 24);
  }
}

module foot_joint() {
  // dowels + lap at -Y edge for service module
  y_foot = -deck_cell_y / 2 + deck_rim / 2;
  for (x = [-deck_cell_x / 4, deck_cell_x / 4]) {
    translate([x, y_foot, deck_top_t + cavity_h - dowel_depth])
      dowel_pin(dowel_depth);
  }
  translate([0, -deck_cell_y / 2 + deck_rim / 2, deck_top_t + cavity_h / 2])
    cube([deck_cell_x - deck_rim * 2, deck_rim, cavity_h], center = true);
}

module deck_cell_section() {
  difference() {
    union() {
      deck_solid_block(deck_cell_x, deck_cell_y);
      foot_joint();
      rib_walls();
    }
    for (i = [0 : grid_n - 1])
      for (j = [0 : grid_n - 1])
        single_cell_well(i, j);
    clip_slots();
    // lighten cavity
    translate([0, 0, deck_top_t + 2])
      rounded_rect_3d(deck_cell_x - deck_rim * 2.5, deck_cell_y - deck_rim * 2.5, cavity_h - 4, corner_r - 2);
    // lap screw holes at foot
    for (x = [-deck_cell_x / 3, deck_cell_x / 3])
      translate([x, -deck_cell_y / 2 + deck_rim / 2, -eps])
        cylinder(h = deck_top_t + cavity_h + 2, d = lap_joint_screw_d, $fn = 24);
  }
}

deck_cell_section();

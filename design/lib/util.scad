include <../params.scad>

module rounded_rect_xy(x, y, r) {
  r2 = min(r, x / 2 - eps, y / 2 - eps);
  minkowski() {
    square([x - 2 * r2, y - 2 * r2], center = true);
    circle(r = r2, $fn = 48);
  }
}

module rounded_rect_3d(x, y, z, r) {
  linear_extrude(height = z, center = false, convexity = 4)
    rounded_rect_xy(x, y, r);
}

module well_cut(open_size, depth) {
  linear_extrude(height = depth + eps)
    rounded_rect_xy(open_size, open_size, corner_r - 1);
}

module port_hole(d = port_d) {
  cylinder(h = deck_top_t + cavity_h + panel_t + 2, d = d, center = false, $fn = 32);
}

// Bottom-center of cell well: through 4 mm floor into routing cavity (hidden from top).
module cell_bottom_port() {
  translate([0, 0, -eps])
    cylinder(h = deck_top_t + eps, d = port_d, $fn = 32);
}

module cell_stem_pocket(h = stem_pocket_h, d = stem_pocket_d) {
  translate([0, 0, -deck_top_t])
    cylinder(h = h, d = d, $fn = 32);
}

// Horizontal groove under deck (−Y toward service bay), centered on cell X.
module cell_run_to_service(run_len) {
  if (run_len > 2)
    translate([0, -run_len / 2, -deck_top_t - channel_depth / 2])
      cube([channel_w, run_len, channel_depth], center = true);
}

function service_foot_y(deck_y) = -deck_y / 2 + deck_rim;

function cell_run_len(cell_y, deck_y) = cell_y - service_foot_y(deck_y);

module cell_underdeck_plumbing(cell_y, deck_y) {
  cell_bottom_port();
  cell_stem_pocket();
  cell_run_to_service(cell_run_len(cell_y, deck_y));
}

module dowel_hole(depth = dowel_depth) {
  cylinder(h = depth + eps, d = dowel_d + slip_fit, $fn = 32);
}

module dowel_pin(h = dowel_depth) {
  cylinder(h = h, d = dowel_d - 0.05, $fn = 32);
}

// Route from cell center toward service bay (-Y direction)
module tube_channel(length, w = channel_w, d = channel_depth) {
  translate([0, -length / 2, -d])
    cube([w, length, d], center = true);
}

module tube_clip_body() {
  clip_w = 12;
  clip_h = channel_depth + 4;
  difference() {
    rounded_rect_3d(clip_w, clip_w, clip_h, 2);
    translate([0, 0, 2])
      cylinder(h = clip_h, d = tube_clip_id, $fn = 32);
    // snap slot
    translate([clip_w / 2 - 1, 0, clip_h / 2])
      cube([2, clip_w, clip_h], center = true);
  }
}

include <../params.scad>

// M3 screw housing — shared across split plates

module m3_clearance_hole(h, d = panel_screw_d) {
  translate([0, 0, -eps])
    cylinder(h = h + 2 * eps, d = d, $fn = 20);
}

module m3_boss(od, h, hole_d = panel_screw_d) {
  difference() {
    cylinder(h = h, d = od, $fn = 32);
    m3_clearance_hole(h + 2, hole_d);
  }
}

// Heat-set insert pocket (M3, optional)
module m3_insert_pocket(h = 4.5) {
  translate([0, 0, -eps])
    cylinder(h = h + eps, d = 4.2, $fn = 24); // ~M3 brass insert
}

// Perimeter screw grid on rectangular plate
module perimeter_boss_grid(x, y, z_base, boss_h, inset = deck_rim) {
  nx = max(2, floor((x - 2 * inset) / flange_screw_pitch));
  ny = max(2, floor((y - 2 * inset) / flange_screw_pitch));
  for (i = [0 : nx])
    for (j = [0 : ny]) {
      if (i == 0 || i == nx || j == 0 || j == ny) {
        px = -x / 2 + inset + i * (x - 2 * inset) / nx;
        py = -y / 2 + inset + j * (y - 2 * inset) / ny;
        translate([px, py, z_base])
          m3_boss(boss_od, boss_h);
      }
    }
}

// Split flange: two half-plates mate at x = 0 (local coords), extra thickness at seam
module split_flange_seam(seam_y, length_y, t = split_flange_t) {
  translate([-split_flange_t / 2, -length_y / 2, 0])
    cube([split_flange_t, length_y, t]);
}

module split_flange_holes_z(z, length_y, count = 3) {
  for (k = [0 : count - 1]) {
    y = -length_y / 2 + (k + 1) * length_y / (count + 1);
    translate([0, y, -eps])
      m3_clearance_hole(z + 2);
  }
}

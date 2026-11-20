// Export: cell_cassette.stl — print ×9, PETG, top surface down for smooth seat
include <../lib/util.scad>

module cell_cassette() {
  outer = flange_seat;
  inner = well_open - 4;
  wall = (outer - inner) / 2;

  difference() {
    union() {
      rounded_rect_3d(outer, outer, cassette_h, corner_r - 2);
      // clamp lip
      translate([0, 0, cassette_h - 2])
        rounded_rect_3d(outer + 2, outer + 2, 2, corner_r);
    }
    // bladder pocket
    translate([0, 0, 3])
      well_cut(inner, cassette_h + eps);
    // bottom-center barb (mates with deck port; not visible from top)
    translate([0, 0, -eps])
      cylinder(h = wall + 4, d = port_d, $fn = 32);
    // label notch
    translate([outer / 2 - 6, -outer / 2 + 4, cassette_h - 4])
      cube([12, 8, 4], center = false);
  }
}

cell_cassette();

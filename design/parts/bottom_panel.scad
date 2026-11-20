// Export: bottom_panel.stl — closes cavity; mount Arduino on cavity-facing side
include <../lib/util.scad>

module arduino_standoffs() {
  hole_spacing_x = 61;
  hole_spacing_y = 46;
  for (dx = [-1, 1])
    for (dy = [-1, 1])
      translate([dx * hole_spacing_x / 2, dy * hole_spacing_y / 2, panel_t])
        difference() {
          cylinder(h = arduino_standoff_h, d = 6, $fn = 32);
          translate([0, 0, -eps])
            cylinder(h = arduino_standoff_h + 2, d = 2.4, $fn = 16); // M2.5 tap optional
        }
}

module bottom_panel_outline(x, y) {
  rounded_rect_3d(x, y, panel_t, corner_r);
}

module perimeter_screws(x, y) {
  nx = max(2, floor(x / panel_screw_pitch));
  ny = max(2, floor(y / panel_screw_pitch));
  for (i = [0 : nx])
    for (j = [0 : ny]) {
      if (i == 0 || i == nx || j == 0 || j == ny) {
        px = -x / 2 + deck_rim + i * (x - 2 * deck_rim) / nx;
        py = -y / 2 + deck_rim + j * (y - 2 * deck_rim) / ny;
        translate([px, py, -eps])
          cylinder(h = panel_t + 2, d = panel_screw_d, $fn = 20);
      }
    }
}

module bottom_panel_full() {
  total_x = deck_cell_x;
  total_y = deck_cell_y + deck_service_y - deck_rim; // overlap lap

  difference() {
    bottom_panel_outline(total_x, total_y);
    perimeter_screws(total_x, total_y);
    // USB access
    translate([-total_x / 2 + deck_rim + 10, 0, -eps])
      cube([arduino_usb_slot_w, arduino_usb_slot_h, panel_t + 2], center = false);
    // vent holes for pumps (foot)
    for (x = [-30, 0, 30])
      translate([x, -total_y / 2 + 25, -eps])
        cylinder(h = panel_t + 2, d = 8, $fn = 24);
    // wire pass-through to deck
    translate([total_x / 2 - 20, total_y / 4, -eps])
      cylinder(h = panel_t + 2, d = 12, $fn = 32);
  }
  // standoffs on top face (inside cavity when panel mounted)
  translate([total_x / 2 - deck_rim - arduino_l / 2 - 8, total_y / 2 - deck_rim - arduino_w / 2 - 8, 0])
    arduino_standoffs();
}

bottom_panel_full();

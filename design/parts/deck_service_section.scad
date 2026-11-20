// Export: deck_service_section.stl — solid deck + valve pockets; sits on electronics_bay_rim
include <../lib/util.scad>
include <../lib/joints.scad>

module valve_slot(idx, cols = 5) {
  col = idx % cols;
  row = floor(idx / cols);
  pitch_x = valve_w + 6;
  pitch_y = valve_l + 8;
  ox = (col - (cols - 1) / 2) * pitch_x;
  oy = deck_service_y / 2 - deck_rim - 25 - row * pitch_y;
  translate([ox, oy, deck_top_t])
    cube([valve_w + 2, valve_l + 2, min(valve_h, e_bay_cavity_h - 6)], center = false);
}

module head_joint() {
  y = deck_service_y / 2 - deck_rim / 2;
  difference() {
    translate([0, y, 0])
      rounded_rect_3d(deck_service_x, deck_rim, deck_top_t + cavity_h, corner_r);
    for (x = [-deck_service_x / 4, deck_service_x / 4])
      translate([x, y, deck_top_t + cavity_h - dowel_depth])
        dowel_hole();
    for (x = [-deck_service_x / 3, deck_service_x / 3])
      translate([x, y - deck_rim / 2, -eps])
        cylinder(h = deck_top_t + cavity_h + 2, d = lap_joint_screw_d, $fn = 24);
  }
}

module deck_service_section() {
  total_h = deck_top_t + e_bay_cavity_h + e_bay_rim_h + e_bay_tray_t;

  difference() {
    union() {
      rounded_rect_3d(deck_service_x, deck_service_y, total_h, corner_r);
      head_joint();
      // electronics bay enclosure walls (aligned to e_bay_x)
      translate([0, 0, deck_top_t])
        difference() {
          rounded_rect_3d(e_bay_x + 4, e_bay_y + 4, e_bay_cavity_h + e_bay_rim_h + e_bay_tray_t, corner_r);
          translate([0, 0, e_bay_rim_h])
            rounded_rect_3d(e_bay_x, e_bay_y, e_bay_cavity_h + e_bay_tray_t + eps, corner_r - 1);
        }
    }
    // cavity for pumps + Arduino (closed by bottom panel)
    translate([0, 0, deck_top_t + e_bay_rim_h])
      rounded_rect_3d(e_bay_x, e_bay_y, e_bay_cavity_h + e_bay_tray_t + eps, corner_r - 1);
    // valve pockets under solid deck (forward / toward cells)
    for (v = [0 : min(valve_count, 9) - 1])
      valve_slot(v);
    // bolt rim to service deck
    translate([0, 0, deck_top_t + e_bay_rim_h + e_bay_tray_t - eps])
      perimeter_boss_grid(e_bay_x, e_bay_y, 0, 12, deck_rim);
    // supply channel toward cells
    translate([0, deck_service_y / 2 - 18, deck_top_t + total_h - channel_depth - 2])
      cube([deck_service_x - 40, 14, channel_depth + 2], center = true);
  }
}

deck_service_section();

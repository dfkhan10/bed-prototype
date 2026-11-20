// Layout preview — not for printing as one STL.
// Export each part from its file in design/parts/
include <../params.scad>
use <../parts/deck_cell_section.scad>
use <../parts/deck_service_section.scad>
use <../parts/bottom_panel.scad>
use <../parts/cell_cassette.scad>

$fn = 48;

module layout_preview() {
  color("SteelBlue", 0.9)
    deck_cell_section();
  translate([0, -deck_cell_y / 2 - deck_service_y / 2 + deck_rim, 0])
    color("CornflowerBlue", 0.9)
      deck_service_section();
  translate([0, 0, -panel_t - 2])
    color("DimGray", 0.85)
      bottom_panel_full();
  // ghost cassettes in center cell only (i=1,j=1)
  for (i = [0 : grid_n - 1])
    for (j = [0 : grid_n - 1]) {
      pos = [
        (i - (grid_n - 1) / 2) * cell_pitch,
        (j - (grid_n - 1) / 2) * cell_pitch,
        deck_top_t + cavity_h
      ];
      translate(pos)
        color("LightSalmon", 0.5)
          cell_cassette();
    }
}

layout_preview();

// Sanity check — echo to console
echo(str("Cell deck footprint: ", deck_cell_x, " x ", deck_cell_y, " mm"));
echo(str("Service module: ", deck_service_x, " x ", deck_service_y, " mm"));
echo(str("Fits P2S if each part <= ", print_limit, " mm"));

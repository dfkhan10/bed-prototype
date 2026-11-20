// Bed prototype — master print file (Bambu P2S)
// Open in OpenSCAD → F5 preview / F6 render → File → Export STL
//
// part = "preview"     full assembly (not for printing)
// part = "deck_cell"   3×3 cell deck
// part = "deck_service" service deck + valve pockets
// part = "e_tray"      electronics bay tray (pumps)
// part = "e_rim"       electronics bay rim
// part = "e_bottom"    Arduino bottom panel (electronics bay only)
// part = "cassette"    one cell cassette (print ×9)
// part = "tube_clip"   tube clip (print ~24)
// part = "deck_single" stage-1 single cell deck

part = "preview";

include <../params.scad>
use <../parts/deck_cell_section.scad>
use <../parts/deck_service_section.scad>
use <../parts/electronics_bay_tray.scad>
use <../parts/electronics_bay_rim.scad>
use <../parts/electronics_bottom_panel.scad>
use <../parts/cell_cassette.scad>
use <../parts/deck_single_cell.scad>
include <../lib/util.scad>

$fn = 48;

module assembly_preview() {
  color("SteelBlue", 0.92)
    deck_cell_section();
  translate([0, -deck_cell_y / 2 - deck_service_y / 2 + deck_rim, 0])
    color("CornflowerBlue", 0.9)
      deck_service_section();
  // electronics screw stack under service bay (local to service center)
  translate([0, -deck_cell_y / 2 - deck_service_y / 2 + deck_rim, 0]) {
    z0 = deck_top_t + e_bay_rim_h + e_bay_tray_t;
    color("DarkGray", 0.85)
      translate([0, 0, z0])
        electronics_bay_rim();
    color("Gray", 0.85)
      electronics_bay_tray("full");
    color("DimGray", 0.9)
      translate([0, 0, -panel_t])
        electronics_bottom_panel();
  }
  for (i = [0 : grid_n - 1])
    for (j = [0 : grid_n - 1]) {
      pos = [
        (i - (grid_n - 1) / 2) * cell_pitch,
        (j - (grid_n - 1) / 2) * cell_pitch,
        deck_top_t + cavity_h
      ];
      translate(pos)
        color("LightSalmon", 0.45)
          cell_cassette();
    }
}

if (part == "preview") {
  assembly_preview();
} else if (part == "deck_cell") {
  deck_cell_section();
} else if (part == "deck_service") {
  deck_service_section();
} else if (part == "e_tray") {
  electronics_bay_tray("full");
} else if (part == "e_rim") {
  electronics_bay_rim();
} else if (part == "e_bottom") {
  electronics_bottom_panel();
} else if (part == "cassette") {
  cell_cassette();
} else if (part == "tube_clip") {
  tube_clip_body();
} else if (part == "deck_single") {
  deck_single_cell();
} else {
  echo("Unknown part — set part to preview|deck_cell|deck_service|e_tray|e_rim|e_bottom|cassette|tube_clip|deck_single");
}

echo(str("Active part: ", part));
echo(str("P2S limit per plate: ", print_limit, " mm"));

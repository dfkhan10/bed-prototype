// LEGACY OpenSCAD — not maintained. Edit design/bed_params.json + Fusion builder instead.

// --- Printer envelope (Bambu P2S) ---
build_max = 256;
print_margin = 4;
print_limit = build_max - print_margin;

// --- Cell grid ---
grid_n = 3;
cell_pitch = 76;
wall_t = 3;
well_open = 58;
flange_seat = 64;
cassette_h = 18;
port_d = 6.5;

// --- Deck structure ---
deck_top_t = 4;
cavity_h = 32; // tube routing under cell deck (not electronics bay)
deck_rim = 8;
corner_r = 6;

// --- 370 micro pump (Taobao kit / photo vs Arduino; see docs/HARDWARE_DIMENSIONS.md) ---
pump_motor_d = 24.5;
pump_head_d = 31;
pump_axis_l = 68;
pump_nozzle_h = 8;
pump_port_od = 4.2;
pump_wire_tail = 35;
pump_count = 8; // set 6–8; layout skips extras above pump_count
pump_rows = 2;
pump_cols = 4;
pump_col_pitch = 36; // center distance along X
pump_row_pitch = 38; // center distance along Y
pump_cradle_z = 2; // floor of cradle above tray surface

// --- Solenoid (kit) ---
valve_l = 22;
valve_w = 12;
valve_h = 30;
valve_count = grid_n * grid_n;

// --- Arduino Uno + sensor shield (kit photo) ---
ctrl_board_l = 69;
ctrl_board_w = 54;
arduino_l = ctrl_board_l;
arduino_w = ctrl_board_w;
arduino_stack_h = 28;
arduino_standoff_h = 6;
arduino_usb_slot_w = 14;
arduino_usb_slot_h = 8;

// --- Closed electronics bay (pumps + Arduino, under service deck) ---
e_bay_x = 200;
e_bay_y = 128;
e_bay_cavity_h = 52;
e_bay_split_x = 100; // optional left/right print split at this X (local)
e_bay_tray_t = 4;
e_bay_rim_h = 8;

// Pump block placement inside bay (local coords, center = origin)
pump_block_w = (pump_cols - 1) * pump_col_pitch + pump_axis_l;
pump_block_h = (pump_rows - 1) * pump_row_pitch + pump_head_d;
pump_block_x0 = -pump_block_w / 2 - 8;
pump_block_y0 = -8;
arduino_pocket_x = e_bay_x / 2 - deck_rim - ctrl_board_l / 2 - 6;
arduino_pocket_y = -e_bay_y / 2 + deck_rim + ctrl_board_w / 2 + 6;

wire_gutter_d = 10;

// --- Service module (solid deck above electronics bay) ---
service_len = e_bay_y + deck_rim * 2;
service_deck_solid = true;

// --- Bottom / screw housing ---
panel_t = 4;
panel_screw_d = 3.4;
panel_screw_pitch = 35;
flange_screw_pitch = 40;
boss_od = 8;
split_flange_t = 10;

// --- Tube routing (cell deck) ---
// Each cell: one tube at bottom-center of well (not visible from top).
tube_od = 6;
tube_clip_id = tube_od + 0.6;
channel_w = tube_od + 4;
channel_depth = 8;
stem_pocket_d = channel_w; // barb + bend relief under well floor
stem_pocket_h = channel_depth + 4;

// --- Joint between deck sections ---
dowel_d = 5;
dowel_depth = 10;
lap_joint_screw_d = 3.4;

slip_fit = 0.25;
eps = 0.01;

function grid_span(n, pitch) = (n - 1) * pitch;
grid_xy = grid_span(grid_n, cell_pitch) + well_open + deck_rim * 2;
deck_cell_x = grid_xy;
deck_cell_y = grid_xy;
deck_service_x = max(deck_cell_x, e_bay_x + deck_rim * 2);
deck_service_y = service_len;

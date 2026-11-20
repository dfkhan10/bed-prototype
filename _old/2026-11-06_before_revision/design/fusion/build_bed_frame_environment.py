# Bed prototype — single Fusion master builder (Design / Solid).
# Params: design/bed_params.json — edit dimensions there only.
# Run: Scripts and Add-Ins, or Fusion MCP → save bed frame / BedPrototype_Frame_v1.f3d
# Print: export bodies / components as STL from Fusion (Bambu P2S).

import json
import os
import sys

import adsk.core, adsk.fusion


def _load_params():
    paths = []
    try:
        script_dir = os.path.dirname(os.path.realpath(__file__))
        paths.append(os.path.normpath(os.path.join(script_dir, "..", "bed_params.json")))
    except NameError:
        pass
    paths.append(
        os.path.normpath(
            "/Users/ivanyalov/Desktop/Bed prototype/design/bed_params.json"
        )
    )
    for path in paths:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError("bed_params.json not found — edit design/bed_params.json")


def mm(v):
    return v / 10.0


def clear_design(design):
    root = design.rootComponent
    t = design.timeline
    while t.count > 0:
        t.item(t.count - 1).deleteObject()
    for i in range(root.sketches.count - 1, -1, -1):
        root.sketches.item(i).deleteObject()
    for i in range(root.constructionPlanes.count - 1, -1, -1):
        p = root.constructionPlanes.item(i)
        if p.name.startswith("BedFrame_"):
            try:
                p.deleteObject()
            except RuntimeError:
                pass


def rect_sketch(root, plane, cx, cy, hx, hy, name):
    sk = root.sketches.add(plane)
    sk.name = name
    sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(mm(cx - hx), mm(cy - hy), 0),
        adsk.core.Point3D.create(mm(cx + hx), mm(cy + hy), 0),
    )
    return sk


def offset_plane(root, planes, base, dz_mm, name):
    inp = planes.createInput()
    inp.setByOffset(base, adsk.core.ValueInput.createByReal(mm(dz_mm)))
    pl = planes.add(inp)
    pl.name = name
    return pl


def cut_down(extrudes, profile, depth_mm, name):
    cut_in = extrudes.createInput(profile, adsk.fusion.FeatureOperations.CutFeatureOperation)
    cut_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(-abs(depth_mm))))
    feat = extrudes.add(cut_in)
    feat.name = name
    return feat


def _fastener(p):
    return p.get(
        "fasteners",
        {
            "clearance_d": 2.7,
            "boss_od": 5.5,
            "boss_h": 6,
            "pilot_d": 2.1,
            "perimeter_pitch": 28,
            "perimeter_inset": 10,
            "joint_screw_count": 4,
        },
    )


def perimeter_boss_points(hx, hy):
    return [
        (-hx, -hy),
        (0, -hy),
        (hx, -hy),
        (-hx, 0),
        (hx, 0),
        (-hx, hy),
        (0, hy),
        (hx, hy),
    ]


def joint_screw_x_positions(span_x, count):
    if count <= 2:
        return [-span_x / 4, span_x / 4]
    inset = span_x * 0.2
    usable = span_x / 2 - inset
    step = (2 * usable) / (count - 1)
    return [-usable + i * step for i in range(count)]


def valve_center(idx, p, service_cy, service_y):
    cols = p["valve_cols"]
    col = idx % cols
    row = idx // cols
    pitch_x = p["valve_w"] + 6
    pitch_y = p["valve_l"] + 8
    ox = (col - (cols - 1) / 2.0) * pitch_x
    oy = service_cy + service_y / 2 - p["deck_rim"] - 25 - row * pitch_y
    return ox, oy


def run(_context: str):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        raise RuntimeError("Open a Design document (not Manufacture/Drawing).")

    ws = ui.workspaces.itemById("FusionSolidEnvironment")
    if ws:
        ws.activate()

    p = _load_params()
    gn_x = p.get("grid_n_x", p.get("grid_n", 3))
    gn_y = p.get("grid_n_y", p.get("grid_n", 3))
    cell_count = gn_x * gn_y
    pitch = p["cell_pitch"]
    seat_depth = p.get("cell_seat_depth", 8)
    floor_t = p.get("cell_floor_t", 2)
    well_cut_depth = max(1.0, seat_depth - floor_t)

    deck_x = (gn_x - 1) * pitch + p["well_open"] + 2 * p["deck_rim"]
    deck_y = (gn_y - 1) * pitch + p["well_open"] + 2 * p["deck_rim"]
    deck_stack = p["deck_top_t"] + p["cavity_h"]
    channel_w = p["channel_w"]
    stem_h = p.get("stem_pocket_h", p["channel_depth"] + 4)

    service_y = p["e_bay_y"] + 2 * p["deck_rim"]
    service_x = max(deck_x, p["e_bay_x"] + 2 * p["deck_rim"])
    service_cy = -deck_y / 2.0 - service_y / 2.0 + p["deck_rim"]
    foot_y = -deck_y / 2.0 + p["deck_rim"]
    mate_y = -deck_y / 2.0 + p["deck_rim"] / 2.0
    cell_floor_z = deck_stack - seat_depth
    f = _fastener(p)
    screw_d = f.get("clearance_d", 2.7)
    boss_od = f.get("boss_od", 5.5)
    boss_h = f.get("boss_h", 6)
    pilot_d = f.get("pilot_d", 2.1)
    joint_n = int(f.get("joint_screw_count", 4))
    joint_span = min(deck_x, service_x) - 2 * p["deck_rim"]
    joint_xs = joint_screw_x_positions(joint_span, joint_n)

    clear_design(design)
    root = design.rootComponent
    xy = root.xYConstructionPlane
    extrudes = root.features.extrudeFeatures
    planes = root.constructionPlanes

    # === A) Cell deck ===
    sk_cell = rect_sketch(root, xy, 0, 0, deck_x / 2, deck_y / 2, "BedFrame_CellDeckSketch")
    cell_in = extrudes.createInput(
        sk_cell.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    cell_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(deck_stack)))
    cell_feat = extrudes.add(cell_in)
    cell_feat.name = "BedFrame_CellDeckExtrude"
    cell_feat.bodies.item(0).name = "BedFrame_CellDeck"

    deck_top_plane = offset_plane(root, planes, xy, deck_stack, "BedFrame_DeckTop")
    cell_floor_plane = offset_plane(root, planes, xy, cell_floor_z, "BedFrame_CellFloor")
    route_plane = offset_plane(root, planes, xy, p["deck_top_t"], "BedFrame_RoutePlane")

    for ix in range(gn_x):
        for iy in range(gn_y):
            cx = (ix - (gn_x - 1) / 2.0) * pitch
            cy = (iy - (gn_y - 1) / 2.0) * pitch
            sk_w = rect_sketch(
                root, deck_top_plane, cx, cy, p["well_open"] / 2, p["well_open"] / 2, f"BedFrame_Well_{ix}_{iy}"
            )
            cut_down(extrudes, sk_w.profiles.item(0), well_cut_depth + 0.5, f"BedFrame_WellCut_{ix}_{iy}")

            sk_p = root.sketches.add(cell_floor_plane)
            sk_p.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(mm(cx), mm(cy), 0), mm(p["port_d"] / 2)
            )
            cut_down(extrudes, sk_p.profiles.item(0), floor_t + 2, f"BedFrame_Port_{ix}_{iy}")

            sk_stem = root.sketches.add(cell_floor_plane)
            sk_stem.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(mm(cx), mm(cy), 0), mm(channel_w / 2)
            )
            cut_down(extrudes, sk_stem.profiles.item(0), floor_t + stem_h, f"BedFrame_Stem_{ix}_{iy}")

            run_len = max(2.0, cy - foot_y)
            sk_c = rect_sketch(
                root,
                route_plane,
                cx,
                cy - run_len / 2.0,
                channel_w / 2,
                run_len / 2,
                f"BedFrame_Run_{ix}_{iy}",
            )
            cut_down(
                extrudes, sk_c.profiles.item(0), p["deck_top_t"] + p["channel_depth"], f"BedFrame_RunCut_{ix}_{iy}"
            )

            for k in (1, 2):
                slot_y = cy - run_len * k / 3.0
                sk_cl = rect_sketch(root, route_plane, cx - 6, slot_y, 6, 2, f"BedFrame_Clip_{ix}_{iy}_{k}")
                cut_down(
                    extrudes, sk_cl.profiles.item(0), p["deck_top_t"] + p["channel_depth"] + 1, f"BedFrame_ClipSlot_{ix}_{iy}_{k}"
                )

    rib_span_x = (gn_x - 1) * pitch + p["well_open"]
    rib_span_y = (gn_y - 1) * pitch + p["well_open"]
    rib_z = p["deck_top_t"] + (p["cavity_h"] - p["channel_depth"]) / 2.0
    rib_plane = offset_plane(root, planes, xy, rib_z, "BedFrame_RibPlane")
    for i in range(gn_x - 1):
        rx = (i - (gn_x - 2) / 2.0) * pitch
        sk_rx = rect_sketch(root, rib_plane, rx, 0, p["wall_t"] / 2, rib_span_y / 2, f"BedFrame_RibX_{i}")
        rx_in = extrudes.createInput(
            sk_rx.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        rx_in.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(mm(p["cavity_h"] - p["channel_depth"]))
        )
        extrudes.add(rx_in).name = f"BedFrame_RibX_{i}"
    for j in range(gn_y - 1):
        ry = (j - (gn_y - 2) / 2.0) * pitch
        sk_ry = rect_sketch(root, rib_plane, 0, ry, rib_span_x / 2, p["wall_t"] / 2, f"BedFrame_RibY_{j}")
        ry_in = extrudes.createInput(
            sk_ry.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        ry_in.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(mm(p["cavity_h"] - p["channel_depth"]))
        )
        extrudes.add(ry_in).name = f"BedFrame_RibY_{j}"

    for j, dx in enumerate(joint_xs):
        sk_l = root.sketches.add(deck_top_plane)
        sk_l.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(dx), mm(mate_y), 0), mm(screw_d / 2)
        )
        cut_down(extrudes, sk_l.profiles.item(0), deck_stack + 2, f"BedFrame_JointScrewCell_{j}")

    # === B) Service deck (coplanar top) ===
    sk_svc = rect_sketch(
        root, xy, 0, service_cy, service_x / 2, service_y / 2, "BedFrame_ServiceCapSketch"
    )
    svc_in = extrudes.createInput(
        sk_svc.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    svc_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(deck_stack)))
    svc_feat = extrudes.add(svc_in)
    svc_feat.name = "BedFrame_ServiceCap"
    svc_feat.bodies.item(0).name = "BedFrame_ServiceDeck"

    valve_cut_h = min(p["valve_h"], p["cavity_h"] - 6)
    for v in range(cell_count):
        vx, vy = valve_center(v, p, service_cy, service_y)
        sk_v = rect_sketch(
            root,
            deck_top_plane,
            vx,
            vy,
            (p["valve_w"] + 2) / 2,
            (p["valve_l"] + 2) / 2,
            f"BedFrame_Valve_{v}",
        )
        cut_down(extrudes, sk_v.profiles.item(0), valve_cut_h + 1, f"BedFrame_ValvePocket_{v}")

    for v in range(cell_count):
        vx, vy = valve_center(v, p, service_cy, service_y)
        stub_len = max(8.0, vy - foot_y)
        sk_vs = rect_sketch(
            root,
            route_plane,
            vx,
            vy - stub_len / 2,
            channel_w / 2,
            stub_len / 2,
            f"BedFrame_ValveRun_{v}",
        )
        cut_down(
            extrudes, sk_vs.profiles.item(0), p["deck_top_t"] + p["channel_depth"], f"BedFrame_ValveRunCut_{v}"
        )

    for j, dx in enumerate(joint_xs):
        sk_ls = root.sketches.add(deck_top_plane)
        sk_ls.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(dx), mm(mate_y), 0), mm(screw_d / 2)
        )
        cut_down(extrudes, sk_ls.profiles.item(0), deck_stack + 2, f"BedFrame_JointScrewService_{j}")

    # === C) Electronics bay (under service) ===
    bay_h = p["e_bay_rim_h"] + p["e_bay_cavity_h"] + p["e_bay_tray_t"]
    bay_bottom = offset_plane(root, planes, xy, -bay_h, "BedFrame_EBayBottom")

    sk_bay = rect_sketch(
        root,
        bay_bottom,
        0,
        service_cy,
        p["e_bay_x"] / 2 + 2,
        p["e_bay_y"] / 2 + 2,
        "BedFrame_EBayShellSketch",
    )
    bay_in = extrudes.createInput(
        sk_bay.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    bay_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(bay_h)))
    bay_feat = extrudes.add(bay_in)
    bay_feat.name = "BedFrame_EBayShell"
    bay_feat.bodies.item(0).name = "BedFrame_ElectronicsBay"

    sk_bay_void = rect_sketch(
        root, bay_bottom, 0, service_cy, p["e_bay_x"] / 2, p["e_bay_y"] / 2, "BedFrame_EBayVoidSketch"
    )
    void_in = extrudes.createInput(
        sk_bay_void.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
    )
    void_in.setDistanceExtent(
        False, adsk.core.ValueInput.createByReal(mm(p["e_bay_cavity_h"] + p["e_bay_tray_t"] + 1))
    )
    extrudes.add(void_in).name = "BedFrame_EBayVoid"

    sk_floor = rect_sketch(
        root, bay_bottom, 0, service_cy, p["e_bay_x"] / 2, p["e_bay_y"] / 2, "BedFrame_EBayFloorSketch"
    )
    floor_in = extrudes.createInput(
        sk_floor.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    floor_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(p["panel_t"])))
    extrudes.add(floor_in).name = "BedFrame_EBayFloor"

    idx = 0
    for iy in range(p["pump_rows"]):
        for ix in range(p["pump_cols"]):
            if idx >= p["pump_count"]:
                break
            cx = (ix - (p["pump_cols"] - 1) / 2.0) * p["pump_col_pitch"] - 8
            cy = (iy - (p["pump_rows"] - 1) / 2.0) * p["pump_row_pitch"] - 8 + service_cy
            sk_pp = rect_sketch(
                root,
                bay_bottom,
                cx,
                cy,
                p["pump_axis_l"] / 2,
                p["pump_head_d"] / 2,
                f"BedFrame_Pump_{idx}",
            )
            pp_in = extrudes.createInput(
                sk_pp.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            pp_in.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(mm(p["panel_t"] + p["pump_head_d"]))
            )
            extrudes.add(pp_in).name = f"BedFrame_PumpPocket_{idx}"
            idx += 1

    inset = 8.0
    hx = p["e_bay_x"] / 2 - inset
    hy = p["e_bay_y"] / 2 - inset
    for i, (bx, by) in enumerate(
        [
            (-hx, -hy),
            (0, -hy),
            (hx, -hy),
            (-hx, 0),
            (hx, 0),
            (-hx, hy),
            (0, hy),
            (hx, hy),
        ]
    ):
        sk_b = root.sketches.add(bay_bottom)
        sk_b.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(bx), mm(by + service_cy), 0), mm(boss_od / 2)
        )
        bj = extrudes.createInput(
            sk_b.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        bj.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(boss_h)))
        extrudes.add(bj).name = f"BedFrame_ScrewBoss_{i}"
        sk_bh = root.sketches.add(bay_bottom)
        sk_bh.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(bx), mm(by + service_cy), 0), mm(pilot_d / 2)
        )
        bh = extrudes.createInput(
            sk_bh.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        bh.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(mm(boss_h + p["panel_t"] + 2))
        )
        extrudes.add(bh).name = f"BedFrame_ScrewPilot_{i}"

    ax = p["e_bay_x"] / 2 - inset - p["arduino_l"] / 2 - 6
    ay = -p["e_bay_y"] / 2 + inset + p["arduino_w"] / 2 + 6
    for dx in (-1, 1):
        for dy in (-1, 1):
            sx = ax + dx * 30.5
            sy = ay + dy * 23.0 + service_cy
            sk_s = root.sketches.add(bay_bottom)
            sk_s.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(mm(sx), mm(sy), 0), mm(3)
            )
            sj = extrudes.createInput(
                sk_s.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            sj.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(p["arduino_standoff_h"])))
            extrudes.add(sj).name = "BedFrame_ArduinoStandoff"
            sk_sh = root.sketches.add(bay_bottom)
            sk_sh.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(mm(sx), mm(sy), 0), mm(1.25)
            )
            sh = extrudes.createInput(
                sk_sh.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            sh.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(mm(p["arduino_standoff_h"] + p["panel_t"]))
            )
            extrudes.add(sh).name = "BedFrame_StandoffHole"

    for sx in (-60.0, 0.0, 60.0):
        sk_t = root.sketches.add(bay_bottom)
        sk_t.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(sx), mm(service_cy + p["e_bay_y"] / 2 - 2), 0),
            mm(5.0),
        )
        t_in = extrudes.createInput(
            sk_t.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        t_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(bay_h + deck_stack + 2)))
        extrudes.add(t_in).name = "BedFrame_TubePassThrough"

    panel_z = -bay_h - p["panel_t"]
    panel_bottom = offset_plane(root, planes, xy, panel_z, "BedFrame_PanelBottom")
    sk_panel = rect_sketch(
        root,
        panel_bottom,
        0,
        service_cy,
        p["e_bay_x"] / 2 + p["deck_rim"],
        p["e_bay_y"] / 2 + p["deck_rim"],
        "BedFrame_BottomPanelSketch",
    )
    panel_in = extrudes.createInput(
        sk_panel.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    panel_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(p["panel_t"])))
    panel_feat = extrudes.add(panel_in)
    panel_feat.name = "BedFrame_BottomPanelExtrude"
    panel_feat.bodies.item(0).name = "BedFrame_BottomPanel"

    pinset = f.get("perimeter_inset", 10)
    hx_p = p["e_bay_x"] / 2 - pinset
    hy_p = p["e_bay_y"] / 2 - pinset
    for pi, (bx, by) in enumerate(perimeter_boss_points(hx_p, hy_p)):
        sk_pb = root.sketches.add(panel_bottom)
        sk_pb.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(bx), mm(by + service_cy), 0), mm(boss_od / 2)
        )
        pj = extrudes.createInput(
            sk_pb.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        pj.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(boss_h)))
        extrudes.add(pj).name = f"BedFrame_PanelBoss_{pi}"
        sk_ph = root.sketches.add(panel_bottom)
        sk_ph.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(bx), mm(by + service_cy), 0), mm(screw_d / 2)
        )
        ph = extrudes.createInput(
            sk_ph.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        ph.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(boss_h + p["panel_t"] + 2)))
        extrudes.add(ph).name = f"BedFrame_PanelScrew_{pi}"

    for i in range(root.bRepBodies.count):
        b = root.bRepBodies.item(i)
        if b.name.startswith("Body"):
            b.name = "BedFrame_BottomPanel"

    vp = app.activeViewport
    if vp:
        vp.fit()

    print("BedFrame complete — params: design/bed_params.json")
    print("Grid:", gn_x, "x", gn_y, "cells | seat", seat_depth, "mm floor", floor_t, "mm")
    print("Deck mm:", deck_x, "x", deck_y, "| top Z:", deck_stack)
    print("Bodies:", root.bRepBodies.count)
    print("Export STLs from Fusion → Bambu P2S")

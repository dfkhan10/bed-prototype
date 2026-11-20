# Builds full bed-frame layout in the active Fusion design (single Part document).
# Clears timeline, one combined body + cell deck body, mechanical connectors D1/D2/E1/E7.
# Run via MCP or Scripts and Add-Ins. Save to hub project "bed frame".

import adsk.core, adsk.fusion


def mm(v):
    return v / 10.0


def clear_design(design):
    root = design.rootComponent
    t = design.timeline
    while t.count > 0:
        t.item(t.count - 1).deleteObject()
    for i in range(root.sketches.count - 1, -1, -1):
        root.sketches.item(i).deleteMe()
    for i in range(root.constructionPlanes.count - 1, -1, -1):
        p = root.constructionPlanes.item(i)
        if p.isLightBulbOn:
            try:
                if p.name.startswith("BedFrame_"):
                    p.deleteMe()
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


def combine_all(root, keep_name="BedFrame_Main"):
    bodies = root.bRepBodies
    if bodies.count <= 1:
        if bodies.count == 1:
            bodies.item(0).name = keep_name
        return
    base = bodies.item(0)
    tools = adsk.core.ObjectCollection.create()
    for i in range(1, bodies.count):
        tools.add(bodies.item(i))
    comb = root.features.combineFeatures.add(base, tools)
    comb.name = "BedFrame_CombineAll"
    comb.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    base.name = keep_name


def run(_context: str):
    app = adsk.core.Application.get()
    ui = app.userInterface
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        raise RuntimeError("Open a Design document (not Manufacture/Drawing).")

    # Prefer Solid workspace so geometry is visible
    ws = ui.workspaces.itemById("FusionSolidEnvironment")
    if ws:
        ws.activate()

    clear_design(design)
    root = design.rootComponent
    xy = root.xYConstructionPlane
    extrudes = root.features.extrudeFeatures
    planes = root.constructionPlanes

    # --- params (mm) ---
    E_BAY_X, E_BAY_Y = 200.0, 128.0
    PANEL_T, WALL_H, WALL_T = 4.0, 48.0, 3.0
    PUMP_AXIS_L, PUMP_HEAD_D = 68.0, 31.0
    PUMP_COLS, PUMP_ROWS, PUMP_COUNT = 4, 2, 8
    COL_PITCH, ROW_PITCH = 36.0, 38.0
    ARDUINO_L, ARDUINO_W, STANDOFF_H = 69.0, 54.0, 6.0
    BOSS_D, M3_HOLE_D = 8.0, 3.2
    DECK_XY = 226.0
    GRID_N, CELL_PITCH, WELL = 3, 76.0, 58.0
    DECK_CAVITY = 32.0
    DECK_TOP_T = 4.0
    DOWEL_D, DOWEL_DEPTH = 5.0, 10.0
    LAP_M3_D = 3.4

    z_top_bay = PANEL_T + WALL_H

    # === 1) Electronics bay floor + walls ===
    sk_base = rect_sketch(root, xy, 0, 0, E_BAY_X / 2, E_BAY_Y / 2, "BedFrame_EBayFloorSketch")
    base_in = extrudes.createInput(
        sk_base.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    base_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(PANEL_T)))
    extrudes.add(base_in).name = "BedFrame_EBayFloor"

    top_plane_in = planes.createInput()
    top_plane_in.setByOffset(xy, adsk.core.ValueInput.createByReal(mm(PANEL_T)))
    top_plane = planes.add(top_plane_in)
    top_plane.name = "BedFrame_EBayFloorTop"

    sk_wall = rect_sketch(root, top_plane, 0, 0, E_BAY_X / 2, E_BAY_Y / 2, "BedFrame_EBayWallSketch")
    wall_in = extrudes.createInput(
        sk_wall.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    wall_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(WALL_H)))
    extrudes.add(wall_in).name = "BedFrame_EBayWall"

    sk_void = rect_sketch(
        root, top_plane, 0, 0, E_BAY_X / 2 - WALL_T, E_BAY_Y / 2 - WALL_T, "BedFrame_EBayVoidSketch"
    )
    void_in = extrudes.createInput(
        sk_void.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
    )
    void_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(WALL_H + 1)))
    extrudes.add(void_in).name = "BedFrame_EBayVoid"

    # Pump pockets
    idx = 0
    for iy in range(PUMP_ROWS):
        for ix in range(PUMP_COLS):
            if idx >= PUMP_COUNT:
                break
            cx = (ix - (PUMP_COLS - 1) / 2.0) * COL_PITCH - 8
            cy = (iy - (PUMP_ROWS - 1) / 2.0) * ROW_PITCH - 8
            sk_p = rect_sketch(
                root, xy, cx, cy, PUMP_AXIS_L / 2, PUMP_HEAD_D / 2, f"BedFrame_PumpSketch_{idx}"
            )
            p_in = extrudes.createInput(
                sk_p.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            p_in.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(mm(PANEL_T + PUMP_HEAD_D))
            )
            extrudes.add(p_in).name = f"BedFrame_PumpPocket_{idx}"
            idx += 1

    # E7 tube pass-throughs (+Y wall toward cells)
    for sx in (-60.0, 0.0, 60.0):
        sk_t = root.sketches.add(xy)
        sk_t.name = "BedFrame_TubePortSketch"
        sk_t.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(sx), mm(E_BAY_Y / 2 - WALL_T), 0), mm(5)
        )
        t_in = extrudes.createInput(
            sk_t.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        t_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(WALL_H + PANEL_T)))
        extrudes.add(t_in).name = "BedFrame_TubePort"

    # E1 M3 bosses on bay floor corners / edges
    inset = 8.0
    hx, hy = E_BAY_X / 2 - inset, E_BAY_Y / 2 - inset
    boss_pts = [
        (-hx, -hy),
        (0, -hy),
        (hx, -hy),
        (-hx, 0),
        (hx, 0),
        (-hx, hy),
        (0, hy),
        (hx, hy),
    ]
    for i, (bx, by) in enumerate(boss_pts):
        sk_b = root.sketches.add(xy)
        sk_b.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(bx), mm(by), 0), mm(BOSS_D / 2)
        )
        bj = extrudes.createInput(
            sk_b.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        bj.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(WALL_H)))
        extrudes.add(bj).name = f"BedFrame_Boss_{i}"
        sk_bh = root.sketches.add(xy)
        sk_bh.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(bx), mm(by), 0), mm(M3_HOLE_D / 2)
        )
        bh = extrudes.createInput(
            sk_bh.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        bh.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(WALL_H + PANEL_T + 2)))
        extrudes.add(bh).name = f"BedFrame_BossHole_{i}"

    combine_all(root, "BedFrame_ElectronicsBay")

    # === 2) Cell deck (separate body, positioned on +Y side) ===
    deck_y = E_BAY_Y / 2 + DECK_XY / 2 + 8.0
    deck_z_base = z_top_bay + DECK_TOP_T

    deck_plane_in = planes.createInput()
    deck_plane_in.setByOffset(xy, adsk.core.ValueInput.createByReal(mm(deck_z_base)))
    deck_plane = planes.add(deck_plane_in)
    deck_plane.name = "BedFrame_CellDeckPlane"

    sk_deck = rect_sketch(
        root, deck_plane, 0, deck_y, DECK_XY / 2, DECK_XY / 2, "BedFrame_CellDeckSketch"
    )
    deck_in = extrudes.createInput(
        sk_deck.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    deck_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(DECK_CAVITY)))
    deck_feat = extrudes.add(deck_in)
    deck_feat.name = "BedFrame_CellDeckBlock"
    deck_body = deck_feat.bodies.item(0)
    deck_body.name = "BedFrame_CellDeck"

    # Wells 3x3
    for i in range(GRID_N):
        for j in range(GRID_N):
            cx = (i - (GRID_N - 1) / 2.0) * CELL_PITCH
            cy = deck_y + (j - (GRID_N - 1) / 2.0) * CELL_PITCH
            sk_w = rect_sketch(
                root, deck_plane, cx, cy, WELL / 2, WELL / 2, f"BedFrame_WellSketch_{i}_{j}"
            )
            w_in = extrudes.createInput(
                sk_w.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            w_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(DECK_CAVITY + 1)))
            extrudes.add(w_in).name = f"BedFrame_Well_{i}_{j}"

    # D1 dowel pins (holes on cell deck foot toward electronics)
    foot_y = deck_y - DECK_XY / 2 + 8.0
    for dx in (-DECK_XY / 4, DECK_XY / 4):
        sk_d = root.sketches.add(deck_plane)
        sk_d.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(dx), mm(foot_y), 0), mm(DOWEL_D / 2)
        )
        d_in = extrudes.createInput(
            sk_d.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        d_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(DOWEL_DEPTH + 2)))
        extrudes.add(d_in).name = "BedFrame_DowelHole"

    # D2 lap joint M3 holes at foot
    for dx in (-DECK_XY / 3, DECK_XY / 3):
        sk_l = root.sketches.add(deck_plane)
        sk_l.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(dx), mm(foot_y), 0), mm(LAP_M3_D / 2)
        )
        l_in = extrudes.createInput(
            sk_l.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        l_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(DECK_TOP_T + DECK_CAVITY + 2)))
        extrudes.add(l_in).name = "BedFrame_LapScrew"

    # Match dowel bosses on electronics bay +Y lip (simple pegs)
    lip_plane_in = planes.createInput()
    lip_plane_in.setByOffset(xy, adsk.core.ValueInput.createByReal(mm(z_top_bay)))
    lip_plane = planes.add(lip_plane_in)
    lip_plane.name = "BedFrame_MatePlane"
    mate_y = E_BAY_Y / 2 - 4.0
    for dx in (-DECK_XY / 4, DECK_XY / 4):
        sk_p = root.sketches.add(lip_plane)
        sk_p.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(dx), mm(mate_y), 0), mm(DOWEL_D / 2 - 0.05)
        )
        peg_in = extrudes.createInput(
            sk_p.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        peg_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(DOWEL_DEPTH)))
        extrudes.add(peg_in).name = "BedFrame_DowelPeg"

    # Keep 2 bodies (electronics + cell deck) for assembly clarity

    vp = app.activeViewport
    if vp:
        vp.fit()
        vp.camera.isSmoothTransition = False

    print("BedFrame environment rebuilt.")
    print("Save: File -> Save -> project 'bed frame' -> BedPrototype_Frame_v1.f3d")
    print("Bodies:", root.bRepBodies.count)

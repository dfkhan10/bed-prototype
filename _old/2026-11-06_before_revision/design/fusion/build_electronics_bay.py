# DEPRECATED — use build_bed_frame_environment.py (full bed + bed_params.json).
# Kept for reference only.

import adsk.core, adsk.fusion


def mm(v):
    return v / 10.0


def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent

    E_BAY_X = 200.0
    E_BAY_Y = 128.0
    PANEL_T = 4.0
    WALL_H = 48.0
    PUMP_AXIS_L = 68.0
    PUMP_HEAD_D = 31.0
    PUMP_COLS = 4
    PUMP_ROWS = 2
    PUMP_COUNT = 8
    COL_PITCH = 36.0
    ROW_PITCH = 38.0
    ARDUINO_L = 69.0
    ARDUINO_W = 54.0
    STANDOFF_H = 6.0
    BOSS_D = 8.0
    WALL_T = 3.0

    for i in range(root.features.count - 1, -1, -1):
        feat = root.features.item(i)
        if feat.name.startswith("BedProto_"):
            feat.deleteMe()

    xy = root.xYConstructionPlane
    extrudes = root.features.extrudeFeatures
    planes = root.constructionPlanes

    def rect_on_plane(plane, cx, cy, hx, hy, name):
        sk = root.sketches.add(plane)
        sk.name = name
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(mm(cx - hx), mm(cy - hy), 0),
            adsk.core.Point3D.create(mm(cx + hx), mm(cy + hy), 0),
        )
        return sk

    sk_base = rect_on_plane(xy, 0, 0, E_BAY_X / 2, E_BAY_Y / 2, "BedProto_BaseSketch")
    base_in = extrudes.createInput(
        sk_base.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    base_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(PANEL_T)))
    extrudes.add(base_in).name = "BedProto_BottomPanel"

    top_plane_in = planes.createInput()
    top_plane_in.setByOffset(xy, adsk.core.ValueInput.createByReal(mm(PANEL_T)))
    top_plane = planes.add(top_plane_in)
    top_plane.name = "BedProto_TopOfPanel"

    sk_wall = rect_on_plane(top_plane, 0, 0, E_BAY_X / 2, E_BAY_Y / 2, "BedProto_WallOuter")
    wall_in = extrudes.createInput(
        sk_wall.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    wall_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(WALL_H)))
    extrudes.add(wall_in).name = "BedProto_WallOuterExtrude"

    sk_void = rect_on_plane(
        top_plane, 0, 0, E_BAY_X / 2 - WALL_T, E_BAY_Y / 2 - WALL_T, "BedProto_Void"
    )
    void_in = extrudes.createInput(
        sk_void.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
    )
    void_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(WALL_H + 1)))
    extrudes.add(void_in).name = "BedProto_VoidCut"

    idx = 0
    for iy in range(PUMP_ROWS):
        for ix in range(PUMP_COLS):
            if idx >= PUMP_COUNT:
                break
            cx = (ix - (PUMP_COLS - 1) / 2.0) * COL_PITCH - 8
            cy = (iy - (PUMP_ROWS - 1) / 2.0) * ROW_PITCH - 8
            sk_p = rect_on_plane(
                xy, cx, cy, PUMP_AXIS_L / 2, PUMP_HEAD_D / 2, f"BedProto_Pump_{idx}"
            )
            p_in = extrudes.createInput(
                sk_p.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            p_in.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(mm(PANEL_T + PUMP_HEAD_D))
            )
            extrudes.add(p_in).name = f"BedProto_PumpPocket_{idx}"
            idx += 1

    ax = E_BAY_X / 2 - 8 - ARDUINO_L / 2 - 6
    ay = -E_BAY_Y / 2 + 8 + ARDUINO_W / 2 + 6
    sk_a = rect_on_plane(
        xy, ax, ay, ARDUINO_L / 2 + 3, ARDUINO_W / 2 + 3, "BedProto_ArduinoPocket"
    )
    a_in = extrudes.createInput(
        sk_a.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
    )
    a_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(PANEL_T + 0.5)))
    extrudes.add(a_in).name = "BedProto_ArduinoPocket"

    for dx in (-1, 1):
        for dy in (-1, 1):
            sx = ax + dx * 30.5
            sy = ay + dy * 23.0
            sk_s = root.sketches.add(xy)
            sk_s.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(mm(sx), mm(sy), 0), mm(3)
            )
            join_in = extrudes.createInput(
                sk_s.profiles.item(0), adsk.fusion.FeatureOperations.JoinFeatureOperation
            )
            join_in.setDistanceExtent(False, adsk.core.ValueInput.createByReal(mm(STANDOFF_H)))
            extrudes.add(join_in).name = "BedProto_Standoff"
            sk_h = root.sketches.add(xy)
            sk_h.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create(mm(sx), mm(sy), 0), mm(1.25)
            )
            hole_in = extrudes.createInput(
                sk_h.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
            )
            hole_in.setDistanceExtent(
                False, adsk.core.ValueInput.createByReal(mm(STANDOFF_H + PANEL_T))
            )
            extrudes.add(hole_in).name = "BedProto_StandoffHole"

    inset = 8
    hx = E_BAY_X / 2 - inset
    hy = E_BAY_Y / 2 - inset
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
        extrudes.add(bj).name = f"BedProto_Boss_{i}"
        sk_bh = root.sketches.add(xy)
        sk_bh.sketchCurves.sketchCircles.addByCenterRadius(
            adsk.core.Point3D.create(mm(bx), mm(by), 0), mm(1.6)
        )
        bh = extrudes.createInput(
            sk_bh.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation
        )
        bh.setDistanceExtent(
            False, adsk.core.ValueInput.createByReal(mm(WALL_H + PANEL_T + 2))
        )
        extrudes.add(bh).name = f"BedProto_BossHole_{i}"

    vp = app.activeViewport
    if vp:
        vp.fit()

    print("BedProto electronics bay OK")

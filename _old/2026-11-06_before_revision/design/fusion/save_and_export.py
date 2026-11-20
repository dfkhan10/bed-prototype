# Run after build_bed_frame_environment.py — export STLs + Save As to hub project.
# First cloud save may still require one manual File → Save in Fusion if saveAs fails.

import json
import os

import adsk.core, adsk.fusion


def run(_context: str):
    app = adsk.core.Application.get()
    doc = app.activeDocument
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        raise RuntimeError("No active Fusion design.")

    export_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "export", "stl")
    )
    os.makedirs(export_dir, exist_ok=True)

    root = design.rootComponent
    em = design.exportManager
    for i in range(root.bRepBodies.count):
        body = root.bRepBodies.item(i)
        safe = "".join(c if c.isalnum() or c in "_-" else "_" for c in body.name)
        path = os.path.join(export_dir, safe + ".stl")
        opts = em.createSTLExportOptions(body, path)
        opts.isBinaryFormat = True
        opts.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium
        em.execute(opts)
        print("STL:", path)

    hub = app.data.activeHub
    proj = None
    for i in range(hub.dataProjects.count):
        p = hub.dataProjects.item(i)
        if p.name == "bed frame":
            proj = p
            break
    if proj:
        fdoc = adsk.fusion.FusionDocument.cast(doc)
        ok = fdoc.saveAs("BedPrototype_Frame_v1", proj.rootFolder, "Bed prototype v1", "")
        print("saveAs bed frame/BedPrototype_Frame_v1:", ok)
    else:
        print("Project 'bed frame' not found — save manually.")

"""Save native/STEP snapshots of the active grouped design, without rebuilding.
For synchronized STL and validation, rebuild with BedGroupedPrototype then run
2026-11-06_grouped_exports.py. Manual snapshot export does not rerun CAD checks.
"""
from pathlib import Path
import adsk.core,adsk.fusion
ROOT=Path("/Users/ivanyalov/Desktop/Bed prototype")
def run(context):
    app=adsk.core.Application.get();design=adsk.fusion.Design.cast(app.activeProduct)
    if not design or not design.attributes.itemByName("BedPrototype","builder"):raise RuntimeError("Open the grouped master first")
    occurrences=list(design.rootComponent.occurrences)
    assembled=next(o for o in occurrences if o.component.name=="Assembly_Raised")
    em=design.exportManager;out=ROOT/"export/2026-11-06_grouped"
    visible=[o.isLightBulbOn for o in occurrences]
    try:
        for o in occurrences:o.isLightBulbOn=False
        for name,stem in [("Assembly_Raised","GroupedBed_assembled"),("Inspection_Exploded","Inspection_Exploded"),("Inspection_G1Raised_G2Lowered","Inspection_G1Raised_G2Lowered")]:
            o=next(o for o in occurrences if o.component.name==name);o.isLightBulbOn=True
            em.execute(em.createSTEPExportOptions(str(out/("2026-11-06_"+stem+".step")),o.component));o.isLightBulbOn=False
        assembled.isLightBulbOn=True
        em.execute(em.createFusionArchiveExportOptions(str(out/"2026-11-06_GroupedBed.f3d")))
    finally:
        for o,state in zip(occurrences,visible):o.isLightBulbOn=state
    print("Native/STEP snapshots saved. Rebuild and postprocess for synchronized print meshes and checks.")

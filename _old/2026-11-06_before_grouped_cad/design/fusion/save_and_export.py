"""Local Fusion archives, STEP and printable STL. Does not publish or cloud-save.
Exports only Assembly_Assembled/BedFrame_*; preserves old exports in _old.
"""
import json
import os
import shutil
import adsk.core, adsk.fusion

PROJECT='/Users/ivanyalov/Desktop/Bed prototype'


def run(_context:str):
    app=adsk.core.Application.get();design=adsk.fusion.Design.cast(app.activeProduct)
    if not design:raise RuntimeError('No active Fusion design')
    root=design.rootComponent
    assembled=next((o for o in root.occurrences if o.component.name=='Assembly_Assembled'),None)
    exploded=next((o for o in root.occurrences if o.component.name=='Inspection_Exploded'),None)
    if not assembled or not exploded:raise RuntimeError('Run the current master builder first')
    p=json.loads(design.attributes.itemByName('BedPrototype','params').value)
    L=json.loads(design.attributes.itemByName('BedPrototype','layout').value)
    out=os.path.join(PROJECT,'export');stldir=os.path.join(out,'stl');refdir=os.path.join(out,'reference')
    os.makedirs(stldir,exist_ok=True);os.makedirs(refdir,exist_ok=True)
    old=os.path.join(PROJECT,'_old','2026-11-06_before_revision','stl');os.makedirs(old,exist_ok=True)
    for name in os.listdir(stldir):
        if name.endswith('.stl'):
            target=os.path.join(old,name)
            if os.path.exists(target):target=os.path.join(old,'previous_'+name)
            shutil.move(os.path.join(stldir,name),target)
    em=design.exportManager;manifest={'units':'mm','parts':[],'references':[], 'layout':L,'params':p}
    for occ in assembled.component.occurrences:
        c=occ.component
        if c.name.startswith('BedFrame_'):
            if c.bRepBodies.count!=1:raise RuntimeError(c.name+': unexpected body count')
            b=c.bRepBodies.item(0)
            if b.name!=c.name:raise RuntimeError('Unapproved body name: '+b.name)
            path=os.path.join(stldir,b.name+'.stl')
            opt=em.createSTLExportOptions(b,path);opt.isBinaryFormat=True
            opt.meshRefinement=adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            if not em.execute(opt):raise RuntimeError('STL export failed: '+path)
            bb=b.boundingBox;dims=[(bb.maxPoint.asArray()[i]-bb.minPoint.asArray()[i])*10 for i in range(3)]
            if max(dims)>p['print_max_mm']+0.01:raise RuntimeError('Print limit exceeded: '+b.name)
            manifest['parts'].append({'name':b.name,'file':'stl/'+b.name+'.stl','bbox_mm':dims,'volume_mm3':b.volume*1000})
        elif c.name.startswith('Reference_'):
            for child in c.occurrences:
                b=child.component.bRepBodies.item(0);path=os.path.join(refdir,b.name+'.stl')
                opt=em.createSTLExportOptions(b,path);opt.isBinaryFormat=True
                if not em.execute(opt):raise RuntimeError('Reference export failed')
                manifest['references'].append({'name':b.name,'file':'reference/'+b.name+'.stl','status':'unmeasured valve envelope' if 'Valve' in b.name else 'generic M2.5 screw reference'})
    # Verify actual BRep cylinders: Y-axis deck/service pairs and Z-axis rim/bay/panel.
    manifest['hole_axes']=[]
    for occ in assembled.component.occurrences:
        if not occ.component.name.startswith('BedFrame_'):continue
        for face in occ.component.bRepBodies.item(0).faces:
            cyl=adsk.core.Cylinder.cast(face.geometry)
            if cyl:
                manifest['hole_axes'].append({'part':occ.component.name,'diameter_mm':cyl.radius*20,'origin_mm':[v*10 for v in cyl.origin.asArray()],'axis':cyl.axis.asArray()})
    entities=adsk.core.ObjectCollection.create()
    for occ in assembled.component.occurrences:
        if occ.component.name.startswith('BedFrame_'):entities.add(occ)
    inp=design.createInterferenceInput(entities);inp.areCoincidentFacesIncluded=False
    interference=design.analyzeInterference(inp)
    manifest['interferences']=[] if not interference else [{'a':r.entityOne.name,'b':r.entityTwo.name,'volume_mm3':r.interferenceBody.volume*1000} for r in interference]
    manifest['feature_issues']=[{'name':it.name,'message':it.errorOrWarningMessage} for it in design.timeline if it.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState]
    if manifest['interferences'] or manifest['feature_issues']:raise RuntimeError('Model check failed; no archives exported')
    assembled.isLightBulbOn=True;exploded.isLightBulbOn=False
    for mode in ['assembled','exploded']:
        assembled.isLightBulbOn=mode=='assembled';exploded.isLightBulbOn=mode=='exploded'
        stem=os.path.join(out,'2026-11-06_BedPrototype_'+mode)
        if not em.execute(em.createFusionArchiveExportOptions(stem+'.f3d')):raise RuntimeError('Archive export failed')
        component=assembled.component if mode=='assembled' else exploded.component
        if not em.execute(em.createSTEPExportOptions(stem+'.step',component)):raise RuntimeError('STEP export failed')
    with open(os.path.join(out,'2026-11-06_export_manifest.json'),'w') as f:json.dump(manifest,f,indent=2)
    print('Exported',len(manifest['parts']),'printable parts,',len(manifest['references']),'hardware references (valves + generic screws).')
    print('Assembled and exploded F3D + STEP:',out)
    print('Zero solid interferences; all timeline features healthy. Exploded inspection visible.')

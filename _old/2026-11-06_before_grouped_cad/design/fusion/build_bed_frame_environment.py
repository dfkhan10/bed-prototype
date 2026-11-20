"""Fusion master. Creates a NEW document; preserves the user's open design.
Run in Fusion Scripts, or execute this file's contents through Fusion MCP.
All authored dimensions: design/bed_params.json. Reference envelopes are not print parts.
"""
import json
import os
import sys
import adsk.core, adsk.fusion

PROJECT = '/Users/ivanyalov/Desktop/Bed prototype'
SCRIPT_DIR = os.path.join(PROJECT, 'design', 'fusion')
if SCRIPT_DIR not in sys.path: sys.path.insert(0, SCRIPT_DIR)
# Reload because Fusion keeps the interpreter alive between builds.
import importlib
import bed_layout
importlib.reload(bed_layout)

NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation


def mm(v): return v/10

def point(x,y,z): return adsk.core.Point3D.create(mm(x),mm(y),mm(z))

def collection(items):
    c=adsk.core.ObjectCollection.create()
    for item in items:c.add(item)
    return c


def plane_at(comp, axis, value):
    base = comp.xYConstructionPlane if axis=='z' else comp.xZConstructionPlane
    n=base.geometry.normal
    normal=n.z if axis=='z' else n.y
    inp=comp.constructionPlanes.createInput()
    inp.setByOffset(base,adsk.core.ValueInput.createByReal(mm(value/normal)))
    plane=comp.constructionPlanes.add(inp);plane.name='Plane_'+axis+'_'+str(value)
    plane.isLightBulbOn=False
    return plane


def sketch_rect(comp, bounds, axis, coord, name):
    # bounds are X/Y for Z extrusions, X/Z for Y extrusions; modelToSketchSpace
    # avoids assumptions about Fusion's XZ sketch handedness.
    x0,y0,x1,y1=bounds
    sk=comp.sketches.add(plane_at(comp,axis,coord));sk.name=name
    a=point(x0,y0,coord) if axis=='z' else point(x0,coord,y0)
    b=point(x1,y1,coord) if axis=='z' else point(x1,coord,y1)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(sk.modelToSketchSpace(a),sk.modelToSketchSpace(b))
    return sk


def extrude(comp, sk, length, axis, op, name):
    inp=comp.features.extrudeFeatures.createInput(sk.profiles.item(0),op)
    normal=sk.referencePlane.geometry.normal
    sign=(normal.z if axis=='z' else normal.y)*length
    extent=adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(mm(abs(length))))
    direction=adsk.fusion.ExtentDirections.PositiveExtentDirection if sign>0 else adsk.fusion.ExtentDirections.NegativeExtentDirection
    inp.setOneSideExtent(extent,direction)
    if op==CUT: inp.participantBodies=[comp.bRepBodies.item(0)]
    feat=comp.features.extrudeFeatures.add(inp);feat.name=name;sk.isVisible=False
    if comp.bRepBodies.count != 1: raise RuntimeError(name+': disconnected or stray bodies')
    return feat


def box(comp,bounds,z,h,op,name):
    return extrude(comp,sketch_rect(comp,bounds,'z',z,name+'_Sketch'),h,'z',op,name)


def hole(comp,x,y,z,d,length,axis,name):
    sk=comp.sketches.add(plane_at(comp,axis,z if axis=='z' else y));sk.name=name+'_Sketch'
    sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(point(x,y,z)),mm(d/2))
    return extrude(comp,sk,length,axis,CUT,name)


def boss(comp,x,y,z,d,h,name):
    sk=comp.sketches.add(plane_at(comp,'z',z));sk.name=name+'_Sketch'
    sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(point(x,y,z)),mm(d/2))
    return extrude(comp,sk,h,'z',JOIN,name)


def round_vertical(comp, r, name):
    edges=[]
    for e in comp.bRepBodies.item(0).edges:
        a,b=e.startVertex.geometry,e.endVertex.geometry
        if abs(a.x-b.x)<1e-6 and abs(a.y-b.y)<1e-6 and abs(a.z-b.z)>1e-6:edges.append(e)
    inp=comp.features.filletFeatures.createInput()
    inp.edgeSetInputs.addConstantRadiusEdgeSet(collection(edges),adsk.core.ValueInput.createByReal(mm(r)),False)
    comp.features.filletFeatures.add(inp).name=name


def soften(comp,p):
    body=comp.bRepBodies.item(0)
    if comp.name.startswith('BedFrame_CellDeck'):
        edges=[]
        for e in body.edges:
            if not e.startVertex or not e.endVertex:continue
            a,b=e.startVertex.geometry,e.endVertex.geometry
            if abs(a.x-b.x)<1e-6 and abs(a.y-b.y)<1e-6 and abs(abs(a.z-b.z)*10-p['cell_seat_depth'])<1e-5:
                edges.append(e)
        if edges:
            inp=comp.features.filletFeatures.createInput()
            inp.edgeSetInputs.addConstantRadiusEdgeSet(collection(edges),adsk.core.ValueInput.createByReal(mm(p['seat_corner_r'])),False)
            comp.features.filletFeatures.add(inp).name='RoundedCellSeats'
    body=comp.bRepBodies.item(0);bb=body.boundingBox;edges=[]
    for e in body.edges:
        eb=e.boundingBox
        if abs(eb.minPoint.z-bb.maxPoint.z)<1e-6 and abs(eb.maxPoint.z-bb.maxPoint.z)<1e-6:
            if any(abs(a-b)<1e-6 for a,b in [(eb.minPoint.x,bb.minPoint.x),(eb.maxPoint.x,bb.maxPoint.x),(eb.minPoint.y,bb.minPoint.y),(eb.maxPoint.y,bb.maxPoint.y)]):edges.append(e)
    if edges:
        inp=comp.features.filletFeatures.createInput()
        inp.edgeSetInputs.addConstantRadiusEdgeSet(collection(edges),adsk.core.ValueInput.createByReal(mm(p['edge_break_r'])),False)
        comp.features.filletFeatures.add(inp).name='OuterTopEdgeSoftening'


def new_part(parent,name):
    occ=parent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name=name
    return occ,occ.component


def finish(comp,name):
    if comp.bRepBodies.count!=1:raise RuntimeError(name+': expected one body')
    comp.bRepBodies.item(0).name=name
    for s in comp.sketches:s.isVisible=False
    for pl in comp.constructionPlanes:pl.isLightBulbOn=False


def reference_screw(parent,name,x,y,z,axis,sign,p):
    occ,c=new_part(parent,name);f=p['fasteners']
    for d,length,op,label in [(2.5,sign*f['screw_length_mm'],NEW,'Shank'),(f['head_clearance_d'],-sign*f['head_h'],JOIN,'Head')]:
        sk=c.sketches.add(plane_at(c,axis,z if axis=='z' else y))
        sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(point(x,y,z)),mm(d/2))
        extrude(c,sk,length,axis,op,label)
    finish(c,name)
    return occ


def add_fasteners(master,ec,p,L):
    sy=p['exploded']['service_shift_y_mm'];withdraw=p['exploded']['screw_withdrawal_mm']
    groups=[('Reference_CellJointScrews','ScrewCell',(0,withdraw,p['exploded']['cell_lift_mm'])),
            ('Reference_RimScrews','ScrewRim',(0,sy,-p['exploded']['bay_drop_mm']-withdraw)),
            ('Reference_PanelScrews','ScrewPanel',(0,sy,-p['exploded']['panel_drop_mm']-withdraw))]
    for group,label,of in groups:
        occ,c=new_part(master,group)
        if label=='ScrewCell':
            seams=[(-L['length']/2+p['wall_t'],-1)]
            seams += [(tile['ymax']-p['wall_t'],1) for tile in L['tiles'][1:]]
            for si,(y,sign) in enumerate(seams):
                for i,x in enumerate(L['joint_xs']):reference_screw(c,'Reference_'+label+'_'+str(si)+'_'+str(i),x,y,p['joint_axis_z'],'y',sign,p)
        else:
            z=-p['panel_t'] if label=='ScrewRim' else -p['e_bay_cavity_h']-p['panel_t']
            for i,(x,y) in enumerate(L['screw_points']):reference_screw(c,'Reference_'+label+'_'+str(i),x,y,z,'z',1,p)
        mat=adsk.core.Matrix3D.create();mat.translation=adsk.core.Vector3D.create(*[mm(v) for v in of]);ec.occurrences.addExistingComponent(c,mat)


def build(p,report_name='2026-11-06_geometry_report.json'):
    app=adsk.core.Application.get()
    L=bed_layout.layout(p);f=p['fasteners'];t=L['ztop'];roof=L['roof'];cav=p['cavity_h']
    doc=app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design=adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
    design.designType=adsk.fusion.DesignTypes.ParametricDesignType
    root=design.rootComponent
    assembly,master=new_part(root,'Assembly_Assembled')
    parts=[]
    # CELL DECK: hollow underside, true 2 mm seats and 2 mm floors, continuous ribs.
    for tile in L['tiles']:
        name=tile['name'];occ,c=new_part(master,name);parts.append((occ,'cell'))
        lo,hi=tile['ymin'],tile['ymax'];hx=L['width']/2;w=p['wall_t']
        box(c,(-hx,lo,hx,hi),0,t,NEW,'DeckBlank')
        round_vertical(c,p['corner_r'],'OuterCorner_R'+str(p['corner_r']))
        box(c,(-hx+w,lo+w,hx-w,hi-w),0,cav,CUT,'OpenUnderside')
        # Longitudinal and cross ribs restore support below the cell-to-cell webs.
        for i in range(p['grid_n_x']-1):
            x=(i-(p['grid_n_x']-2)/2)*p['cell_pitch'];q=p['rib_t']/2
            box(c,(x-q,lo+w-0.1,x+q,hi-w+0.1),0,cav,JOIN,'LongRib_'+str(i))
        for row in range(p['grid_n_y']-1):
            y=(L['cells'][row*p['grid_n_x']]['y']+L['cells'][(row+1)*p['grid_n_x']]['y'])/2
            if lo+w < y < hi-w:
                q=p['rib_t']/2;box(c,(-hx+w-0.1,y-q,hx-w+0.1,y+q),0,cav,JOIN,'CrossRib_'+str(row))
        for cell in L['cells']:
            if cell['row'] not in tile['rows']:continue
            x,y=cell['x'],cell['y'];h=p['well_open']/2
            box(c,(x-h,y-h,x+h,y+h),t,-p['cell_seat_depth'],CUT,'Seat_'+cell['id'])
            hole(c,x,y,t-p['cell_seat_depth'],p['port_d'],-p['cell_floor_t'],'z','Port_'+cell['id'])
        # Open 4-hose bundle tunnels in every cross rib and the mating wall.
        for col in range(p['grid_n_x']):
            x=(col-(p['grid_n_x']-1)/2)*p['cell_pitch'];q=p['tube_bundle_w']/2
            box(c,(x-q,lo-0.1,x+q,hi-p['wall_t']-0.1 if tile==L['tiles'][0] else hi+0.1),p['tube_route_z']-p['tube_bundle_h']/2,p['tube_bundle_h'],CUT,'TubeBundle_'+str(col))
        # Four Y-axis screws at each interface. Heads accessible from open underside.
        for edge,is_front in [(lo,False),(hi,True)]:
            if is_front and tile==L['tiles'][0]:continue
            for i,x in enumerate(L['joint_xs']):
                if is_front: # Lower tile receives clearance, upper tile gets blind pilots.
                    hole(c,x,edge+0.1,p['joint_axis_z'],f['clearance_d'],-(w+0.2),'y','SeamClearance_'+str(i))
                elif tile!=L['tiles'][-1]:
                    box(c,(x-f['joint_receiver_w']/2,edge,x+f['joint_receiver_w']/2,edge+f['boss_h']),p['joint_axis_z']-f['joint_receiver_h']/2,f['joint_receiver_h'],JOIN,'SeamPad_'+str(i))
                    hole(c,x,edge-0.1,p['joint_axis_z'],f['pilot_d'],f['boss_h']-0.9,'y','SeamPilot_'+str(i))
                else:
                    hole(c,x,edge-0.1,p['joint_axis_z'],f['clearance_d'],w+0.2,'y','ServiceClearance_'+str(i))
        soften(c,p);finish(c,name)
    # SERVICE: closed clean top, underside-accessible valve rails and open bundle bulkhead.
    occ,c=new_part(master,'BedFrame_ServiceDeck');parts.append((occ,'service'))
    hx=L['service_x']/2;hy=L['service_y']/2;cy=L['service_cy'];w=p['electronics_wall_t']
    box(c,(-hx,cy-hy,hx,cy+hy),0,t,NEW,'ServiceBlank');round_vertical(c,p['corner_r'],'ServiceCorners')
    box(c,(-hx+w,cy-hy+w,hx-w,cy+hy-w),0,cav,CUT,'ServiceCavity')
    # Lower rim forms an accessible 4 mm grip for 10 mm screws into bay pilots.
    box(c,(-hx+w-0.1,cy-hy+w-0.1,hx-w+0.1,cy+hy-w+0.1),0,p['panel_t'],JOIN,'LowerFlangeBlank')
    fw=p['rim_flange_w']
    box(c,(-hx+fw,cy-hy+fw,hx-fw,cy+hy-fw),-0.1,p['panel_t']+0.2,CUT,'LowerFlangeOpening')
    for i,x in enumerate(L['joint_xs']):
        box(c,(x-f['joint_receiver_w']/2,cy+hy-f['boss_h'],x+f['joint_receiver_w']/2,cy+hy),p['joint_axis_z']-f['joint_receiver_h']/2,f['joint_receiver_h'],JOIN,'CellJointPad_'+str(i))
        hole(c,x,cy+hy+0.1,p['joint_axis_z'],f['pilot_d'],-(f['boss_h']-0.9),'y','CellJointPilot_'+str(i))
    for col in range(p['grid_n_x']):
        x=(col-(p['grid_n_x']-1)/2)*p['cell_pitch'];q=p['tube_bundle_w']/2
        box(c,(x-q,cy+hy-w-0.1,x+q,cy+hy+0.1),p['tube_route_z']-p['tube_bundle_h']/2,p['tube_bundle_h'],CUT,'Bulkhead_'+str(col))
    for i,(x,y) in enumerate(L['screw_points']):
        boss(c,x,y,0,f['boss_od'],f['boss_h'],'RimReceiver_'+str(i))
        hole(c,x,y,-0.1,f['pilot_d'],f['boss_h']-0.9,'z','RimPilot_'+str(i))
    # Provisional valve envelopes have side guide rails, open ends for fittings.
    for v in L['valves']:
        x,y=v['x'],v['y'];gap=p['valve_w']/2+p['valve_fit_clearance']/2;rt=p['valve_mount_rail_t'];rl=p['valve_mount_rail_l']/2;rh=p['valve_mount_rail_h']
        for side in (-1,1):
            a,b=(x-gap-rt,x-gap) if side<0 else (x+gap,x+gap+rt)
            box(c,(a,y-rl,b,y+rl),cav-rh,rh+0.1,JOIN,'ValveRail_'+v['id']+'_'+str(side))
    soften(c,p);finish(c,'BedFrame_ServiceDeck')
    # BAY: genuinely open frame, consistent wall; independent top/bottom blind bosses.
    occ,c=new_part(master,'BedFrame_ElectronicsBay');parts.append((occ,'bay'));bh=p['e_bay_cavity_h']
    box(c,(-hx,cy-hy,hx,cy+hy),-bh,bh,NEW,'BayBlank');round_vertical(c,p['corner_r'],'BayCorners')
    box(c,(-hx+w,cy-hy+w,hx-w,cy+hy-w),-bh-0.1,bh+0.2,CUT,'BayOpenBothSides')
    # Heads face down: a driver reaches these screws through the open bottom.
    box(c,(-hx+w-0.1,cy-hy+w-0.1,hx-w+0.1,cy+hy-w+0.1),-p['panel_t'],p['panel_t'],JOIN,'UpperFlangeBlank')
    box(c,(-hx+fw,cy-hy+fw,hx-fw,cy+hy-fw),-p['panel_t']-0.1,p['panel_t']+0.2,CUT,'UpperFlangeOpening')
    for i,(x,y) in enumerate(L['screw_points']):
        hole(c,x,y,-p['panel_t']-0.1,f['clearance_d'],p['panel_t']+0.2,'z','UpperClearance_'+str(i))
        # Connect inward-set lower bosses to walls with short printable webs.
        q=f['boss_web_t']/2
        if x:
            box(c,(min(x,(hx-0.1)*(1 if x>0 else -1)),y-q,max(x,(hx-0.1)*(1 if x>0 else -1)),y+q),-bh,f['boss_h'],JOIN,'LowerWebX_'+str(i))
        if abs(y-cy)>hy/2:
            edge=cy+(hy-0.1)*(1 if y>cy else -1)
            box(c,(x-q,min(y,edge),x+q,max(y,edge)),-bh,f['boss_h'],JOIN,'LowerWebY_'+str(i))
        boss(c,x,y,-bh,f['boss_od'],f['boss_h'],'LowerBoss_'+str(i))
        hole(c,x,y,-bh-0.1,f['pilot_d'],f['boss_h']-0.9,'z','LowerPilot_'+str(i))
    soften(c,p);finish(c,'BedFrame_ElectronicsBay')
    # PANEL: one complete removable solid, exactly the same XY screw table as the rim.
    occ,c=new_part(master,'BedFrame_BottomPanel');parts.append((occ,'panel'));pt=p['panel_t']
    box(c,(-hx,cy-hy,hx,cy+hy),-bh-pt,pt,NEW,'BottomPanelBlank');round_vertical(c,p['corner_r'],'PanelCorners')
    for i,(x,y) in enumerate(L['screw_points']):hole(c,x,y,-bh-pt-0.1,f['clearance_d'],pt+0.2,'z','PanelClearance_'+str(i))
    for i in range(p['vent_count']):
        x=(i-(p['vent_count']-1)/2)*p['vent_pitch']
        box(c,(x-p['vent_slot_w']/2,cy-p['vent_slot_l']/2,x+p['vent_slot_w']/2,cy+p['vent_slot_l']/2),-bh-pt-0.1,pt+0.2,CUT,'Vent_'+str(i))
    soften(c,p);finish(c,'BedFrame_BottomPanel')
    # Hardware is reference geometry only: deliberately no assumed pump count/mounts.
    refs,rc=new_part(master,'Reference_ValveEnvelopes_UNMEASURED')
    for v in L['valves']:
        vo,vc=new_part(rc,'Reference_Valve_'+v['id'])
        x,y=v['x'],v['y']
        box(vc,(x-p['valve_w']/2,y-p['valve_l']/2,x+p['valve_w']/2,y+p['valve_l']/2),cav-p['valve_h'],p['valve_h'],NEW,'Envelope')
        finish(vc,'Reference_Valve_'+v['id'])
    # A second linked assembly is a genuine exploded inspection state, never a print source.
    exploded,ec=new_part(root,'Inspection_Exploded')
    offsets={'cell':(0,0,p['exploded']['cell_lift_mm']),'service':(0,p['exploded']['service_shift_y_mm'],p['exploded']['service_lift_mm']),
             'bay':(0,p['exploded']['service_shift_y_mm'],-p['exploded']['bay_drop_mm']),'panel':(0,p['exploded']['service_shift_y_mm'],-p['exploded']['panel_drop_mm'])}
    for i,(part,kind) in enumerate(parts):
        dx,dy,dz=offsets[kind]
        if kind=='cell' and len(L['tiles'])>1:dy=(len(L['tiles'])-1-i)*20
        mat=adsk.core.Matrix3D.create();mat.translation=adsk.core.Vector3D.create(mm(dx),mm(dy),mm(dz))
        ec.occurrences.addExistingComponent(part.component,mat)
    mat=adsk.core.Matrix3D.create();mat.translation=adsk.core.Vector3D.create(0,mm(p['exploded']['service_shift_y_mm']),mm(-p['exploded']['valve_drop_mm']))
    ec.occurrences.addExistingComponent(rc,mat)
    add_fasteners(master,ec,p,L)
    exploded.isLightBulbOn=False
    design.attributes.add('BedPrototype','layout',json.dumps(L))
    design.attributes.add('BedPrototype','params',json.dumps(p))
    report={'parts':[], 'layout':L,'pump_count':None,'hardware_fit':'UNMEASURED','interferences':[]}
    entities=collection([o for o,k in parts])
    ii=design.createInterferenceInput(entities);ii.areCoincidentFacesIncluded=False
    results=design.analyzeInterference(ii)
    if results:
        for it in results:report['interferences'].append({'a':it.entityOne.name,'b':it.entityTwo.name,'volume_mm3':it.interferenceBody.volume*1000})
    for o,k in parts:
        b=o.component.bRepBodies.item(0);bb=b.boundingBox
        dims=[(bb.maxPoint.asArray()[j]-bb.minPoint.asArray()[j])*10 for j in range(3)]
        if max(dims)>p['print_max_mm']+0.01:raise RuntimeError(b.name+' exceeds print limit: '+str(dims))
        report['parts'].append({'name':b.name,'bbox_mm':dims,'volume_mm3':b.volume*1000,'kind':k})
    unhealthy=[]
    for item in design.timeline:
        if item.healthState!=adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:unhealthy.append({'name':item.name,'message':item.errorOrWarningMessage})
    report['feature_issues']=unhealthy
    out=os.path.join(PROJECT,'export');os.makedirs(out,exist_ok=True)
    with open(os.path.join(out,report_name),'w') as fp:json.dump(report,fp,indent=2)
    print(json.dumps(report,indent=2))
    if report['interferences'] or unhealthy:raise RuntimeError('Geometry verification failed; inspect report')
    print('Built assembled + linked exploded assemblies. Pump count intentionally pending.')


def run(_context:str):
    with open(os.path.join(PROJECT,'design','bed_params.json')) as f:p=json.load(f)
    build(p)

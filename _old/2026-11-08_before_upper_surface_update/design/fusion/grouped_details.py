"""Native section and one-cell fitting coupon, generated from the same solid master."""
import json,math

def make_details(context):
    global C,F,T,box,cyl,cut,union,zhole,bounds,moved,boolean,I,EPS,pt,vec
    gg=context['global'];v=context['local']
    for k in ['C','F','T','box','cyl','cut','union','zhole','bounds','moved','boolean','I','EPS','pt','vec']:globals()[k]=gg[k]
    p=v['p'];c=p['cell'];h=p['housing'];q=p['guide'];f=p['fasteners'];design=v['design'];app=v['app'];out=v['out'];components=v['components'];instances=v['instances'];component=v['component'];em=design.exportManager;ao=v['ao'];states=v['states'];progress=v['progress'];geo=context['global']
    def add_body(parent,name,body):
        o,co=component(parent,name);bf=co.features.baseFeatures.add();bf.startEdit();saved=co.bRepBodies.add(body,bf);saved.name=name;bf.finishEdit();return o,co
    def export_mesh(comp,name,folder):
        dest=folder/(name+'.stl');opt=em.createSTLExportOptions(comp.bRepBodies.item(0),str(dest));opt.isBinaryFormat=True;opt.meshRefinement=F.MeshRefinementSettings.MeshRefinementHigh;em.execute(opt);return dest
    progress('Creating the section and one-cell hardware-fit coupon')
    so,section=component(design.rootComponent,'Inspection_CellSection_A1');ce=v['cells'][0];pitch=p['grid']['pitch']
    window=box(ce['x'],ce['y']-pitch/2,-EPS,ce['x']+pitch/2,ce['y']+pitch/2,h['outer_top_z']+EPS)
    section_records=[]
    for en in instances:
        if en['kind'] in ['fastener'] or en['kind'].startswith('tube'):continue
        if not geo['intersects_bb'](bounds(en['body']),bounds(window)):continue
        b=T.copy(en['body'])
        if not T.booleanOperation(b,T.copy(window),I) or b.volume<1e-8:continue
        if en['kind'] not in ['frame','panel','cup','ring','cap1','tpu1','valve']:continue
        o,co=add_body(section,en['name']+'_Section',b)
        section_records.append({'name':co.name,'kind':en['kind']})
    so.isLightBulbOn=False
    # A deliberately simple one-cell stand preserves the exact production cup,
    # guide, ring, cap, dry flange and screw coordinates.
    co,coupon=component(design.rootComponent,'Coupon_OneCell')
    base=h['base_t'];r=pitch/2;top=h['frame_top_z'];cb,cby=c['cup_screw_xy'];wall=h['wall_t']
    stand=box(-r,-r,0,r,r,base)
    rim=box(-r,-r,top-wall,r,r,top);cut(rim,box(-r+wall,-r+wall,top-wall-EPS,r-wall,r-wall,top+EPS))
    # Build posts before joining the rim, so every final printed item is connected.
    for x in [-cb,cb]:
        for y in [-cby,cby]:
            union(stand,cyl((x,y,base-EPS),(x,y,top),h['column_od']))
            edge=-r+wall/2 if y<0 else r-wall/2
            union(stand,box(x-h['column_web_t']/2,min(y,edge),base-EPS,x+h['column_web_t']/2,max(y,edge)+EPS,top))
    union(stand,rim)
    for x in [-cb,cb]:
        for y in [-cby,cby]:
            zhole(stand,x,y,-EPS,top-h['column_grip'],h['column_tool_d']);zhole(stand,x,y,top-h['column_grip']-EPS,top+EPS,f['clearance_d'])
    # Inspection openings for the two guide-stop screws.
    for y in [-q['spacing_half'],q['spacing_half']]:zhole(stand,0,y,-EPS,base+EPS,h['column_tool_d'])
    o,standcomp=add_body(coupon,'Print_OneCellTestStand',stand)
    coupon_dir=out/'coupon';coupon_dir.mkdir(exist_ok=True);cm=coupon_dir/'meshes';cm.mkdir(exist_ok=True)
    export_mesh(standcomp,'Print_OneCellTestStand',cm)
    coupon_items=[{'name':'Print_OneCellTestStand','file':'coupon/meshes/Print_OneCellTestStand.stl','where':[0,0,0],'kind':'frame'}]
    for name in ['Print_CellCup','Print_ClampRing','Print_MovingCap_G1']:
        add_body(coupon,'Coupon_'+name,T.copy(components[name]['body']));coupon_items.append({'name':name,'file':'meshes/'+name+'.stl','where':[0,0,0],'kind':components[name]['kind']})
    # All coupon screws are the same types as the full assembly.
    for x in [-c['clamp_screw_xy'],c['clamp_screw_xy']]:
        for y in [-c['clamp_screw_xy'],c['clamp_screw_xy']]:
            add_body(coupon,'Coupon_Clamp',moved(components['Ref_Clamp_M2p5x10']['body'],(x,y,v['ring_top']-f['head_h'])))
    for x in [-cb,cb]:
        for y in [-cby,cby]:
            add_body(coupon,'Coupon_CupJoint',moved(components['Ref_CupJoint_M2p5x10']['body'],(x,y,top-h['column_grip'])))
    for y in [-q['spacing_half'],q['spacing_half']]:
        for name,xyz in [('Ref_StopWasher',(0,y,0)),('Ref_Stop_M2p5x6',(0,y,v['cap_high']-q['post_length']-q['washer_t']))]:
            add_body(coupon,'Coupon_'+name,moved(components[name]['body'],xyz))
    ao.isLightBulbOn=False;co.isLightBulbOn=True
    em.execute(em.createSTEPExportOptions(str(coupon_dir/'2026-11-06_OneCellCoupon.step'),coupon))
    co.isLightBulbOn=False;so.isLightBulbOn=True
    em.execute(em.createSTEPExportOptions(str(out/'2026-11-06_CellSection_A1.step'),section))
    so.isLightBulbOn=False;ao.isLightBulbOn=True
    def image(name,occ,eye,target):
        ao.isLightBulbOn=False
        for state in states.values():state.isLightBulbOn=False
        occ.isLightBulbOn=True
        vp=app.activeViewport;cam=vp.camera;cam.isPerspective=False;cam.eye=pt(*eye);cam.target=pt(*target);cam.upVector=vec(0,0,1);cam.isFitView=True;vp.camera=cam;vp.refresh();geo['adsk_do']();vp.saveAsImageFile(str(out/('2026-11-06_'+name+'.png')),1400,1100);occ.isLightBulbOn=False;ao.isLightBulbOn=True
    image('cell_section',so,(ce['x']+pitch*3,ce['y']-pitch*2,h['outer_top_z']*2),(ce['x']+pitch/4,ce['y'],h['outer_top_z']/2))
    image('one_cell_coupon',co,(pitch*3,-pitch*3,h['outer_top_z']*3),(0,0,h['outer_top_z']/2))
    manifest=json.loads((out/'2026-11-06_manifest.json').read_text());manifest['coupon']={'items':coupon_items,'stand_bbox_mm':[pitch,pitch,top],'hardware':{'M2.5x10':8,'M2.5x6':2,'M2.5_clearance_washers_OD8':2},'status':'fit coupon; pressure hardware and TPU are not print parts'};manifest['section']=section_records
    (out/'2026-11-06_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    ao.isLightBulbOn=True;v['capture']('assembled',(v['W'],-v['L'],h['outer_top_z']*5));em.execute(em.createFusionArchiveExportOptions(str(out/'2026-11-06_GroupedBed.f3d')))

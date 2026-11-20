"""JSON-driven editable Fusion solids for the fixed two-group bed prototype.
All geometry is in mm at this boundary; Fusion BRep uses cm. No cloud save.
Printable bodies and purchased/reference geometry are distinct components.
"""
import json, math, time, traceback
from pathlib import Path
import adsk.core as C
import adsk.fusion as F

T=F.TemporaryBRepManager.get()
U=F.BooleanTypes.UnionBooleanType
D=F.BooleanTypes.DifferenceBooleanType
I=F.BooleanTypes.IntersectionBooleanType
EPS=0.02

def pt(x,y,z): return C.Point3D.create(x/10,y/10,z/10)
def vec(x,y,z): return C.Vector3D.create(x,y,z)
def box(x0,y0,z0,x1,y1,z1):
    assert x1>x0 and y1>y0 and z1>z0,(x0,y0,z0,x1,y1,z1)
    bb=C.OrientedBoundingBox3D.create(pt((x0+x1)/2,(y0+y1)/2,(z0+z1)/2),vec(1,0,0),vec(0,1,0),(x1-x0)/10,(y1-y0)/10,(z1-z0)/10)
    return T.createBox(bb)
def cyl(a,b,d): return T.createCylinderOrCone(pt(*a),d/20,pt(*b),d/20)
def sphere(a,d): return T.createSphere(pt(*a),d/20)
def boolean(a,b,op):
    if not T.booleanOperation(a,b,op): raise RuntimeError('BRep boolean failed')
    return a

def union(a,b): return boolean(a,b,U)
def cut(a,b): return boolean(a,b,D)
def join_all(items):
    items=list(items);a=items.pop(0)
    for b in items:union(a,b)
    return a

def zhole(a,x,y,z0,z1,d): return cut(a,cyl((x,y,z0),(x,y,z1),d))
def moved(body,xyz):
    a=T.copy(body);m=C.Matrix3D.create();m.translation=vec(*[v/10 for v in xyz]);T.transform(a,m);return a

def bounds(b):
    bb=b.boundingBox
    return [[v*10 for v in bb.minPoint.asArray()],[v*10 for v in bb.maxPoint.asArray()]]
def intersects_bb(a,b):
    return all(min(a[1][i],b[1][i])-max(a[0][i],b[0][i])>EPS for i in range(3))
def rounded_box(w,d,z,h,r):
    # A single connected solid with true circular vertical corners.
    return join_all([box(-w/2+r,-d/2,z,w/2-r,d/2,z+h),box(-w/2,-d/2+r,z,w/2,d/2-r,z+h)]+[cyl((x,y,z),(x,y,z+h),2*r) for x in [-w/2+r,w/2-r] for y in [-d/2+r,d/2-r]])
def tube_path(points,od):
    # Swept outside-diameter reference, with round segment junctions.
    items=[]
    for a,b in zip(points,points[1:]):
        if math.dist(a,b)>1e-5:items.append(cyl(a,b,od))
    for p in points[1:-1]:items.append(sphere(p,od))
    return join_all(items)
def arc_xz(x,y,z,r,direction,n=12):
    # Starts vertically downward, ends horizontally toward +/- X.
    return [(x+direction*r*(1-math.cos(a)),y,z-r*math.sin(a)) for a in [i*math.pi/2/n for i in range(n+1)]]
def arc_yz(x,y,z,r,direction=1,n=12):
    return [(x,y+direction*r*math.sin(a),z-r*(1-math.cos(a))) for a in [i*math.pi/2/n for i in range(n+1)]]
def arc_xy(cx,cy,z,r,a0,a1,n=12):
    return [(cx+r*math.cos(a0+(a1-a0)*i/n),cy+r*math.sin(a0+(a1-a0)*i/n),z) for i in range(n+1)]

def build_and_export(root):
    root=Path(root);p=json.loads((root/'design/bed_params.json').read_text())
    out=root/'export/2026-11-08_grouped';out.mkdir(parents=True,exist_ok=True)
    meshes=out/'meshes';meshes.mkdir(exist_ok=True)
    log=root/'.cache/grouped-cad/run.log'
    def progress(s):
        with log.open('a') as f:f.write(s+'\n')
        adsk_do()
    g,c,h,f,q,t,s=p['grid'],p['cell'],p['housing'],p['fasteners'],p['guide'],p['tubes'],p['service']
    pitch=g['pitch'];W=g['columns']*pitch+2*g['border'];L=g['rows']*pitch+2*g['border'];H=h['outer_top_z'];B=h['base_t'];wall=h['wall_t'];gap=h['joint_gap'];sd=h['service_depth']
    cup_bottom=c['support_z']-c['cup_floor'];ring_bottom=c['support_z']+c['clamp_gap'];ring_top=ring_bottom+c['ring_thickness'];cap_low=c['lower_cap_underside_z'];cap_high=cap_low+c['stroke'];cb,cby=c['cup_screw_xy'];rb=c['clamp_screw_xy'];gy=q['spacing_half']
    cells=[dict(id=chr(65+col)+str(row+1),x=(col-(g['columns']-1)/2)*pitch,y=g['border']+(row+.5)*pitch,group=g['groups'][row][col],row=row,col=col) for row in range(g['rows']) for col in range(g['columns'])]
    ln={};exec(compile((root/'design/fusion/bed_layout.py').read_text(),str(root/'design/fusion/bed_layout.py'),'exec'),ln);derived=ln['layout'](p)
    assert cells==derived['cells'] and W==derived['width'] and L==derived['field_length']
    app=C.Application.get();doc=app.documents.add(C.DocumentTypes.FusionDesignDocumentType)
    design=F.Design.cast(doc.products.itemByProductType('DesignProductType'));design.designType=F.DesignTypes.ParametricDesignType
    design.attributes.add('BedPrototype','builder','grouped-v1')
    def component(parent,name,where=(0,0,0)):
        mat=C.Matrix3D.create();mat.translation=vec(*[v/10 for v in where])
        o=parent.occurrences.addNewComponent(mat);o.component.name=name;return o,o.component
    ao,asm=component(design.rootComponent,'Assembly_Soft_Lowered')
    po,pr=component(asm,'Printable_Solids');ro,refs=component(asm,'Reference_Hardware_UNVERIFIED');to,tr=component(design.rootComponent,'Reference_TPU_ENVELOPES_NOT_SIMULATION'); optional_o,optional=component(design.rootComponent,'Optional_Cap_System_Hidden')
    components={};instances=[];fixed=[];caps=[];hardware=[];hose_records=[];joint_records=[];bom=[]
    colors={'frame':(200,204,209),'panel':(180,185,192),'cup':(214,217,222),'ring':(126,136,149),'cap1':(68,133,166),'cap2':(202,148,70),'cover':(110,123,139),'pump':(150,157,166),'valve':(75,116,154),'board':(70,130,103),'tube1':(55,131,184),'tube2':(210,148,54),'tpu1':(113,174,197),'tpu2':(219,177,105),'fastener':(100,104,111),'clip':(128,140,151),'cradle':(142,150,161),'splice':(150,160,171)}
    appearances={}
    def appearance(key):
        if key in appearances:return appearances[key]
        # Copy a native material appearance; geometry export does not depend on this.
        try:
            lib=app.materialLibraries.itemByName('Fusion Appearance Library') or app.materialLibraries.itemByName('Fusion 360 Appearance Library')
            base=lib.appearances.itemByName('Plastic - Matte (Gray)')
            if not base:base=lib.appearances.item(0)
            ap=design.appearances.addByCopy(base,'Bed_'+key)
            prop=ap.appearanceProperties.itemById('opaque_albedo')
            if prop:prop.value=C.Color.create(*colors[key],255)
            appearances[key]=ap;return ap
        except Exception:return None
    def register(name,body,kind,where=(0,0,0),qty_ref=False,color=None,parent=None):
        if name not in components:
            if not body or not body.isSolid:raise RuntimeError(name+' is not a solid')
            o,comp=component(parent or (pr if not qty_ref else refs),name,where)
            bf=comp.features.baseFeatures.add();bf.name='Scripted solid from bed_params.json';bf.startEdit()
            saved=comp.bRepBodies.add(body,bf);saved.name=name;bf.finishEdit()
            if name in ['Print_CellCup','Print_ClampRing']:
                level=c['support_z'] if name=='Print_CellCup' else ring_bottom
                es=C.ObjectCollection.create()
                for edge in saved.edges:
                    eb=edge.boundingBox
                    if abs(eb.minPoint.z*10-level)<EPS and abs(eb.maxPoint.z*10-level)<EPS:es.add(edge)
                if es.count:
                    fil=comp.features.filletFeatures.createInput();fil.edgeSetInputs.addConstantRadiusEdgeSet(es,C.ValueInput.createByReal(c['film_edge_radius']/10),False)
                    comp.features.filletFeatures.add(fil).name='Smooth TPU contact R'+str(c['film_edge_radius'])
                    saved=comp.bRepBodies.item(0);body=T.copy(saved)
            ap=appearance(color or kind)
            if ap:saved.appearance=ap
            components[name]={'component':comp,'body':body,'kind':kind,'reference':qty_ref,'first':o}
        else:
            m=C.Matrix3D.create();m.translation=vec(*[v/10 for v in where]);comp=components[name]['component'];o=(parent or (refs if qty_ref else pr)).occurrences.addExistingComponent(comp,m)
        entry={'name':name,'occ':o,'where':list(where),'kind':kind,'reference':qty_ref,'body':moved(components[name]['body'],where)}
        instances.append(entry)
        if qty_ref:hardware.append(entry)
        elif kind.startswith('cap'):caps.append(entry)
        else:fixed.append(entry)
        return entry
    def screw(name,x,y,z,length,direction=1,parent=None):
        # Head is below the starting seat for upward screws, above for downward.
        a=cyl((0,0,0),(0,0,direction*length),2.5)
        union(a,cyl((0,0,-direction*f['head_h']),(0,0,0),f['head_d']))
        entry=register(name,a,'fastener',(x,y,z),True,parent=parent)
        entry['screw_direction']=direction
        return entry
    progress('Building cups, clamps and guided caps')
    cup=box(-c['cup_width']/2,-c['cup_width']/2,cup_bottom,c['cup_width']/2,c['cup_width']/2,c['support_z'])
    for x in [-rb,rb]:
        for y in [-rb,rb]:union(cup,cyl((x,y,c['cup_boss_bottom_z']),(x,y,c['support_z']),c['clamp_boss_d']))
    for x in [-cb,cb]:
        for y in [-cby,cby]:union(cup,cyl((x,y,c['cup_boss_bottom_z']),(x,y,cup_bottom+EPS),c['cup_boss_d']))
    for y in [-gy,gy]:union(cup,cyl((0,y,q['shoulder_z']),(0,y,c['support_z']),q['sleeve_od']))
    zhole(cup,0,0,cup_bottom-EPS,c['support_z']+EPS,c['port_clearance_d'])
    for x in [-rb,rb]:
        for y in [-rb,rb]:zhole(cup,x,y,c['support_z']-f['clamp_pilot_depth'],c['support_z']+EPS,f['pilot_d'])
    for x in [-cb,cb]:
        for y in [-cby,cby]:zhole(cup,x,y,c['cup_boss_bottom_z']-EPS,c['cup_boss_bottom_z']+f['cup_pilot_depth'],f['pilot_d'])
    for y in [-gy,gy]:zhole(cup,0,y,q['shoulder_z']-EPS,c['support_z']+EPS,q['bore_d'])
    ring=box(-c['cup_width']/2,-c['cup_width']/2,ring_bottom,c['cup_width']/2,c['cup_width']/2,ring_top)
    a=c['ring_opening']/2;cut(ring,box(-a,-a,ring_bottom-EPS,a,a,ring_top+EPS))
    for x in [-rb,rb]:
        for y in [-rb,rb]:
            zhole(ring,x,y,ring_bottom-EPS,ring_top+EPS,f['clearance_d']);zhole(ring,x,y,ring_top-f['head_h'],ring_top+EPS,f['head_d'])
    for y in [-gy,gy]:zhole(ring,0,y,ring_bottom-EPS,ring_top+EPS,q['bore_d'])
    for x in [-c['lower_stop_x'],c['lower_stop_x']]:
        for y in [-c['lower_stop_y'],c['lower_stop_y']]:
            sx,sy=c['lower_stop_size'];union(ring,box(x-sx/2,y-sy/2,ring_top-EPS,x+sx/2,y+sy/2,cap_low))
    cap=rounded_box(c['cap_width'],c['cap_width'],cap_high,c['cap_thickness'],c['cap_corner_r'])
    for y in [-gy,gy]:
        union(cap,cyl((0,y,cap_high-q['post_length']),(0,y,cap_high+EPS),q['post_d']))
        zhole(cap,0,y,cap_high-q['post_length']-EPS,cap_high-q['post_length']+q['cap_pilot_depth'],f['pilot_d'])
    for cell in cells:
        x,y=cell['x'],cell['y'];group=cell['group'];where=(x,y,0)
        register('Print_CellCup',cup,'cup',where)
        register('Print_ClampRing',ring,'ring',where)
        e=register('Print_MovingCap_G'+str(group),cap,'cap'+str(group),where,parent=optional);e['cell']=cell['id'];e['group']=group
        for dx in [-rb,rb]:
            for dy in [-rb,rb]:
                seat=ring_top-f['head_h'];screw('Ref_Clamp_M2p5x10',x+dx,y+dy,seat,f['clamp_length'],-1)
                joint_records.append({'interface':'dry_flange_clamp','cell':cell['id'],'xy':[x+dx,y+dy],'seat_z':seat,'screw':'M2.5x10','grip':seat-ring_bottom+c['clamp_gap'],'engagement':f['clamp_length']-(seat-c['support_z'])})
        for dy in [-gy,gy]:
            tip=cap_high-q['post_length'];washer=cyl((0,0,tip-q['washer_t']),(0,0,tip),q['washer_od']);zhole(washer,0,0,tip-q['washer_t']-EPS,tip+EPS,f['clearance_d'])
            register('Ref_StopWasher',washer,'fastener',(x,y+dy,0),True,parent=optional).update(cap_group=group,cell=cell['id'])
            screw('Ref_Stop_M2p5x6',x,y+dy,tip-q['washer_t'],q['stop_screw_length'],1,parent=optional).update(cap_group=group,cell=cell['id'])
    # Two-column, four-row housing subdivision includes the service bay.
    xbands=[(-W/2,0),(0,W/2)];ybands=list(zip([-sd,0]+h['field_split_y'],[0]+h['field_split_y']+[L]))
    # Shared splice coordinates: same table cuts both receivers and each plate.
    splices=[];ins=f['splice_inset'];spw,spl,spt=f['splice_plate'];shx,shy=f['splice_holes']
    for seam in [0]+h['field_split_y']:
        for x0,x1 in xbands:
            for x in ([x0+ins,x1-f['splice_inner_inset']] if x1==0 else [x0+f['splice_inner_inset'],x1-ins]):splices.append({'centre':[x,seam],'axis':'y','z':B})
    for y in f['service_splice_y']:splices.append({'centre':[0,y],'axis':'x','z':f['service_splice_z']})
    for row in range(g['rows']):splices.append({'centre':[0,g['border']+(row+.5)*pitch],'axis':'x','z':B})
    for n,sp in enumerate(splices):
        x,y=sp['centre'];ax=sp['axis'];hx,hy=(spw/2,spl/2) if ax=='y' else (spl/2,spw/2)
        pts=[(x+dx,y+dy) for dx in ([-shx,shx] if ax=='y' else [-shy,shy]) for dy in ([-shy,shy] if ax=='y' else [-shx,shx])]
        sp.update({'bounds':[x-hx,y-hy,x+hx,y+hy],'holes':pts})
        sz=sp['z'];plate=box(x-hx,y-hy,sz,x+hx,y+hy,sz+spt)
        for xx,yy in pts:zhole(plate,xx,yy,sz-EPS,sz+spt+EPS,f['clearance_d']);screw('Ref_Splice_M2p5x10',xx,yy,sz,f['splice_length'])
        register('Print_Splice_'+str(n+1),plate,'splice')
        joint_records.append({'interface':'section_splice','id':n+1,'holes':pts,'seat_z':sz,'screw':'M2.5x10','grip':spt,'engagement':f['splice_length']-spt})
    panel_screws=[]
    progress('Building eight screw-connected lower frames and bottom panels')
    for yi,(Y0,Y1) in enumerate(ybands):
        for xi,(X0,X1) in enumerate(xbands):
            x0=X0+(gap/2 if X0==0 else 0);x1=X1-(gap/2 if X1==0 else 0)
            y0=Y0+(gap/2 if Y0!=-sd else 0);y1=Y1-(gap/2 if Y1!=L else 0)
            top=h['frame_top_z'];mount_top=h['cell_mount_top_z'];frame=box(x0,y0,B,x1,y1,top)
            cut(frame,box(x0+wall,y0+wall,B-EPS,x1-wall,y1-wall,top+EPS))
            # External walls alone reach the common raised top plane.
            if X0==-W/2:union(frame,box(x0,y0,B,x0+wall,y1,H))
            if X1==W/2:union(frame,box(x1-wall,y0,B,x1,y1,H))
            if Y0==-sd:union(frame,box(x0,y0,B,x1,y0+wall,H))
            if Y1==L:union(frame,box(x0,y1-wall,B,x1,y1,H))
            if yi==0:
                if xi==0:cut(frame,box(x1-wall-EPS,y0+wall,B-EPS,x1+EPS,y1-wall,top+EPS))
                else:cut(frame,box(x0-EPS,y0+wall,B-EPS,x0+wall+EPS,y1-wall,top+EPS))
            cell_list=[ce for ce in cells if X0<ce['x']<X1 and Y0<ce['y']<Y1]
            for ce in cell_list:
                for dx in [-cb,cb]:
                    for dy in [-cby,cby]:
                        xx,yy=ce['x']+dx,ce['y']+dy
                        union(frame,cyl((xx,yy,B),(xx,yy,mount_top),h['column_od']))
                        # Web to nearest Y wall carries the post and leaves the port corridor open.
                        edge=y0+wall/2 if yy<(y0+y1)/2 else y1-wall/2
                        union(frame,box(xx-h['column_web_t']/2,min(yy,edge),B,xx+h['column_web_t']/2,max(yy,edge)+EPS,top))
                        zhole(frame,xx,yy,B-EPS,mount_top-h['column_grip'],h['column_tool_d']);zhole(frame,xx,yy,mount_top-h['column_grip']-EPS,mount_top+EPS,f['clearance_d'])
                        screw('Ref_CupJoint_M2p5x10',xx,yy,mount_top-h['column_grip'],f['cup_length'])
                        joint_records.append({'interface':'cup_to_lower_chassis','cell':ce['id'],'xy':[xx,yy],'seat_z':mount_top-h['column_grip'],'screw':'M2.5x10','grip':h['column_grip'],'engagement':f['cup_length']-h['column_grip'],'driver_bore_d':h['column_tool_d']})
            points=[(x0+h['panel_inset'],y0+h['panel_inset']),(x1-h['panel_inset'],y0+h['panel_inset']),(x0+h['panel_inset'],y1-h['panel_inset']),(x1-h['panel_inset'],y1-h['panel_inset'])]
            if yi==0:
                ox=x0+h['panel_inset'] if xi==0 else x1-h['panel_inset']
                points=[(ox,yy) for yy in [y0+h['panel_inset'],y0+sd/3,y0+2*sd/3,y1-h['panel_inset']]]
            panel=box(x0,y0,0,x1,y1,B)
            for sp in splices:
                if sp['z']!=B:continue
                for xx,yy in sp['holes']:
                    if x0<xx<x1 and y0<yy<y1:
                        zhole(panel,xx,yy,B-f['splice_head_pocket_depth'],B+EPS,f['splice_head_pocket_d'])
            for xx,yy in points:
                union(frame,cyl((xx,yy,B),(xx,yy,B+h['panel_boss_h']),h['panel_boss_d']))
                # Connect receiving bosses to their nearest outside edge.
                edge=x0+wall/2 if xx<(x0+x1)/2 else x1-wall/2
                union(frame,box(min(xx,edge),yy-wall/2,B,max(xx,edge)+EPS,yy+wall/2,B+h['panel_boss_h']))
                zhole(frame,xx,yy,B-EPS,B+h['panel_boss_h']-1,f['pilot_d']);zhole(panel,xx,yy,-EPS,B+EPS,f['clearance_d'])
                # Recessed heads preserve a truly flat bottom datum.
                zhole(panel,xx,yy,-EPS,f['head_h'],f['head_d']);screw('Ref_Panel_M2p5x10',xx,yy,f['head_h'],f['panel_length'])
                joint_records.append({'interface':'bottom_panel','tile':[xi,yi],'xy':[xx,yy],'seat_z':f['head_h'],'screw':'M2.5x10','grip':B-f['head_h'],'engagement':f['panel_length']-(B-f['head_h'])})
            # Group trunks cross horizontal tile joints in matching open passages.
            for group in [1,2]:
                xx=t['group_x'][str(group)];zz=t['group_z'][str(group)]
                if x0<xx<x1:
                    cutlo=max(y0-EPS,-wall-gap-EPS);cuthi=min(y1+EPS,cells[-1]['y']+t['clip_offset_y']+t['clip_foot'][1])
                    passw=t['service_front_passage_width'] if yi==0 else t['passage_width']
                    if cuthi>cutlo:cut(frame,box(xx-passw/2,cutlo,zz-t['passage_height']/2,xx+passw/2,cuthi,zz+t['passage_height']/2))
            # Horizontal cell branches cross the centre seam.
            for ce in cell_list:
                zz=t['group_z'][str(ce['group'])];rail_y=ce['y']+t['group_lane_sign'][str(ce['group'])]*2*t['minimum_bend_radius_assumed']
                passx0,passx1=(x1-wall-EPS,x1+EPS) if xi==0 else (x0-EPS,x0+wall+EPS)
                cut(frame,box(passx0,rail_y-t['passage_height']/2,zz-t['passage_height']/2,passx1,rail_y+t['passage_height']/2,zz+t['passage_height']/2))
            for sp in splices:
                a,b,cc,dd=sp['bounds'];sz=sp['z'];padtop=sz+spt+(f['splice_pad_top_z']-B-spt)
                if min(x1,cc)>max(x0,a) and min(y1,dd)>max(y0,b):
                    for xx,yy in sp['holes']:
                        if x0<xx<x1 and y0<yy<y1:
                            pad=cyl((xx,yy,sz),(xx,yy,padtop),f['splice_pad_d'])
                            boolean(pad,box(x0,y0,sz-EPS,x1,y1,padtop+EPS),I);union(frame,pad)
                            if yi==0 and sz>B:
                                edge=y0+wall/2 if yy<(y0+y1)/2 else y1-wall/2
                                union(frame,box(xx-wall/2,min(edge,yy),sz,xx+wall/2,max(edge,yy)+EPS,padtop))
                                # Bridge around the splice recess to a supported perimeter post.
                                support_offset=h['cover_front_inner_axis'] if sp['centre'][1]>-sd/2 else spl/2+wall*6
                                supportx=-support_offset if xi==0 else support_offset
                                union(frame,box(min(supportx,xx)-wall/2,edge-f['splice_pad_d']/2,sz,max(supportx,xx)+wall/2,edge+f['splice_pad_d']/2,padtop))
                                supporty=-h['cover_front_inset'] if sp['centre'][1]>-sd/2 else edge
                                if supporty!=edge:union(frame,box(supportx-wall/2,min(supporty,edge)-wall/2,sz,supportx+wall/2,max(supporty,edge)+wall/2,padtop))
                                support=box(supportx-wall/2,supporty-wall/2,B,supportx+wall/2,supporty+wall/2,padtop)
                                boolean(support,box(x0,y0,B-EPS,x1,y1,padtop+EPS),I);union(frame,support)
                            elif sp['axis']=='y':
                                edge=y0+wall/2 if abs(yy-y0)<abs(yy-y1) else y1-wall/2
                                union(frame,box(xx-wall/2,min(edge,yy),B,xx+wall/2,max(edge,yy)+EPS,padtop))
                            else:
                                edge=x0+wall/2 if abs(xx-x0)<abs(xx-x1) else x1-wall/2
                                union(frame,box(min(edge,xx),yy-wall/2,B,max(edge,xx)+EPS,yy+wall/2,padtop))
                            zhole(frame,xx,yy,sz+spt-EPS,sz+f['splice_length']+1,f['pilot_d'])
                    cut(frame,box(a,b,sz-EPS,cc,dd,sz+spt))
                    if yi==0 and sp['axis']=='x' and sp['centre'][1]>-sd/2:
                        cut(frame,box(a,y1-wall*5,B-EPS,cc,y1+EPS,sz+EPS))
            if yi==0:
                # Removable fixed cover: four shared receiving positions per half.
                cover_xs=[-h['cover_outer_axis'],-h['cover_inner_axis']] if xi==0 else [h['cover_inner_axis'],h['cover_outer_axis']]
                cp=[(xx,y0+h['cover_rear_inset']) for xx in cover_xs]
                front_xs=[-h['cover_outer_axis'],-h['cover_front_inner_axis']] if xi==0 else [h['cover_front_inner_axis'],h['cover_outer_axis']]
                cp += [(xx,y1-h['cover_front_inset']) for xx in front_xs]
                cover=box(x0+(wall+gap if X0==-W/2 else 0),y0+wall+gap,H-h['service_cover_t'],x1-(wall+gap if X1==W/2 else 0),y1,H)
                cover_base=H-h['service_cover_t']
                cover_seat=H-h['cover_head_recess']
                grip=cover_seat-cover_base
                engagement=f['cover_length']-grip
                assert 0<engagement<h['cover_boss_h']-1
                cover_lo,cover_hi=bounds(cover)
                recess_d=f['head_d']+.5
                for xx,yy in cp:
                    edge_distance=min(xx-cover_lo[0],cover_hi[0]-xx,yy-cover_lo[1],cover_hi[1]-yy)
                    assert edge_distance>=recess_d/2+1, (xx,yy,edge_distance)
                    receiver_bottom=cover_base-h['cover_boss_h']
                    boss=cyl((xx,yy,receiver_bottom),(xx,yy,cover_base),h['cover_boss_d'])
                    boolean(boss,box(*bounds(cover)[0][:2],receiver_bottom-EPS,*bounds(cover)[1][:2],H),I)
                    # Keep each receiving boss tied to the existing chassis support.
                    flange_z=receiver_bottom-3
                    if abs(xx)>W/4:
                        edge=x0+wall/2 if xi==0 else x1-wall/2
                        flange=box(min(edge,xx),yy-h['cover_boss_d']/2,flange_z,max(edge,xx),yy+h['cover_boss_d']/2,receiver_bottom)
                    else:
                        edge=y0+wall/2 if yy<(y0+y1)/2 else y1-wall/2
                        flange=box(xx-h['cover_boss_d']/2,min(edge,yy),flange_z,xx+h['cover_boss_d']/2,max(edge,yy),receiver_bottom)
                        if yy>(y0+y1)/2:
                            union(frame,cyl((xx,yy,B),(xx,yy,receiver_bottom),h['cover_boss_d']))
                            union(frame,box(xx-wall/2,min(yy,edge),B,xx+wall/2,max(yy,edge)+EPS,B+h['cover_support_t']))
                    union(frame,flange);union(frame,boss)
                    zhole(frame,xx,yy,cover_base-engagement-1,cover_base+EPS,f['pilot_d'])
                    zhole(cover,xx,yy,cover_base-EPS,H+EPS,f['clearance_d'])
                    zhole(cover,xx,yy,cover_seat,H+EPS,recess_d)
                    screw('Ref_Cover_M2p5x8',xx,yy,cover_seat,f['cover_length'],-1)
                    joint_records.append({'interface':'service_cover','xy':[xx,yy],'seat_z':cover_seat,'screw':'M2.5x8','grip':grip,'engagement':engagement,'drive':'top'})
                # Slot ventilation in the bottom panel.
                for vi in range(8):
                    vx=x0+(vi+1)*(x1-x0)/9
                    cut(panel,box(vx-wall/2,(y0+y1)/2-8,-EPS,vx+wall/2,(y0+y1)/2+8,B+EPS))
                if xi==1:
                    px,py,pz=s['power_entry_centre'];cut(frame,cyl((px,py-wall,pz),(px,py+wall*2,pz),s['power_entry_d']))
                    ux0,ux1,uz0,uz1=s['usb_window'];cut(frame,box(ux0,py-EPS,uz0,ux1,py+wall+EPS,uz1))
                # Keep raised splice supports inside the rectangular chassis outline.
                boolean(frame,box(x0,y0,B-EPS,x1,y1,H+EPS),I)
                register('Print_ServiceCover_'+str(xi+1),cover,'cover')
            # Later joint/boss additions must not fill the cup screwdriver bores.
            for ce in cell_list:
                for dx in [-cb,cb]:
                    for dy in [-cby,cby]:
                        zhole(frame,ce['x']+dx,ce['y']+dy,B-EPS,mount_top-h['column_grip'],h['column_tool_d'])
                        zhole(frame,ce['x']+dx,ce['y']+dy,mount_top-h['column_grip']-EPS,mount_top+EPS,f['clearance_d'])
            register('Print_LowerFrame_'+str(xi+1)+'_'+str(yi+1),frame,'frame')
            register('Print_BottomPanel_'+str(xi+1)+'_'+str(yi+1),panel,'panel')
    progress('Building eight adjustable pump cradles and service hardware')
    # Cradle feet react against isolation washers above the removable base.
    pl,pw,ph=s['cradle_plate'];pz=s['cradle_plate_z'];mx,my=s['cradle_mount_xy'];axisz=s['pump_axis_z']
    cradle=box(-pl/2,-pw/2,pz,pl/2,pw/2,pz+ph)
    for xx in [-mx,mx]:
        for yy in [-my,my]:union(cradle,cyl((xx,yy,s['pump_feet_z']),(xx,yy,pz+ph),s['pump_foot_d']));zhole(cradle,xx,yy,s['pump_feet_z']-EPS,pz+ph+EPS,f['pilot_d'])
    for xx in [-s['cradle_saddle_x'],s['cradle_saddle_x']]:
        st=s['cradle_saddle_t'];union(cradle,box(xx-st/2,-pw/2,pz+ph-EPS,xx+st/2,pw/2,axisz))
        cut(cradle,cyl((xx-st/2-EPS,0,axisz),(xx+st/2+EPS,0,axisz),s['cradle_bore_d']))
        for yy in [-pw/2+s['strap_slot'][1],pw/2-s['strap_slot'][1]]:
            cut(cradle,box(xx-s['strap_slot'][0]/2,yy-s['strap_slot'][1]/2,pz-EPS,xx+s['strap_slot'][0]/2,yy+s['strap_slot'][1]/2,pz+ph+EPS))
    for nx,ny in s['cradle_tool_notches']:zhole(cradle,nx,ny,s['pump_feet_z']-EPS,axisz+EPS,h['column_tool_d'])
    pump=cyl((-s['pump_reference_length']/2,0,axisz),(s['pump_reference_length']/2,0,axisz),s['pump_reference_diameter'])
    union(pump,cyl((s['pump_reference_length']/2,0,axisz),(s['pump_reference_length']/2+t['cross_port_length'],0,axisz),t['port_barb_od']))
    ambient_z=axisz-s['ambient_port_drop']
    union(pump,cyl((s['pump_reference_length']/2,0,ambient_z),(s['pump_reference_length']/2+t['cross_port_length'],0,ambient_z),t['port_barb_od']))
    for col,xx in enumerate(s['pump_centres_x']):
        for row,yy in enumerate(s['pump_centres_y']):
            register('Print_PumpCradle',cradle,'cradle',(xx,yy,0));e=register('Ref_Pump_'+s['pump_bank_by_column'][col],pump,'pump',(xx,yy,0),True);e['bank']=s['pump_bank_by_column'][col]
            for dx in [-mx,mx]:
                for dy in [-my,my]:
                    # Drill the corresponding removable service panel, not an unrelated solid.
                    panel_entry=next(en for en in fixed if en['name'].startswith('Print_BottomPanel_') and bounds(en['body'])[0][0]<xx+dx<bounds(en['body'])[1][0] and bounds(en['body'])[0][1]<yy+dy<bounds(en['body'])[1][1])
                    # Panel details are added in a second BRep edit below, before export.
                    panel_screws.append((panel_entry['name'],xx+dx,yy+dy,'pump'))
                    screw('Ref_PumpMount_M2p5x8',xx+dx,yy+dy,f['head_h'],f['pump_length'])
    # Two replaceable slotted PCB trays, with generic board/connector envelopes.
    tx,ty,th=s['board_tray'];bx,by=s['board_centre'];mounts=s['board_mount_half']
    for level,z in enumerate(s['board_tray_levels']):
        tray=box(bx-tx/2,by-ty/2,z,bx+tx/2,by+ty/2,z+th)
        for dx in [-mounts[0],mounts[0]]:
            for dy in [-mounts[1],mounts[1]]:
                # Rounded slots permit changing carrier/driver boards without guessed Uno holes.
                zz=z-EPS;slot=s['board_slot_length'];r=f['clearance_d']/2
                cutter=join_all([box(bx+dx-slot/2,by+dy-r,zz,bx+dx+slot/2,by+dy+r,z+th+EPS),cyl((bx+dx-slot/2,by+dy,zz),(bx+dx-slot/2,by+dy,z+th+EPS),f['clearance_d']),cyl((bx+dx+slot/2,by+dy,zz),(bx+dx+slot/2,by+dy,z+th+EPS),f['clearance_d'])]);cut(tray,cutter)
        # Four legs connect to the base; no assumed purchased-board hole coordinates.
        legx,legy=s['lower_tray_leg_half'] if level==0 else s['upper_tray_leg_half']
        legbottom=B if level==0 else s['board_tray_levels'][0]+th
        for dx in [-legx,legx]:
            for dy in [-legy,legy]:
                union(tray,cyl((bx+dx,by+dy,legbottom),(bx+dx,by+dy,z+EPS),f['splice_pad_d']))
                zhole(tray,bx+dx,by+dy,legbottom-EPS,min(legbottom+8,z+th-EPS),f['pilot_d'])
                if level==0:panel_screws.append(('Print_BottomPanel_2_1',bx+dx,by+dy,'tray'))
                else:
                    screw('Ref_TrayStack_M2p5x10',bx+dx,by+dy,s['board_tray_levels'][0],10)
                    joint_records.append({'interface':'pcb_tray_stack','xy':[bx+dx,by+dy],'seat_z':s['board_tray_levels'][0],'screw':'M2.5x10','grip':th,'engagement':10-th,'assembly':'preassemble trays before boards and bottom-panel mounting'})
        if level==0:
            # Through holes for the upper-tray screws, with head relief where
            # the neighbouring lower feet would otherwise obstruct the heads.
            for dx in [-s['upper_tray_leg_half'][0],s['upper_tray_leg_half'][0]]:
                for dy in [-s['upper_tray_leg_half'][1],s['upper_tray_leg_half'][1]]:
                    zhole(tray,bx+dx,by+dy,z-EPS,z+th+EPS,f['clearance_d'])
                    zhole(tray,bx+dx,by+dy,B-EPS,z+EPS,f['head_d']+.5)
        for yy in [-sd+h['panel_inset'],-2*sd/3,-sd/3,-h['panel_inset']]:
            cut(tray,cyl((W/2-h['panel_inset'],yy,B-EPS),(W/2-h['panel_inset'],yy,z+th+EPS),h['panel_boss_d']+2))
        notchx=W/2-h['panel_inset']-(h['panel_boss_d']+2)/2
        cut(tray,box(notchx,-sd-EPS,B-EPS,W/2+EPS,-sd+h['panel_inset']+(h['panel_boss_d']+2)/2,z+th+EPS))
        for xx in [h['cover_inner_axis'],h['cover_outer_axis']]:zhole(tray,xx,-sd+s['board_rear_relief_inset'],B-EPS,z+th+EPS,h['column_tool_d'])
        rx0,rx1,ry=s['wire_tray_relief'];cut(tray,box(rx0,-sd-EPS,z-EPS,rx1,ry,z+th+EPS))
        register('Print_ElectronicsTray_'+str(level+1),tray,'cradle')
        bw,bd,bt=s['board_reference'];board=box(bx-bw/2,by-bd/2,z+th+wall,bx+bw/2,by+bd/2,z+th+wall+bt)
        register('Ref_ControllerCarrier' if level==0 else 'Ref_SixChannelPowerDriver',board,'board',qty_ref=True)
    # A slotted four-valve carrier, with two physically distinct valve pairs.
    vx,vy=s['valve_mount_centre'];vl,vw,vt=s['valve_mount_plate'];vz=s['valve_mount_z'];vp=box(vx-vl/2,vy-vw/2,vz,vx+vl/2,vy+vw/2,vz+vt)
    for xx,yy in s['valve_centres']:
        for dx in [-s['valve_keepout'][0]/2+wall,s['valve_keepout'][0]/2-wall]:
            cut(vp,box(xx+dx-f['clearance_d']/2,yy-s['valve_slot_length']/2,vz-EPS,xx+dx+f['clearance_d']/2,yy+s['valve_slot_length']/2,vz+vt+EPS))
    for dx in [-vl/2+f['splice_pad_d']/2+1,vl/2-f['splice_pad_d']/2-1]:
        for dy in [-vw/2+f['splice_pad_d']/2+1,vw/2-f['splice_pad_d']/2-1]:
            union(vp,cyl((vx+dx,vy+dy,B),(vx+dx,vy+dy,vz+EPS),f['splice_pad_d']));zhole(vp,vx+dx,vy+dy,B-EPS,vz+vt-1,f['pilot_d']);panel_screws.append(('Print_BottomPanel_2_1',vx+dx,vy+dy,'tray'))
    for yy in [-sd+h['panel_inset'],-2*sd/3,-sd/3,-h['panel_inset']]:cut(vp,cyl((W/2-h['panel_inset'],yy,B-EPS),(W/2-h['panel_inset'],yy,vz+vt+EPS),h['panel_boss_d']+2))
    for xx in [h['cover_front_inner_axis'],h['cover_outer_axis']]:zhole(vp,xx,-h['cover_front_inset'],B-EPS,vz+vt+EPS,h['cover_boss_d']+2)
    register('Print_ValveCarrier',vp,'cradle')
    for (xx,yy),name in zip(s['valve_centres'],s['valve_ids']):
        dw,dl,dh=s['valve_envelope'];vb=box(xx-dw/2,yy-dl/2,s['valve_z'],xx+dw/2,yy+dl/2,s['valve_z']+dh)
        half=dw/2;barb=t['cross_port_length'];portz=s['valve_port_z']
        union(vb,cyl((xx-half-barb,yy,portz),(xx+half+barb,yy,portz),t['port_barb_od']))
        register('Ref_Valve_'+name,vb,'valve',qty_ref=True)
    progress('Building group trunks, twelve cell branches and supported ports')
    for group in [1,2]:
        gx=t['group_x'][str(group)];gz=t['group_z'][str(group)];od=t['od'];r=t['minimum_bend_radius_assumed'];sy=t['group_lane_sign'][str(group)]
        first=g['border']+pitch/2+sy*2*r;last=g['border']+(g['rows']-.5)*pitch+sy*2*r
        pts=[(gx,first,gz),(gx,last,gz)];register('Ref_G'+str(group)+'_Trunk',tube_path(pts,od),'tube'+str(group),qty_ref=True)
        hose_records.append({'id':'G'+str(group)+' trunk','group':group,'points':pts,'od':od,'id_mm':t['id'],'length_mm':math.dist(*pts)})
        for ce in [ce for ce in cells if ce['group']==group]:
            xx,yy=ce['x'],ce['y'];direction=1 if gx>xx else -1;startz=gz+r;rail_y=yy+sy*2*r
            pts=[(xx,yy,c['support_z'])]+[(xx,yy+sy*r*(1-math.cos(i*math.pi/24)),startz-r*math.sin(i*math.pi/24)) for i in range(13)]
            a0=math.pi if direction>0 else 0;a1=a0-sy*direction*math.pi/2
            pts+=arc_xy(xx+direction*r,yy+sy*r,gz,r,a0,a1)[1:];pts.append((gx,rail_y,gz))
            register('Ref_Hose_'+ce['id']+'_G'+str(group),tube_path(pts,od),'tube'+str(group),qty_ref=True)
            hose_records.append({'id':ce['id'],'group':group,'points':pts,'od':od,'id_mm':t['id'],'bend_radius_mm':r,'length_mm':c['support_z']-startz+r*math.pi+abs(gx-pts[-2][0])})
            stem=cyl((xx,yy,c['support_z']-t['port_insertion']),(xx,yy,c['support_z']),t['fitting_stem_od']);union(stem,cyl((xx,yy,c['support_z']),(xx,yy,c['support_z']+c['film_ply']),c['weld_port_flange_d']))
            register('Ref_SupportedWeldPort_'+ce['id'],stem,'valve',qty_ref=True)
        for row in range(g['rows']):
            yy=g['border']+(row+.5)*pitch+sy*2*r;d=t['cross_body'];cross=box(gx-d/2,yy-d/2,gz-d/2,gx+d/2,yy+d/2,gz+d/2)
            union(cross,cyl((gx-t['cross_port_length'],yy,gz),(gx+t['cross_port_length'],yy,gz),t['port_barb_od']));union(cross,cyl((gx,yy-t['cross_port_length'],gz),(gx,yy+(d/2 if row==g['rows']-1 else t['cross_port_length']),gz),t['port_barb_od']))
            fitting='TerminalTee' if row==g['rows']-1 else 'Cross'
            register('Ref_G'+str(group)+'_'+fitting+'_'+str(row+1),cross,'valve',qty_ref=True)
            clip_offset=t['group_clip_offset'][str(group)]
            terminal=row==g['rows']-1
            clip_panel_row=row+2
            if terminal and group==2:
                clip_offset=-(pitch/2+6)
                clip_panel_row-=1
            cy=yy+clip_offset;fw,fd,fh=t['clip_foot'];cl=t['clip_body_length'];outside=-1 if group==1 else 1
            fx0=gx-t['clip_inner_extent'] if outside>0 else gx-t['clip_outer_extent'];fx1=gx+t['clip_outer_extent'] if outside>0 else gx+t['clip_inner_extent']
            clip=box(fx0,cy-fd/2,B,fx1,cy+fd/2,B+fh)
            union(clip,cyl((gx,cy-cl/2,gz),(gx,cy+cl/2,gz),t['clip_outer_d']))
            if gz-t['clip_outer_d']/2>B+fh:union(clip,box(gx-wall/2,cy-fd/2,B+fh-EPS,gx+wall/2,cy+fd/2,gz))
            cut(clip,cyl((gx,cy-fd/2-EPS,gz),(gx,cy+fd/2+EPS,gz),t['clip_bore']))
            cut(clip,box(gx-t['clip_mouth']/2,cy-fd/2-EPS,gz,gx+t['clip_mouth']/2,cy+fd/2+EPS,gz+t['clip_outer_d']))
            for dy in sorted(set([-t['clip_mount_y'],t['clip_mount_y']])):
                mx=gx+outside*t['clip_screw_half'];my=cy+dy;zhole(clip,mx,my,B-EPS,B+fh-.2,f['pilot_d'])
                panelname='Print_BottomPanel_'+str(1 if gx<0 else 2)+'_'+str(clip_panel_row);panel_screws.append((panelname,mx,my,'clip'));screw('Ref_Clip_M2p5x6',mx,my,f['head_h'],f['clip_length'])
            register('Print_TubeClip_G'+str(group)+'_R'+str(row+1),clip,'clip')
    # Complete shared pressure/extraction distribution and two group routes.
    # All service hose bends use the same explicit, unverified R12 assumption.
    r=t['minimum_bend_radius_assumed'];od=t['od'];vtop=s['valve_z']+s['valve_envelope'][2];portz=s['valve_port_z']
    over=max(vtop+od/2+s['hose_over_valve_clearance'],portz+r+t['port_insertion']);tee_x=(s['valve_centres'][0][0]+s['valve_centres'][1][0])/2;front=s['service_front_hose_y'];dropx=s['group_drop_x']
    def add_hose(name,points,kind,**meta):
        # Remove coincident adjacent path samples before creating the OD solid.
        clean=[]
        for point in points:
            if not clean or math.dist(clean[-1],point)>1e-5:clean.append(point)
        register(name,tube_path(clean,od),kind,qty_ref=True)
        hose_records.append(dict(id=name,points=clean,od=od,id_mm=t['id'],minimum_bend_radius_assumed=r,length_mm=sum(math.dist(a,b) for a,b in zip(clean,clean[1:])),**meta))
    def offset_s(start,forward,side,amount):
        if amount<1e-8:return [start]
        if amount>2*r:
            points=[tuple(start[k]+forward[k]*r*math.sin(i*math.pi/24)+side[k]*r*(1-math.cos(i*math.pi/24)) for k in range(3)) for i in range(13)]
            corner=tuple(points[-1][k]+side[k]*(amount-2*r) for k in range(3));points.append(corner)
            points += [tuple(corner[k]+forward[k]*r*(1-math.cos(i*math.pi/24))+side[k]*r*math.sin(i*math.pi/24) for k in range(3)) for i in range(1,13)]
            return points
        theta=math.acos(1-amount/(2*r));points=[]
        for i in range(13):
            u=theta*i/12;d=r*math.sin(u);v=r*(1-math.cos(u));points.append(tuple(start[k]+forward[k]*d+side[k]*v for k in range(3)))
        for i in range(1,13):
            u=theta*i/12;d=r*math.sin(theta)+r*(math.sin(theta)-math.sin(theta-u));v=r*(1-math.cos(theta))+r*(math.cos(theta-u)-math.cos(theta));points.append(tuple(start[k]+forward[k]*d+side[k]*v for k in range(3)))
        return points
    pump_header_x=[]
    for col,bank in enumerate(s['pump_bank_by_column']):
        zz=s['pressure_bus_z'] if bank=='pressure' else s['suction_bus_z'];nozzle_x=s['pump_centres_x'][col]+s['pump_reference_length']/2+t['cross_port_length'];hx=nozzle_x+r;pump_header_x.append(hx)
        add_hose('Ref_'+bank+'_PumpHeader',[(hx,s['pump_centres_y'][0],zz),(hx,s['bus_y'],zz)],'tube1' if col==0 else 'tube2')
        for row,yy in enumerate(s['pump_centres_y']):
            points=[(nozzle_x+r*math.sin(i*math.pi/24),yy,s['pump_axis_z']+r*(1-math.cos(i*math.pi/24))) for i in range(13)]
            points.append((hx,yy,zz));add_hose('Ref_'+bank+'_PumpBranch_'+str(row+1),points,'tube1' if col==0 else 'tube2')
    fill_header_x=t['group_x']['2']-s['fill_header_offset'];extract_header_x=s['valve_centres'][1][0]+s['valve_envelope'][0]/2+t['cross_port_length']+r
    for name,hx,hz,startx,kind in [('Pressure',fill_header_x,s['pressure_bus_z'],pump_header_x[0],'tube1'),('Suction',extract_header_x,s['suction_bus_z'],pump_header_x[1],'tube2')]:
        add_hose('Ref_'+name+'Bus',[(startx,s['bus_y'],hz),(hx,s['bus_y'],hz)],kind)
        add_hose('Ref_'+name+'ValveHeader',[(hx,s['valve_centres'][2][1],hz),(hx,s['bus_y'],hz)],kind)
    for group in [1,2]:
        yy=s['valve_centres'][(group-1)*2][1];gz=t['group_z'][str(group)];gx=t['group_x'][str(group)]
        fx=s['valve_centres'][(group-1)*2][0];ex=s['valve_centres'][(group-1)*2+1][0];barb=t['cross_port_length'];half=s['valve_envelope'][0]/2
        # Fill valve uses its left inlet; extraction valve uses its right outlet.
        for name,hx,hz,endx,direction,kind in [('Fill',fill_header_x,s['pressure_bus_z'],fx-half-barb,1,'tube1'),('Extract',extract_header_x,s['suction_bus_z'],ex+half+barb,-1,'tube2')]:
            points=[(hx,yy,hz),(hx,yy,portz+r)]+arc_xz(hx,yy,portz+r,r,direction)[1:]+[(endx,yy,portz)]
            add_hose('Ref_G'+str(group)+'_'+name+'BusConnection',points,kind)
        # Nominal commercial tee. The purchased part remains to be measured.
        half_body=t['cross_body']/2
        tee=box(tee_x-half_body,yy-half_body,portz-half_body,tee_x+half_body,yy+half_body,portz+half_body)
        union(tee,cyl((tee_x-barb,yy,portz),(tee_x+barb,yy,portz),t['port_barb_od']))
        branch_end=(tee_x,yy+barb,portz) if group==1 else (tee_x,yy,portz+barb)
        union(tee,cyl((tee_x,yy,portz),branch_end,t['port_barb_od']))
        register('Ref_G'+str(group)+'_ServiceTee',tee,'valve',qty_ref=True)
        add_hose('Ref_G'+str(group)+'_FillToTee',[(fx+half,yy,portz),(tee_x,yy,portz)],'tube'+str(group))
        add_hose('Ref_G'+str(group)+'_TeeToExtract',[(tee_x,yy,portz),(ex-half,yy,portz)],'tube'+str(group))
        if group==1:
            points=[(tee_x,yy,portz),(tee_x,front-r,portz)]+arc_xy(tee_x-r,front-r,portz,r,0,math.pi/2)[1:]
            # Keep the existing service-side crossing under the elevated cell mount.
            old_cup_bottom=cup_bottom-(h['cell_mount_top_z']-h['frame_top_z'])
            crossz=(h['frame_top_z']+old_cup_bottom)/2;points+=offset_s(points[-1],(-1,0,0),(0,0,-1),portz-crossz)[1:]
            points.append((gx+r,front,crossz));points+=arc_xy(gx+r,front+r,crossz,r,-math.pi/2,-math.pi)[1:]
            points.append((gx,s['group1_field_drop_y'],crossz));points+=offset_s(points[-1],(0,1,0),(0,0,-1),crossz-gz)[1:]
            points.append((gx,cells[0]['y']+t['group_lane_sign'][str(group)]*2*r,gz))
        else:
            points=[(tee_x,yy,portz),(tee_x,yy,over-r)]
            points += [(tee_x-r*(1-math.cos(i*math.pi/24)),yy,over-r+r*math.sin(i*math.pi/24)) for i in range(1,13)]
            points.append((dropx+r,yy,over));points+=arc_xy(dropx+r,yy+r,over,r,-math.pi/2,-math.pi)[1:]
            points+=offset_s(points[-1],(0,1,0),(0,0,-1),over-gz)[1:]
            points.append((dropx,s['group2_lateral_shift_y'],gz))
            points+=offset_s(points[-1],(0,1,0),(-1,0,0),dropx-gx)[1:];points.append((gx,cells[0]['y']+t['group_lane_sign'][str(group)]*2*r,gz))
        add_hose('Ref_G'+str(group)+'_ServiceRoute',points,'tube'+str(group))
    # Commercial connector keep-outs at every header corner and branch node.
    for col,bank in enumerate(s['pump_bank_by_column']):
        hz=s['pressure_bus_z'] if bank=='pressure' else s['suction_bus_z'];hx=pump_header_x[col];vhx=fill_header_x if bank=='pressure' else extract_header_x;d=s['header_fitting_body'];network_kind='tube1' if col==0 else 'tube2'
        nodes=[(hx,yy,hz) for yy in s['pump_centres_y']]+[(hx,s['bus_y'],hz),(vhx,s['bus_y'],hz)]+[(vhx,s['valve_centres'][i][1],hz) for i in [0,2]]
        for ni,(xx,yy,zz) in enumerate(nodes):
            body=box(xx-d/2,yy-d/2,zz-d/2,xx+d/2,yy+d/2,zz+d/2)
            register('Ref_'+bank+'_HeaderFitting_'+str(ni+1),body,'valve',qty_ref=True)
    # TPU reference envelopes: not a simulated membrane or a printable part.
    for ce in cells:
        group=ce['group'];height=cap_high-c['support_z'];bl=rounded_box(c['active_width'],c['active_width'],c['support_z'],height,c['active_corner_r'])
        register('Ref_TPU_G'+str(group)+'_Raised',bl,'tpu'+str(group),(ce['x'],ce['y'],0),True,parent=tr)
    # Add all panel mounting holes from the shared hardware coordinate table.
    for name,xx,yy,kind in panel_screws:
        if kind=='tray':screw('Ref_TrayPanel_M2p5x6',xx,yy,f['head_h'],6)
        elif kind=='pump':
            washer=cyl((0,0,B),(0,0,s['pump_feet_z']),s['pump_foot_d']);zhole(washer,0,0,B-EPS,s['pump_feet_z']+EPS,f['clearance_d'])
            register('Ref_IsolationWasher',washer,'fastener',(xx,yy,0),True)
        body=components[name]['body'];zhole(body,xx,yy,-EPS,B+EPS,f['clearance_d']);zhole(body,xx,yy,-EPS,f['head_h'],f['head_d'])
    # Update bodies changed after registration and local copies used by checks.
    for name,data in components.items():
        if name.startswith('Print_BottomPanel'):
            comp=data['component'];bf=comp.features.baseFeatures.item(0);bf.startEdit();bf.updateBody(bf.bodies.item(0),data['body']);bf.finishEdit()
            for en in fixed:
                if en['name']==name:en['body']=moved(data['body'],en['where'])
    progress('Checking print solids and cap travel')
    reserved=h['spare_route']
    route_half=reserved['width']/2
    route_z0=reserved['bottom_z'];route_z1=route_z0+reserved['height']
    spare_routes={}
    for ce in cells[:g['columns']]:
        x=ce['x']+reserved['longitudinal_x_offset']
        route_start_y=5 if ce['id']=='B1' else -3
        spare_routes['Longitudinal_'+ce['id'][0]]=box(x-route_half,route_start_y,route_z0,x+route_half,L-8,route_z1)
    for ce in cells[::g['columns']]:
        y=ce['y']+reserved['transverse_y_offset']
        spare_routes['Transverse_'+str(ce['row']+1)]=box(-W/2+8,y-route_half,route_z0,W/2-8,y+route_half,route_z1)
    spare_route_hits=[]
    for name,route in spare_routes.items():
        route_bounds=bounds(route)
        for part in fixed+hardware:
            if not intersects_bb(route_bounds,bounds(part['body'])):continue
            overlap=T.copy(route)
            if T.booleanOperation(overlap,T.copy(part['body']),I) and overlap.volume*1000>p['validation']['interference_volume_tolerance_mm3']:
                spare_route_hits.append({'route':name,'part':part['name'],'volume_mm3':overlap.volume*1000})
    progress('Spare under-cell route checks: '+str(spare_route_hits))
    # Solid intersections are checked in the actual raised arrangement, with
    # separate reports for reference keep-outs and sampled moving-cap positions.
    def collisions(entries):
        collisions=[];bbs=[bounds(en['body']) for en in entries]
        for i,a in enumerate(entries):
            for j in range(i):
                if not intersects_bb(bbs[i],bbs[j]):continue
                body=T.copy(a['body'])
                if T.booleanOperation(body,T.copy(entries[j]['body']),I):
                    v=body.volume*1000
                    if v>p['validation']['interference_volume_tolerance_mm3']:collisions.append({'a':a.get('cell',a['name']),'b':entries[j].get('cell',entries[j]['name']),'volume_mm3':v})
        return collisions
    interference=collisions(fixed+caps)
    progress('Print-part intersection check: '+str(len(interference)))
    motion=[]
    for offset in range(0,int(c['stroke'])+1,int(p['validation']['clearance_sample_mm'])):
        if offset==0:continue
        for ca in caps:
            body=moved(ca['body'],(0,0,-offset));bb=bounds(body)
            for fi in fixed:
                if not intersects_bb(bb,bounds(fi['body'])):continue
                inter=T.copy(body)
                if T.booleanOperation(inter,T.copy(fi['body']),I) and inter.volume*1000>p['validation']['interference_volume_tolerance_mm3']:
                    motion.append({'cell':ca['cell'],'below_upper_mm':offset,'fixed':fi['name'],'volume_mm3':inter.volume*1000})
    progress('Sampled cap travel check: '+str(len(motion)))
    # Tube and purchased-body clearances are reported separately from print parts.
    tube_hits=[]
    for en in hardware:
        if not en['kind'].startswith('tube'):continue
        bb=bounds(en['body'])
        for fi in fixed+caps:
            if not intersects_bb(bb,bounds(fi['body'])):continue
            inter=T.copy(en['body'])
            if T.booleanOperation(inter,T.copy(fi['body']),I) and inter.volume*1000>p['validation']['interference_volume_tolerance_mm3']:
                tube_hits.append({'tube':en['name'],'part':fi.get('cell',fi['name']),'volume_mm3':inter.volume*1000,'bounds_mm':bounds(inter)})
    rigid_hits=[]
    for en in hardware:
        if en['kind'] not in ['pump','valve','board']:continue
        bb=bounds(en['body'])
        for fi in fixed+caps:
            if not intersects_bb(bb,bounds(fi['body'])):continue
            inter=T.copy(en['body'])
            if T.booleanOperation(inter,T.copy(fi['body']),I) and inter.volume*1000>p['validation']['interference_volume_tolerance_mm3']:rigid_hits.append({'hardware':en['name'],'part':fi['name'],'volume_mm3':inter.volume*1000})
    def network(en):
        n=en['name']
        if 'FillBusConnection' in n or 'Pressure' in n or 'pressure_' in n or n=='Ref_Pump_pressure':return 'P'
        if 'ExtractBusConnection' in n or 'Suction' in n or 'extraction_' in n or n=='Ref_Pump_extraction':return 'S'
        if 'G1' in n:return 'G1'
        if 'G2' in n:return 'G2'
        if n.startswith('Ref_SupportedWeldPort_'):
            cellid=n.rsplit('_',1)[1];return 'G'+str(next(ce['group'] for ce in cells if ce['id']==cellid))
        return None
    network_hits=[];tube_hardware_hits=[];tubes=[en for en in hardware if en['kind'].startswith('tube')]
    for i,en in enumerate(tubes):
        na=network(en)
        for other in tubes[:i]:
            nb=network(other)
            if not na or not nb or na==nb or not intersects_bb(bounds(en['body']),bounds(other['body'])):continue
            inter=T.copy(en['body'])
            if T.booleanOperation(inter,T.copy(other['body']),I) and inter.volume*1000>p['validation']['interference_volume_tolerance_mm3']:network_hits.append({'a':en['name'],'b':other['name'],'networks':[na,nb],'volume_mm3':inter.volume*1000})
        for other in hardware:
            if other['kind'] not in ['pump','valve','board'] or not intersects_bb(bounds(en['body']),bounds(other['body'])):continue
            nb=network(other)
            if na and nb and na==nb:continue
            inter=T.copy(en['body'])
            if T.booleanOperation(inter,T.copy(other['body']),I) and inter.volume*1000>p['validation']['interference_volume_tolerance_mm3']:
                intentional=False
                if other['name'].startswith('Ref_Valve_G'):
                    vi=s['valve_ids'].index(other['name'][len('Ref_Valve_'):]);cx,cy=s['valve_centres'][vi];half=s['valve_envelope'][0]/2;ib=bounds(inter)
                    intentional=ib[1][0]<=cx-half+EPS or ib[0][0]>=cx+half-EPS
                if not intentional:tube_hardware_hits.append({'tube':en['name'],'hardware':other['name'],'volume_mm3':inter.volume*1000})
    progress('Cross-network / tube-hardware checks: '+str((len(network_hits),len(tube_hardware_hits))))
    tool_hits=[];head_hits=[]
    tolerance=p['validation']['interference_volume_tolerance_mm3']
    tool_d=p['validation']['driver_shaft_d']
    printed=fixed+caps
    service_obstacles=[en for en in hardware if en['kind'] in ('pump','valve','board') or en['kind'].startswith('tube')]
    def check_clearance(probe,candidates):
        probe_bounds=bounds(probe)
        for entry in candidates:
            if not intersects_bb(probe_bounds,bounds(entry['body'])):continue
            inter=T.copy(probe)
            if T.booleanOperation(inter,T.copy(entry['body']),I) and inter.volume*1000>tolerance:
                yield entry['name'],inter.volume*1000
    for joint in joint_records:
        interface=joint['interface'];seat=joint['seat_z']
        top_access=interface in ('dry_flange_clamp','service_cover')
        # Cup and splice screws are reached before fitting their bottom panels.
        excluded={'panel'} if interface in ('section_splice','cup_to_lower_chassis','pcb_tray_stack') else set()
        if interface=='dry_flange_clamp':excluded.update(('cap1','cap2'))
        if interface=='section_splice':excluded.update(('cradle','clip'))
        candidates=[en for en in printed if en['kind'] not in excluded]
        if interface=='service_cover':candidates+=service_obstacles
        for xx,yy in joint.get('holes',[joint.get('xy')]):
            end=seat+f['head_h']+EPS if top_access else seat-f['head_h']-EPS
            start=H+c['stroke']+10 if top_access else -c['stroke']
            tool=cyl((xx,yy,min(start,end)),(xx,yy,max(start,end)),tool_d)
            for name,volume in check_clearance(tool,candidates):
                tool_hits.append({'interface':interface,'xy':[xx,yy],'blocked_by':name,'volume_mm3':volume})
    for entry in hardware:
        if 'screw_direction' not in entry:continue
        xx,yy,seat=entry['where']
        outside=seat-entry['screw_direction']*f['head_h']
        head=cyl((xx,yy,min(seat,outside)),(xx,yy,max(seat,outside)),f['head_d'])
        for name,volume in check_clearance(head,printed):
            head_hits.append({'screw':entry['name'],'xyz':entry['where'],'blocked_by':name,'volume_mm3':volume})
    progress('Tube / rigid / driver / screw-head checks: '+str((len(tube_hits),len(rigid_hits),len(tool_hits),len(head_hits))))
    manifest={'schema':p['schema'],'units':'mm','params':p,'layout_checks':derived['checks'],'coverage':{k:derived[k] for k in ['active_area_per_cell_mm2','cap_area_per_cell_mm2','cap_coverage_of_field','active_coverage_of_field']},'dimensions':{'width':W,'field_length':L,'service_length':sd,'length':L+sd,'height':H,'nominal_raised_surface':H+c['stroke'],'cap_gap':pitch-c['cap_width'],'cap_edge_border':g['border']+(pitch-c['cap_width'])/2,'active_width':c['active_width'],'cap_width':c['cap_width'],'stroke':c['stroke']},'cells':cells,'parts':[],'instances':[],'joints':joint_records,'hoses':hose_records,'interferences':interference,'motion_interferences':motion,'tube_interferences':tube_hits,'rigid_reference_interferences':rigid_hits,'driver_access_interferences':tool_hits,'screw_head_interferences':head_hits,'tube_network_interferences':network_hits,'tube_hardware_interferences':tube_hardware_hits,'physical_fit':'UNVERIFIED','pump_count_required':None,'pump_capacity':s['pump_capacity'],'state_table':{'rise':['open','closed'],'hold':['closed','closed'],'lower':['closed','open']}}
    em=design.exportManager
    for name,data in components.items():
        body=data['component'].bRepBodies.item(0);bb=bounds(body);dims=[bb[1][i]-bb[0][i] for i in range(3)]
        if not data['reference'] and max(dims)>p['print']['max_envelope']+EPS:raise RuntimeError(name+' exceeds print allowance '+str(dims))
        path=meshes/(name+'.stl');opt=em.createSTLExportOptions(body,str(path));opt.isBinaryFormat=True;opt.meshRefinement=F.MeshRefinementSettings.MeshRefinementHigh
        if not em.execute(opt):raise RuntimeError('Export failed '+name)
        qty=sum(en['name']==name for en in instances)
        manifest['parts'].append({'name':name,'file':'meshes/'+name+'.stl','kind':data['kind'],'reference':data['reference'],'quantity':qty,'bbox_mm':dims,'volume_mm3':body.volume*1000})
    for en in instances:manifest['instances'].append({k:en[k] for k in ['name','where','kind','reference'] if k in en}|{k:en[k] for k in ['cell','group','bank','cap_group'] if k in en})
    manifest['spare_routes']={name:bounds(body) for name,body in spare_routes.items()}
    manifest['spare_route_interferences']=spare_route_hits
    manifest['feature_issues']=[{'name':it.name,'message':it.errorOrWarningMessage} for it in design.timeline if it.healthState!=F.FeatureHealthStates.HealthyFeatureHealthState]
    (out/'2026-11-08_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    design.attributes.add('BedPrototype','params',json.dumps(p));design.attributes.add('BedPrototype','manifest_path',str(out/'2026-11-08_manifest.json'))
    progress('Creating linked exploded and alternating-group assemblies')
    optional_o.isLightBulbOn=False
    to.isLightBulbOn=False
    lowered_o,lowered=component(asm,'Reference_TPU_Lowered')
    for en in instances:
        if en['kind'].startswith('tpu'):en['occ'].isLightBulbOn=False
    for ce in cells:
        body=rounded_box(c['active_width'],c['active_width'],c['support_z'],cap_low-c['support_z'],c['active_corner_r'])
        o,co=component(lowered,'Ref_TPU_Lowered_'+ce['id'],(ce['x'],ce['y'],0))
        bf=co.features.baseFeatures.add();bf.startEdit();co.bRepBodies.add(body,bf);bf.finishEdit()
    states={}
    for state in ['Inspection_Exploded','Inspection_G1Raised_G2Lowered']:
        so,sc=component(design.rootComponent,state);states[state]=so
        for en in instances:
            cover_screw=en['name']=='Ref_Cover_M2p5x8'
            if en['kind']=='fastener' and 'cap_group' not in en and not (cover_screw and state=='Inspection_Exploded'):continue
            if state!='Inspection_Exploded' and (en['kind'].startswith('cap') or 'cap_group' in en):continue
            xyz=en['where'][:];kind=en['kind']
            if state=='Inspection_Exploded':
                lift=p['exploded'];dz=lift['cap_lift'] if kind.startswith('cap') else lift['ring_lift'] if kind=='ring' else lift['cup_lift'] if kind=='cup' else -lift['panel_drop'] if kind=='panel' else lift['cover_lift'] if kind=='cover' else 0
                xyz[2]+=lift['cover_lift']+12 if cover_screw else dz
            elif (kind.startswith('cap') and en.get('group')==2) or en.get('cap_group')==2:xyz[2]-=c['stroke']
            elif kind.startswith('tpu'):
                continue # Separate TPU states are added below.
            m=C.Matrix3D.create();m.translation=vec(*[v/10 for v in xyz]);linked=sc.occurrences.addExistingComponent(components[en['name']]['component'],m);linked.isLightBulbOn=True
        if state=='Inspection_G1Raised_G2Lowered':
            for ce in cells:
                z_top=cap_high if ce['group']==1 else cap_low
                state_name='Raised' if ce['group']==1 else 'Lowered'
                body=rounded_box(c['active_width'],c['active_width'],c['support_z'],z_top-c['support_z'],c['active_corner_r'])
                o,co=component(sc,'Reference_TPU_'+state_name+'_'+ce['id'],(ce['x'],ce['y'],0))
                bf=co.features.baseFeatures.add();bf.startEdit();co.bRepBodies.add(body,bf);bf.finishEdit()
        so.isLightBulbOn=False
    progress('Saving local Fusion and STEP assemblies')
    # Keep a reviewable CAD model even if checks identify work to correct.
    em.execute(em.createSTEPExportOptions(str(out/'2026-11-08_GroupedBed_assembled.step'),asm))
    for state,o in states.items():
        ao.isLightBulbOn=False;o.isLightBulbOn=True
        em.execute(em.createSTEPExportOptions(str(out/('2026-11-08_'+state+'.step')),o.component))
        o.isLightBulbOn=False
    ao.isLightBulbOn=True
    # Native CAD view captures, excluding UI chrome and using actual BRep solids.
    def capture(name,eye,up=(0,0,1)):
        try:
            vp=app.activeViewport;cam=vp.camera;cam.isPerspective=False;cam.target=pt(0,(L-sd)/2,H/2);cam.eye=pt(*eye);cam.upVector=vec(*up);cam.isFitView=True;vp.camera=cam;vp.refresh();adsk_do();vp.saveAsImageFile(str(out/('2026-11-08_'+name+'.png')),1600,1200)
        except Exception as ex:progress('Capture '+name+': '+str(ex))
    capture('bottom',(0,(L-sd)/2,-H*12),(0,1,0));capture('assembled',(W,-L,H*5));capture('top',(0,(L-sd)/2,H*12),(0,1,0));capture('side',(W*3,(L-sd)/2,H/2))
    for en in instances:
        if en['kind'] in ['panel','cap1','cap2','cup','ring','cover','tpu1','tpu2']:en['occ'].isLightBulbOn=False
    lowered_o.isLightBulbOn=False
    capture('routing',(W,-L,-H*5))
    for en in instances:en['occ'].isLightBulbOn=not en['kind'].startswith('tpu')
    lowered_o.isLightBulbOn=True
    ao.isLightBulbOn=False;states['Inspection_Exploded'].isLightBulbOn=True;capture('exploded',(W,-L,H*5));states['Inspection_Exploded'].isLightBulbOn=False
    states['Inspection_G1Raised_G2Lowered'].isLightBulbOn=True;capture('alternating',(W,-L,H*5));states['Inspection_G1Raised_G2Lowered'].isLightBulbOn=False;ao.isLightBulbOn=True
    capture('assembled',(W,-L,H*5))
    progress('Checks: print intersections='+str(len(interference))+', motion='+str(len(motion))+', tube='+str(len(tube_hits)))
    if interference or motion or tube_hits or rigid_hits or tool_hits or head_hits or network_hits or tube_hardware_hits or spare_route_hits or manifest['feature_issues']:progress('REVIEW_REQUIRED: inspect manifest before print release')
    import builtins
    builtins.bed_grouped_context={'local':locals(),'global':globals()}
    details=root/'design/fusion/grouped_details.py'
    if details.exists():
        dn={'__name__':'bed_grouped_details'};exec(compile(details.read_text(),str(details),'exec'),dn);dn['make_details'](builtins.bed_grouped_context)
    progress('CAD exports complete: '+str(out))

def adsk_do():
    import adsk
    adsk.doEvents()

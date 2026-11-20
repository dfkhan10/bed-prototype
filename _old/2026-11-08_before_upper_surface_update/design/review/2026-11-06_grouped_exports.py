"""Validate actual Fusion meshes and prepare print/BOM/review artifacts."""
from pathlib import Path
import json,csv,math,shutil,subprocess,sys
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'export/2026-11-06_grouped';M=json.loads((OUT/'2026-11-06_manifest.json').read_text());P=json.loads((ROOT/'design/bed_params.json').read_text())
if not M.get('coupon'):raise SystemExit('Finish the native CAD detail export before preparing print files.')
if M['params']!=P:raise SystemExit('Current exports do not match bed_params.json; finish the CAD rebuild first.')
PRINT=OUT/'stl';PRINT.mkdir(exist_ok=True);report={'units':'mm','parts':[],'errors':[],'cad_check_counts':{},'incremental_checks':M.get('incremental_checks',{})}
for k in ['interferences','motion_interferences','tube_interferences','rigid_reference_interferences','driver_access_interferences','tube_network_interferences','tube_hardware_interferences','feature_issues']:
 report['cad_check_counts'][k]=len(M.get(k,[]))
 if M.get(k):report['errors'].append(k+': '+str(len(M[k])))
if M.get('layout_checks') and not all(M['layout_checks'].values()):report['errors'].append('Layout preconditions failed')
meshes={};print_rows=[];hardware_rows=[]
for p in M['parts']:
 mesh=trimesh.load_mesh(OUT/p['file']);meshes[p['name']]=mesh
 if p['reference']:
  if p['kind'] in ['fastener','pump','board'] or p['name'].startswith('Ref_Valve_'):
   status='capacity reservation; installed pump count unverified' if p['kind']=='pump' else 'reference only; exact purchased component/material unverified'
   hardware_rows.append([p['name'],p['quantity'],status])
  continue
 components=len(mesh.split(only_watertight=False));dims=mesh.extents
 row={'name':p['name'],'quantity':p['quantity'],'watertight':bool(mesh.is_watertight),'consistent_winding':bool(mesh.is_winding_consistent),'connected_solids':components,'bbox_mm':dims.tolist(),'cad_bbox_mm':p['bbox_mm']}
 if not mesh.is_watertight or not mesh.is_winding_consistent or components!=1:report['errors'].append(p['name']+': invalid/disconnected mesh')
 if np.max(np.abs(dims-np.array(p['bbox_mm'])))>.1:report['errors'].append(p['name']+': CAD/STL dimensions differ')
 if max(dims)>P['print']['max_envelope']+.02:report['errors'].append(p['name']+': oversized')
 oriented=mesh.copy()
 flip=p['kind'] in ['cup','cover','cap1','cap2']
 if flip:oriented.apply_transform(trimesh.transformations.rotation_matrix(math.pi,[1,0,0]))
 oriented.apply_translation([-oriented.centroid[0],-oriented.centroid[1],-oriented.bounds[0,2]])
 oriented.export(PRINT/(p['name']+'.stl'))
 row['print_orientation']='flat top/film face on bed' if flip else 'normalized CAD orientation; inspect supports'
 report['parts'].append(row);print_rows.append([p['name'],p['quantity'],*[round(float(v),3) for v in dims],row['print_orientation']])
# Native detail exports are generated from the very same cell solids.
if 'coupon' in M:
 cpdir=OUT/'coupon/stl';cpdir.mkdir(parents=True,exist_ok=True)
 for item in M['coupon']['items']:
  mesh=trimesh.load_mesh(OUT/item['file']);mesh=mesh.copy()
  if item['kind'] in ['cup','ring','cap1','cap2'] and item['kind']!='ring':mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi,[1,0,0]))
  if len(mesh.split(only_watertight=False))!=1 or not mesh.is_watertight or not mesh.is_winding_consistent:report['errors'].append(item['name']+': coupon mesh invalid')
  mesh.apply_translation([-mesh.centroid[0],-mesh.centroid[1],-mesh.bounds[0,2]]);mesh.export(cpdir/(item['name']+'.stl'))

# Measure the complete printed assembly as well as each individual print.
boxes=[meshes[i['name']].bounds+np.asarray(i['where']) for i in M['instances'] if not i['reference']]
assembly_box=np.array([np.min([b[0] for b in boxes],axis=0),np.max([b[1] for b in boxes],axis=0)])
report['assembly_bbox_mm']=assembly_box.tolist();report['assembly_extents_mm']=(assembly_box[1]-assembly_box[0]).tolist()
if np.max(np.abs((assembly_box[1]-assembly_box[0])-np.array([M['dimensions'][k] for k in ['width','length','height']])))>.1:report['errors'].append('Printed assembly envelope differs from declared dimensions')

def csvfile(name,header,rows):
 with (OUT/name).open('w',newline='') as f:w=csv.writer(f);w.writerow(header);w.writerows(rows)
csvfile('2026-11-06_print_BOM.csv',['part','quantity','x_mm','y_mm','z_mm','orientation'],print_rows)
csvfile('2026-11-06_hardware_BOM.csv',['item','quantity','status'],hardware_rows+[['Supported weld-compatible bladder ports',12,'nominal 6 mm insertion stem / 20 mm weld flange; actual fitting unverified'],['Cable ties / reusable retaining straps',16,'two per pump cradle; select actual strap'],['TPU welded cell',12,'not FDM printed; pattern is a coupon starting point'],['TPU gusset dry-flange reinforcement ring',12,'second dry ply; remove central 64 mm opening; coupon first'],['4-way cross fittings',6,'generic 4 mm ID tubing connections; verify exact purchased envelope'],['End plugs',2,'one per group trunk'],['Tee fittings',10,'2 group tees + 8 distribution branch tees; exact fittings unverified'],['Elbow fittings',8,'header/valve connections; exact fittings unverified'],['Valve retaining straps',4,'one per provisional valve body'],['Controller/driver spacers and retainers',8,'match actual board; slotted trays are adjustable']])
csvfile('2026-11-06_joint_coordinates.csv',['interface','cell_or_joint','x_mm','y_mm','seat_z_mm','screw','grip_mm','engagement_mm'],[[j['interface'],j.get('cell',j.get('id','')),xy[0],xy[1],j['seat_z'],j['screw'],j['grip'],j['engagement']] for j in M['joints'] for xy in j.get('holes',[j.get('xy')])])
csvfile('2026-11-06_hose_cut_list.csv',['route','network_or_group','model_centreline_length_mm','status'],[[h['id'],h.get('group','see route name'),round(h.get('length_mm',0),1),'geometric length only; add fitting insertion/service allowance after trial'] for h in M['hoses']])
csvfile('2026-11-06_dimensions.csv',['dimension','value_mm_or_ratio'],list(M['dimensions'].items())+list(M.get('coverage',{}).items()))
(OUT/'2026-11-06_mesh_checks.json').write_text(json.dumps(report,indent=2)+'\n')
# Millimetre-scale vector templates. They are fabrication coupons, not accepted weld tooling.
c=P['cell'];g=P['guide'];size=c['cup_width'];active=c['active_width'];land=c['weld_land'];r=c['active_corner_r'];upper=active+2*land;belt=4*(active-2*r)+2*math.pi*r;belt_h=(c['lower_cap_underside_z']+c['stroke']-c['support_z'])+2*land
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210"><style>text{font-family:Arial,sans-serif;font-size:3px}.cut{fill:none;stroke:#202830;stroke-width:.25}.weld{fill:none;stroke:#ca7834;stroke-width:.3;stroke-dasharray:1.5 1}.active{fill:none;stroke:#4287a6;stroke-width:.25}</style>','<text x="12" y="8">TPU gusset-pouch coupon • dimensions in mm • weld geometry and material NOT validated</text>']
def panel(x,y,width,label,dry=False,port=True):
 svg.append(f'<rect class="cut" x="{x}" y="{y}" width="{width}" height="{width}" rx="{r+land}"/><rect class="weld" x="{x+(width-upper)/2}" y="{y+(width-upper)/2}" width="{upper}" height="{upper}" rx="{r+land}"/><rect class="active" x="{x+(width-active)/2}" y="{y+(width-active)/2}" width="{active}" height="{active}" rx="{r}"/><text x="{x}" y="{y+width+5}">{label}: {width:g} × {width:g}</text>')
 if dry:
  for dx in [-c['clamp_screw_xy'],c['clamp_screw_xy']]:
   for dy in [-c['clamp_screw_xy'],c['clamp_screw_xy']]:svg.append(f'<circle class="cut" cx="{x+width/2+dx}" cy="{y+width/2+dy}" r="{P["fasteners"]["clearance_d"]/2}"/>')
  for dy in [-g['spacing_half'],g['spacing_half']]:svg.append(f'<circle class="cut" cx="{x+width/2}" cy="{y+width/2+dy}" r="{g["bore_d"]/2}"/>')
  if port:svg.append(f'<circle class="active" cx="{x+width/2}" cy="{y+width/2}" r="{c["weld_port_flange_d"]/2}"/>')
panel(12,18,size,'Lower panel / external dry flange',True);panel(112,18,upper,'Upper panel')
panel(200,18,size,'Dry-flange reinforcement ring',True,False)
svg.append(f'<rect class="cut" x="{200+(size-upper)/2}" y="{18+(size-upper)/2}" width="{upper}" height="{upper}" rx="{r+land}"/><text x="200" y="109">Remove centre; second dry ply.</text>')
svg.append(f'<rect class="cut" x="12" y="123" width="{belt+2*land:.3f}" height="{belt_h:.3f}"/><path class="weld" d="M12,{123+land} h{belt+2*land:.3f} M12,{123+belt_h-land} h{belt+2*land:.3f}"/><text x="12" y="{123+belt_h+6:.3f}">Wall strip: {(belt+2*land):.2f} × {belt_h:.2f}; includes {2*land:g} end overlap. Trial assembly required.</text><text x="12" y="183">Orange: weld-land boundary. Blue: active outline / supported port footprint. Black: cut / dry holes.</text><text x="12" y="190">Keep mounting and guide holes outside every airtight seam. Print/export at 100%; verify the 80 mm panel.</text><text x="12" y="197">Blue port circle is a footprint only: make the lower-panel aperture to match the actual fitting.</text></svg>')
(OUT/'coupon/2026-11-06_TPU_gusset_pattern.svg').write_text(''.join(svg))
# The simpler pillow coupon uses two of the same dry-flange panels.
svg=svg[:2];svg[1]=svg[1].replace('gusset-pouch','two-sheet pillow');panel(12,18,size,'Pillow panel 1',True);panel(112,18,size,'Pillow panel 2',True,False);svg.append('<text x="12" y="123">Two-sheet pillow comparison coupon. Its achieved lift/volume must be measured; 25 mm is not guaranteed.</text><text x="12" y="130">Lower panel 1 only: make its port aperture to the actual welded fitting. Do not open the upper panel.</text></svg>')
(OUT/'coupon/2026-11-06_TPU_pillow_pattern.svg').write_text(''.join(svg))
# An offline viewer uses actual exported triangle geometry, never a rendered reconstruction.
viewer={'manifest':{k:M[k] for k in ['dimensions','cells','instances','params']},'parts':{}}
for p in M['parts']:
 m=meshes[p['name']];viewer['parts'][p['name']]={'position':m.vertices.round(3).ravel().tolist(),'index':m.faces.ravel().tolist(),'kind':p['kind']}
if M.get('coupon'):
 viewer['coupon']=M['coupon'];stand=trimesh.load_mesh(OUT/'coupon/meshes/Print_OneCellTestStand.stl');viewer['parts']['Print_OneCellTestStand']={'position':stand.vertices.round(3).ravel().tolist(),'index':stand.faces.ravel().tolist(),'kind':'frame'}
cache=ROOT/'.cache/grouped-cad';bundle=cache/'review.bundle.js'
subprocess.run([str(cache/'node_modules/.bin/esbuild'),str(ROOT/'design/review/2026-11-06_grouped_viewer.js'),'--bundle','--minify','--format=iife','--outfile='+str(bundle)],check=True)
html=(ROOT/'design/review/2026-11-06_grouped_viewer.html').read_text().replace('__DATA__',json.dumps(viewer,separators=(',',':'))).replace('__SCRIPT__',bundle.read_text())
(OUT/'2026-11-06_design_review.html').write_text(html)
print('Printed types:',len(report['parts']),'total pieces:',sum(p['quantity'] for p in report['parts']),'errors:',report['errors'])
if report['errors']:sys.exit(1)
# Keep the existing operating report current and package only validated print files.
subprocess.run([sys.executable,str(ROOT/'design/review/2026-11-06_grouped_drawings.py')],check=True)
max_dimension=max(max(part['bbox_mm']) for part in report['parts'])
rows='\n'.join('| '+key.replace('_',' ')+' | '+str(value)+' |' for key,value in report['cad_check_counts'].items())
(ROOT/'docs/DESIGN_DEBUG.md').write_text(f'''# Grouped CAD verification

6 November 2026. Current parameter schema: `{P['schema']}`. [Native geometry manifest](../export/2026-11-06_grouped/2026-11-06_manifest.json) matches the current JSON dimensions. [Mesh report](../export/2026-11-06_grouped/2026-11-06_mesh_checks.json) records the actual exported geometry checks.

| CAD check | Reported issues |
|---|---:|
{rows}

All {len(M['layout_checks'])} layout preconditions pass. Checks cover fixed printed parts, raised caps, cap travel sampled every {P['validation']['clearance_sample_mm']} mm through the {P['cell']['stroke']} mm stroke, hose OD envelopes, separate pneumatic networks, bought rigid keep-outs and Ø{P['validation']['driver_shaft_d']} mm driver shafts. Solid intersections smaller than {P['validation']['interference_volume_tolerance_mm3']} mm³ are outside the report threshold. This is a nominal geometry check, not a tolerance-stack or structural calculation.

All {len(report['parts'])} printable mesh types ({sum(p['quantity'] for p in report['parts'])} full-assembly pieces) are watertight, consistently wound, connected single solids and within 0.1 mm of the native CAD bounding boxes. Largest dimension: {max_dimension:.3f} mm, within the {P['print']['max_envelope']} mm allowance. The complete printed assembly measures {report['assembly_extents_mm'][0]:g} × {report['assembly_extents_mm'][1]:g} × {report['assembly_extents_mm'][2]:g} mm. The four one-cell coupon meshes are checked separately. The final PCB tray correction adds four through holes and four head-clearance pockets; its explicit head/driver checks report zero conflicts.

The model contains eight pump envelopes, four group valves, stacked board trays, supported cell ports, hose bends, group crosses, tube clips and section screws. Expected hose/barb insertion overlap and connections within one pneumatic network are intentional. Actual ports, board connectors and hose compliance remain provisional.

Physical acceptance is open: kit measurements, valve function/vacuum compatibility, installed pump flow and required pump count, electrical ratings, TPU weld/port leakage, clamp compression, guide friction, screw strip-out, slicing/support removal and load capacity. Begin with the [one-cell coupon](../export/2026-11-06_grouped/coupon/stl/) and [assembly sequence](ASSEMBLY.md). Eight is packaging capacity, not the proven operating count.
''')
import zipfile
package=OUT/'2026-11-06_print_package.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED) as z:
 for folder in [PRINT,OUT/'coupon/stl']:
  for file in sorted(folder.glob('*.stl')):z.write(file,file.relative_to(OUT))
 for file in sorted(OUT.glob('*.csv')):z.write(file,file.name)
 for file in sorted((OUT/'coupon').glob('*.svg')):z.write(file,file.relative_to(OUT))
 for name in ['2026-11-06_dimensions.svg','2026-11-06_mesh_checks.json','2026-11-06_one_cell_coupon.png']:
  if (OUT/name).exists():z.write(OUT/name,name)
 for name in ['ASSEMBLY.md','PRINT_CHECKLIST.md','BED_FRAME_CONNECTORS.md','TUBE_ROUTING.md']:z.write(ROOT/'docs'/name,'instructions/'+name)
 z.writestr('READ_FIRST.txt','CAD prototype, millimetres. Print coupon/stl first (4 parts). Full-assembly quantities are in print_BOM.csv. Read instructions/ASSEMBLY.md. TPU is welded film, not an FDM print. Hardware, material, slicing, pressure and load tests remain open. Eight pumps are a packaging reservation, not the established operating count.\n')
with zipfile.ZipFile(package) as z:
 if z.testzip() is not None:raise RuntimeError('Print package CRC check failed')
print('Validated print package:',package)

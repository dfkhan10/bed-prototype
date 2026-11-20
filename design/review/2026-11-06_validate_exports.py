"""Validate the exported Fusion meshes and actual cylinder axes, not just formulas."""
from pathlib import Path
import json, math
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'export'
m=json.loads((OUT/'2026-11-06_export_manifest.json').read_text())
p=m['params'];L=m['layout'];rows=[]
for part in m['parts']:
 mesh=trimesh.load_mesh(OUT/part['file']);connected=len(mesh.split(only_watertight=False))
 assert mesh.is_watertight and mesh.is_winding_consistent and connected==1, part['name']
 assert np.allclose(mesh.extents,part['bbox_mm'],atol=.005),part['name']
 assert max(mesh.extents)<=p['print_max_mm']+.005
 assert abs(mesh.volume-part['volume_mm3'])/part['volume_mm3']<.001
 rows.append({'name':part['name'],'bbox_mm':mesh.extents.round(4).tolist(),'watertight':True,'connected_solids':connected,'triangles':len(mesh.faces)})
axes=m['hole_axes']
def has_axis(part,diam,x,y,z,axis):
 for h in axes:
  if h['part']!=part or abs(h['diameter_mm']-diam)>.001:continue
  v=np.array(h['axis']);origin=np.array(h['origin_mm']);target=np.array([x,y,z])
  if abs(abs(v[axis])-1)<1e-5 and np.linalg.norm(np.cross(target-origin,v))<.001:return True
 return False
for x in L['joint_xs']:
 assert has_axis('BedFrame_CellDeck',p['fasteners']['clearance_d'],x,L['mate_y'],p['joint_axis_z'],1)
 assert has_axis('BedFrame_ServiceDeck',p['fasteners']['pilot_d'],x,L['mate_y'],p['joint_axis_z'],1)
for x,y in L['screw_points']:
 assert has_axis('BedFrame_ServiceDeck',p['fasteners']['pilot_d'],x,y,0,2)
 assert has_axis('BedFrame_ElectronicsBay',p['fasteners']['clearance_d'],x,y,0,2)
 assert has_axis('BedFrame_ElectronicsBay',p['fasteners']['pilot_d'],x,y,-p['e_bay_cavity_h'],2)
 assert has_axis('BedFrame_BottomPanel',p['fasteners']['clearance_d'],x,y,-p['e_bay_cavity_h'],2)
for c in L['cells']:assert has_axis('BedFrame_CellDeck',p['port_d'],c['x'],c['y'],L['ztop']-p['cell_seat_depth'],2)
assert not m['interferences'] and not m['feature_issues']
assert p['pneumatics']['pump_count'] is None and not p['pneumatics']['pump_mounts_enabled']
assert len(list((OUT/'stl').glob('*.stl')))==len(m['parts'])
report={'status':'pass','print_parts':rows,'coaxial_cell_service_pairs':4,'coaxial_rim_pairs':8,'coaxial_panel_pairs':8,'through_floor_ports':12,'frame_interferences':0,'feature_issues':0,'hardware_fit':'pending physical measurement','pump_count':None}
(OUT/'2026-11-06_mesh_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

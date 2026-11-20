"""Build the offline review from actual Fusion STLs. Requires numpy/trimesh.
The first run installs pinned three/esbuild locally into .cache/bed-review.
"""
from pathlib import Path
import json,shutil,subprocess
import trimesh

root=Path(__file__).resolve().parents[2];out=root/'export';source=root/'design/review';cache=root/'.cache/bed-review'
cache.mkdir(parents=True,exist_ok=True)
m=json.loads((out/'2026-11-06_export_manifest.json').read_text());p=m['params'];e=p['exploded'];sy=e['service_shift_y_mm'];w=e['screw_withdrawal_mm']
data={'parts':[],'params':p,'layout':m['layout']}
for part in m['parts']+m['references']:
 name=part['name']
 kind='cell' if 'CellDeck' in name else 'service' if 'ServiceDeck' in name else 'bay' if 'ElectronicsBay' in name else 'panel' if 'BottomPanel' in name else 'screw' if 'Screw' in name else 'valve'
 offset={'cell':[0,0,e['cell_lift_mm']], 'service':[0,sy,e['service_lift_mm']], 'bay':[0,sy,-e['bay_drop_mm']], 'panel':[0,sy,-e['panel_drop_mm']], 'valve':[0,sy,-e['valve_drop_mm']], 'screw':[0,0,0]}[kind]
 if 'ScrewCell' in name:offset=[0,w,e['cell_lift_mm']]
 if 'ScrewRim' in name:offset=[0,sy,-e['bay_drop_mm']-w]
 if 'ScrewPanel' in name:offset=[0,sy,-e['panel_drop_mm']-w]
 mesh=trimesh.load_mesh(out/part['file'])
 data['parts'].append({'name':name,'kind':kind,'vertices':mesh.vertices.round(3).ravel().tolist(),'faces':mesh.faces.ravel().tolist(),'offset':offset,'dimensions':mesh.extents.round(3).tolist()})
shutil.copy2(source/'2026-11-06_viewer.js',cache/'viewer.js')
esbuild=cache/'node_modules/.bin/esbuild'
if not esbuild.exists():subprocess.run(['npm','install','--prefix',str(cache),'--no-package-lock','--no-save','three@0.170.0','esbuild@0.24.0'],check=True)
subprocess.run([str(esbuild),str(cache/'viewer.js'),'--bundle','--minify','--format=iife','--outfile='+str(cache/'viewer.bundle.js')],check=True)
html=(source/'2026-11-06_viewer_template.html').read_text().replace('__MODEL_DATA__',json.dumps(data,separators=(',',':'))).replace('__VIEWER_SCRIPT__',(cache/'viewer.bundle.js').read_text())
(out/'2026-11-06_design_review.html').write_text(html)
print('Offline viewer:',out/'2026-11-06_design_review.html',len(html),'bytes')

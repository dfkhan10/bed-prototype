from pathlib import Path
import copy,json,zipfile,xml.etree.ElementTree as E
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'export/2026-11-10_Bed_P2S_12_plates_flat.3mf'
OUT=Path(__file__).parent/'2026-11-16_plate_unsliced.3mf'
C='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
P='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
B='http://schemas.bambulab.com/package/2021'
E.register_namespace('',C);E.register_namespace('p',P);E.register_namespace('BambuStudio',B)
ns={'m':C}
def meta(el,key,value):
 e=el.find(f"metadata[@key='{key}']")
 if e is None:e=E.SubElement(el,'metadata',key=key)
 e.set('value',str(value))
with zipfile.ZipFile(SRC) as z:
 model=E.fromstring(z.read('3D/3dmodel.model'))
 conf=E.fromstring(z.read('Metadata/model_settings.config'))
 names={o.find("metadata[@key='name']").get('value'):o for o in conf.findall('object')}
 print('CLAMPS',[k for k in names if 'Clamp_AC' in k])
 specs=[('Electronics_tray_2',15,15,False),('Electronics_tray_1',15,95,False),
        (next(k for k in names if 'Clamp_AC' in k),164,55,False),
        ('Rounded_handle 01',15,193,True),('Rounded_handle 02',139,193,True),
        ('Rounded_handle 03',15,228,True),('Rounded_handle 04',139,228,True)]
 resources=model.find('m:resources',ns);oldobjects={o.get('id'):o for o in resources};resources.clear()
 build=model.find('m:build',ns);build.clear()
 newconf=E.Element('config');plate=E.Element('plate')
 for k,v in [('plater_id',1),('plater_name','4 upright handles, 2 electronics trays, 1 clamp frame'),('locked','false'),('bed_type','Textured PEI Plate'),('filament_map_mode','Auto For Flush')]:meta(plate,k,v)
 paths=[];bounds=[]
 for index,(name,x,y,upright) in enumerate(specs,1):
  settings=copy.deepcopy(names[name]); oid=settings.get('id');obj=copy.deepcopy(oldobjects[oid]);resources.append(obj)
  comp=obj.find('m:components/m:component',ns);path=comp.get('{'+P+'}path').lstrip('/');paths.append(path)
  geom=E.fromstring(z.read(path));verts=np.array([[float(v.get(a)) for a in 'xyz'] for v in geom.findall('.//m:vertex',ns)])
  assert comp.get('transform')=='1 0 0 0 1 0 0 0 1 0 0 0'
  R=np.array([[1,0,0],[0,0,-1],[0,1,0]]) if upright else np.eye(3)
  rotated=verts@R; offset=np.array([x,y,0])-rotated.min(axis=0)
  transform=' '.join(f'{v:.9g}' for v in [*R.ravel(),*offset])
  E.SubElement(build,'{'+C+'}item',objectid=oid,transform=transform,printable='1')
  if upright:
   meta(settings,'enable_support',1);meta(settings,'brim_type','outer_only');meta(settings,'brim_width',7)
   meta(settings,'support_type','normal(auto)');meta(settings,'support_style','snug')
  if 'Clamp' in name:meta(settings,'enable_support',0)
  newconf.append(settings)
  inst=E.SubElement(plate,'model_instance')
  for k,v in [('object_id',oid),('instance_id',0),('identify_id',index)]:meta(inst,k,v)
  bb=np.array([rotated.min(axis=0)+offset,rotated.max(axis=0)+offset]);bounds.append((name,bb.tolist()))
  print(name,np.round(bb,2).tolist())
 newconf.append(plate);E.SubElement(newconf,'assemble')
 settings=json.loads(z.read('Metadata/project_settings.config'))
 settings['curr_bed_type']='Textured PEI Plate'
 rel=E.fromstring(z.read('3D/_rels/3dmodel.model.rels'))
 for r in list(rel):
  if r.get('Target').lstrip('/') not in paths:rel.remove(r)
 for m in model.findall('m:metadata',ns):
  if m.get('name') in ['CreationDate','ModificationDate']:m.text='2026-11-16'
 with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as out:
  for path in ['[Content_Types].xml','_rels/.rels',*paths]:out.writestr(path,z.read(path))
  out.writestr('3D/3dmodel.model',E.tostring(model,encoding='utf-8',xml_declaration=True))
  out.writestr('3D/_rels/3dmodel.model.rels',E.tostring(rel,encoding='utf-8',xml_declaration=True).replace(b'ns0:',b'').replace(b'xmlns:ns0=',b'xmlns='))
  out.writestr('Metadata/model_settings.config',E.tostring(newconf,encoding='utf-8',xml_declaration=True))
  out.writestr('Metadata/project_settings.config',json.dumps(settings,indent=2))
 print(OUT)

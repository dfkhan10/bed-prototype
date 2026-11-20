import * as THREE from '../../.cache/grouped-cad/node_modules/three/build/three.module.js';
import {OrbitControls} from '../../.cache/grouped-cad/node_modules/three/examples/jsm/controls/OrbitControls.js';
const D=window.BED_DATA,P=D.manifest.params,viewport=document.getElementById('scene'),status=document.getElementById('status');
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setClearColor(0xf1f3f5);viewport.append(renderer.domElement);
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(36,1,.1,6000);camera.up.set(0,0,1);const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
scene.add(new THREE.HemisphereLight(0xffffff,0x87919d,2.5));const light=new THREE.DirectionalLight(0xffffff,3);light.position.set(200,-300,700);scene.add(light);
const colors={frame:0xb9c2cb,panel:0x969fa9,cup:0xd4d9df,ring:0x606f80,cap1:0x3d86aa,cap2:0xc48b36,cover:0x788b9d,pump:0x949fa9,valve:0x496d8a,board:0x3f7960,tube1:0x237ca9,tube2:0xd19328,tpu1:0x75b5d2,tpu2:0xe0b76a,fastener:0x69717c,cradle:0x8f9caa,clip:0x8898a9,splice:0x7b8e9e};
const geo={};for(const [name,p]of Object.entries(D.parts)){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(p.position,3));g.setIndex(p.index);g.computeVertexNormals();g.computeBoundingBox();geo[name]=g;}
const group=new THREE.Group();scene.add(group);let meshes=[],view='lowered';
const routeGroup=new THREE.Group();scene.add(routeGroup);
for(const [name,[min,max]]of Object.entries(D.manifest.spare_routes)){
  const size=max.map((v,i)=>v-min[i]);const b=new THREE.BoxGeometry(...size);
  const m=new THREE.LineSegments(new THREE.EdgesGeometry(b),new THREE.LineBasicMaterial({color:0x2e8d5b}));
  m.position.fromArray(min.map((v,i)=>(v+max[i])/2));m.name=name;routeGroup.add(m);
}
function make(instance){const kind=D.parts[instance.name].kind;const material=new THREE.MeshStandardMaterial({color:colors[kind]||0xa1abb6,roughness:.72,metalness:kind==='fastener'?.5:.05,transparent:kind.startsWith('tpu'),opacity:kind.startsWith('tpu')?.3:1,side:THREE.DoubleSide});const m=new THREE.Mesh(geo[instance.name],material);m.position.fromArray(instance.where);m.userData={...instance,kind,base:instance.where.slice()};return m;}
function load(items){for(const m of meshes){group.remove(m);m.material.dispose();}meshes=items.map(make);meshes.forEach(m=>group.add(m));}
function home(){const d=D.manifest.dimensions;const b=view==='service'?new THREE.Box3(new THREE.Vector3(-d.width/2,-d.service_length,0),new THREE.Vector3(d.width/2,0,d.height)):new THREE.Box3().setFromObject(group),c=b.getCenter(new THREE.Vector3()),s=b.getSize(new THREE.Vector3()),n=Math.max(s.x,s.y,s.z);controls.target.copy(c);camera.position.copy(c).add(new THREE.Vector3(n*.95,-n*1.3,n*1.15));controls.update();}
function apply(){const mode=document.getElementById('view').value;const coupon=mode==='coupon';if(view!==mode){load(coupon&&D.coupon?D.coupon.items:D.manifest.instances);view=mode;}
for(const m of meshes){const d=m.userData,k=d.kind;m.position.fromArray(d.base);m.scale.set(1,1,1);m.material.opacity=k.startsWith('tpu')?.3:1;m.material.transparent=k.startsWith('tpu');m.material.depthWrite=true;
let visible=true;if(!['coupon','caps','exploded'].includes(mode)&&(k.startsWith('cap')||d.cap_group))visible=false;if(k==='fastener'&&!document.getElementById('fasteners').checked)visible=false;if(k.startsWith('tpu')&&!document.getElementById('tpu').checked)visible=false;if(d.reference&&k!=='fastener'&&!k.startsWith('tpu')&&!document.getElementById('hardware').checked)visible=false;
if(mode==='caps'&&(k.startsWith('cap')||d.cap_group))m.position.z-=P.cell.stroke;
if(mode==='lowered'||mode==='caps'||mode==='alternating'){if(k.startsWith('tpu')&&(mode!=='alternating'||k==='tpu2')){const factor=(P.cell.lower_cap_underside_z-P.cell.support_z)/(P.cell.lower_cap_underside_z+P.cell.stroke-P.cell.support_z);m.scale.z=factor;m.position.z+=P.cell.support_z*(1-factor);}}
if(mode==='exploded'){let dz=k.startsWith('cap')?P.exploded.cap_lift:k==='ring'?P.exploded.ring_lift:k==='cup'?P.exploded.cup_lift:k==='panel'?-P.exploded.panel_drop:k==='cover'?P.exploded.cover_lift:d.name==='Ref_Cover_M2p5x8'?P.exploded.cover_lift+12:0;m.position.z+=dz;}
if(mode==='service'&&(m.geometry.boundingBox.min.y+d.base[1]>=-0.1||k==='cover'))visible=false;
if(mode==='routing'){if(['panel','cap1','cap2','cup','ring','cover','tpu1','tpu2','fastener'].includes(k))visible=false;if(k==='frame'){m.material.transparent=true;m.material.opacity=.15;m.material.depthWrite=false;}}
m.visible=visible;}
routeGroup.visible=mode==='routing';
status.textContent=coupon?'One-cell fit coupon · production cup, clamp and guided cap':`${D.manifest.dimensions.width} × ${D.manifest.dimensions.length} × ${D.manifest.dimensions.height} mm · 73 mm common datum · 4 pressure / 4 extraction pump positions`;
}
load(D.manifest.instances);apply();home();document.querySelectorAll('select,input').forEach(e=>e.addEventListener('change',()=>{apply();home();}));document.getElementById('home').addEventListener('click',home);
const ray=new THREE.Raycaster(),pointer=new THREE.Vector2();renderer.domElement.addEventListener('pointermove',e=>{const r=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);ray.setFromCamera(pointer,camera);const hit=ray.intersectObjects(meshes.filter(m=>m.visible),false)[0];document.getElementById('selection').textContent=hit?(hit.object.userData.cell?hit.object.userData.cell+' · ':'')+hit.object.userData.name:'';});
new ResizeObserver(()=>{const w=viewport.clientWidth,h=viewport.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h);}).observe(viewport);
function render(){requestAnimationFrame(render);controls.update();renderer.render(scene,camera);}render();

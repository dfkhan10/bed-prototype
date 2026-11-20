import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
const data=JSON.parse(document.getElementById('model').textContent);
const vp=document.getElementById('viewport');
const scene=new THREE.Scene();scene.background=new THREE.Color('#eef1f4');
const camera=new THREE.PerspectiveCamera(34,1,.1,5000);camera.up.set(0,0,1);
const renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.setClearColor('#eef1f4');vp.prepend(renderer.domElement);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.12;
scene.add(new THREE.HemisphereLight(0xffffff,0x698091,2.1));
const key=new THREE.DirectionalLight(0xffffff,2.6);key.position.set(-200,-400,600);scene.add(key);
const fill=new THREE.DirectionalLight(0xc6dcee,1.1);fill.position.set(300,100,180);scene.add(fill);
const colors={cell:0xd7dfe5,service:0xc9d4dd,bay:0x567b95,panel:0x586876,valve:0x3c9fae,screw:0xb8b9bc};
const labels={cell:'Cell deck',service:'Service cover',bay:'Electronics bay',panel:'Bottom access panel',valve:'Valve envelopes',screw:'M2.5 screw references'};
const objects=[];let separation=1,currentView='iso';
for(const part of data.parts){
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(part.vertices,3));geometry.setIndex(part.faces);geometry.computeVertexNormals();
 // Non-indexed normals preserve the actual CAD feature facets while fillets remain finely tessellated.
 const flat=geometry.toNonIndexed();flat.computeVertexNormals();
 const mesh=new THREE.Mesh(flat,new THREE.MeshStandardMaterial({color:colors[part.kind],roughness:.72,metalness:part.kind==='screw'?.5:.05,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:1,polygonOffsetUnits:1}));
 const edges=new THREE.LineSegments(new THREE.EdgesGeometry(flat,35),new THREE.LineBasicMaterial({color:0x344957,transparent:true,opacity:.25}));mesh.add(edges);
 mesh.userData=part;scene.add(mesh);objects.push(mesh);
}
const settings=new Map();
for(const kind of ['cell','service','valve','bay','panel','screw']){
 if(!objects.some(m=>m.userData.kind===kind))continue;
 const row=document.createElement('label');row.className='part';const cb=document.createElement('input');cb.type='checkbox';cb.checked=true;cb.id='show-'+kind;settings.set(kind,cb);
 const dot=document.createElement('span');dot.className='swatch';dot.style.background='#'+colors[kind].toString(16).padStart(6,'0');const txt=document.createTextNode(labels[kind]);row.append(cb,dot,txt);document.getElementById('parts').append(row);
 cb.addEventListener('change',()=>{for(const mesh of objects)if(mesh.userData.kind===kind)mesh.visible=cb.checked;});
}
function update(){
 for(const mesh of objects){const o=mesh.userData.offset;mesh.position.set(o[0]*separation,o[1]*separation,o[2]*separation);}
 document.getElementById('percent').value=Math.round(separation*100)+'%';
 document.getElementById('assembled').classList.toggle('active',separation===0);document.getElementById('exploded').classList.toggle('active',separation===1);
 document.getElementById('selection').textContent=separation===0?'Assembled design':separation===1?'Exploded assembly':'Assembly separation: '+Math.round(separation*100)+'%';
}
function fit(){
 const b=new THREE.Box3();for(const mesh of objects)if(mesh.visible)b.expandByObject(mesh);
 const center=b.getCenter(new THREE.Vector3()),size=b.getSize(new THREE.Vector3());
 controls.target.copy(center);
 const dim=Math.max(size.x,size.y,size.z),distance=dim/2/Math.tan(camera.fov*Math.PI/360)*1.4/Math.min(camera.aspect,1);
 const dir=currentView==='top'?new THREE.Vector3(0,-.001,1):currentView==='bottom'?new THREE.Vector3(.45,-.65,-1):new THREE.Vector3(.85,-1.3,1.05);
 dir.normalize();camera.position.copy(center).addScaledVector(dir,distance);camera.near=.1;camera.far=distance*10;camera.updateProjectionMatrix();controls.update();
}
function setExplode(value){separation=value/100;document.getElementById('explode').value=value;update();fit();}
document.getElementById('explode').addEventListener('input',e=>{separation=+e.target.value/100;update();});
document.getElementById('assembled').addEventListener('click',()=>setExplode(0));document.getElementById('exploded').addEventListener('click',()=>setExplode(100));
for(const b of document.querySelectorAll('[data-view]'))b.addEventListener('click',()=>{currentView=b.dataset.view;fit();});
document.getElementById('fit').addEventListener('click',fit);
const raycaster=new THREE.Raycaster(),pointer=new THREE.Vector2();let down;
renderer.domElement.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY];});
renderer.domElement.addEventListener('pointerup',e=>{
 if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>4)return;
 const r=renderer.domElement.getBoundingClientRect();pointer.set((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1);raycaster.setFromCamera(pointer,camera);
 const hit=raycaster.intersectObjects(objects.filter(m=>m.visible),false)[0];if(!hit)return;
 const d=hit.object.userData;document.getElementById('selection').textContent=d.name.replace('BedFrame_','').replaceAll('_',' ');
 document.getElementById('info').textContent=d.dimensions.map(n=>n.toFixed(1)).join(' × ')+' mm'+(d.kind==='valve'?' · Unmeasured envelope':'');
});
function resize(){const w=vp.clientWidth,h=vp.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();fit();}
new ResizeObserver(resize).observe(vp);resize();update();fit();document.getElementById('loading').hidden=true;
window.bedInspection={objects,camera,controls,renderer,setExplode,fit};
function loop(){requestAnimationFrame(loop);controls.update();renderer.render(scene,camera);}loop();

"""Dimensioned layout drawing derived from the same master JSON, in millimetres."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[2];p=json.loads((R/'design/bed_params.json').read_text());m=json.loads((R/'export/2026-11-08_grouped/2026-11-08_manifest.json').read_text());g=p['grid'];c=p['cell'];h=p['housing'];s=p['service'];W=m['dimensions']['width'];L=m['dimensions']['length'];H=m['dimensions']['height'];sd=h['service_depth'];k=.5
v=['<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297"><defs><marker id="a" markerWidth="5" markerHeight="5" refX="2.5" refY="2.5" orient="auto-start-reverse"><path d="M5 0L0 2.5L5 5" fill="none" stroke="#263746" stroke-width=".7"/></marker></defs><style>@media screen{svg{max-width:100%;height:auto}}text{font:3.4px Arial,sans-serif;fill:#263746}.dim{stroke:#263746;stroke-width:.25;fill:none;marker-start:url(#a);marker-end:url(#a)}.edge{stroke:#263746;stroke-width:.3;fill:none}.ref{stroke:#768493;stroke-width:.2;fill:none;stroke-dasharray:1 1}</style><rect width="420" height="297" fill="white"/><text x="14" y="13" style="font-size:6px">Grouped bed prototype · 4 × 3 · dimensioned layout</text><text x="14" y="21">08 November 2026 · all dimensions mm · derived layout, not an acceptance drawing for purchased hardware</text>']
def text(x,y,t):v.append(f'<text x="{x}" y="{y}">{t}</text>')
def rect(x,y,w,d,fill='none',cls='edge',rx=0):v.append(f'<rect x="{x}" y="{y}" width="{w}" height="{d}" style="fill:{fill}" class="{cls}" rx="{rx}"/>')
def circle(x,y,r):v.append(f'<circle cx="{x}" cy="{y}" r="{r}" class="edge"/>')
def dim(x1,y1,x2,y2,t,tx=None,ty=None):v.append(f'<path class="dim" d="M{x1},{y1}L{x2},{y2}"/>');text(tx if tx is not None else (x1+x2)/2+2,ty if ty is not None else (y1+y2)/2-2,str(t))
def X(x):return 40+(x+W/2)*k
def Y(y):return 40+(y+sd)*k
rect(40,40,W*k,L*k);rect(40,40,W*k,sd*k,'#eef1f4');text(44,46,'Service bay · 8 pump positions / 4 valves / stacked controller trays')
for ce in m['cells']:
 x,y=ce['x'],ce['y'];col='#d5e9f3' if ce['group']==1 else '#f6e6c9';rect(X(x-c['cap_width']/2),Y(y-c['cap_width']/2),c['cap_width']*k,c['cap_width']*k,col,rx=.4);text(X(x)-8,Y(y),ce['id']+' / G'+str(ce['group']))
for x in s['pump_centres_x']:
 for y in s['pump_centres_y']:rect(X(x-s['pump_reference_length']/2),Y(y-s['pump_reference_diameter']/2),s['pump_reference_length']*k,s['pump_reference_diameter']*k,cls='ref')
for x,y in s['valve_centres']:rect(X(x-6),Y(y-11),6,11,'#d7e0e7')
text(145,87,'Controller / driver');text(149,92,'stacked trays')
dim(40,32,40+W*k,32,W);dim(29,40,29,40+L*k,L,15,148);dim(220,40,220,Y(0),sd,222,84);dim(220,Y(0),220,40+L*k,L-sd,222,193)
dim(X(m['cells'][0]['x']),266,X(m['cells'][1]['x']),266,g['pitch']);text(40,277,'Top view · cap outline shown for optional variant · row 1 nearest service bay')
# Cell plan: active outline, hidden cup, guide and two distinct screw interfaces.
cx,cy,cs=300,93,1.1
rect(cx-c['cap_width']/2*cs,cy-c['cap_width']/2*cs,c['cap_width']*cs,c['cap_width']*cs,cls='ref',rx=.8)
rect(cx-40*cs,cy-40*cs,80*cs,80*cs,rx=6)
rect(cx-28*cs,cy-28*cs,56*cs,56*cs,'#d5e9f3',rx=6)
for x in [-c['clamp_screw_xy'],c['clamp_screw_xy']]:
 for y in [-c['clamp_screw_xy'],c['clamp_screw_xy']]:circle(cx+x*cs,cy+y*cs,1.35*cs)
for x in [-c['cup_screw_xy'][0],c['cup_screw_xy'][0]]:
 for y in [-c['cup_screw_xy'][1],c['cup_screw_xy'][1]]:circle(cx+x*cs,cy+y*cs,1.05*cs)
for y in [-p['guide']['spacing_half'],p['guide']['spacing_half']]:circle(cx,cy+y*cs,p['guide']['bore_d']/2*cs)
circle(cx,cy,c['port_clearance_d']/2*cs)
dim(cx-41*cs,40,cx+41*cs,40,82);dim(cx-28*cs,145,cx+28*cs,145,56)
text(249,155,'Cup 80 × 80; cap 82 × 82; pitch 84');text(249,162,'Clamp screws: 4 × M2.5 at (±36, ±36)');text(249,169,'Cup/frame screws: 4 × M2.5 at (±32, ±34)');text(249,176,'Guides: Ø4 / bore Ø4.8 at (0, ±36)');text(249,183,'Supported port through Ø14 cup opening')
# Side layout with alternating cells, at their nominal surface datums.
x0,z0,sk=249,235,.32
rect(x0,z0-H*sk,L*sk,H*sk,'#eef1f4');rect(x0,z0-H*sk,sd*sk,4*sk,'#788b9d')
for row in range(3):
 start=sd+g['border']+(row+.5)*g['pitch']-c['cap_width']/2
 top=H+c['stroke'] if row%2==0 else H
 rect(x0+start*sk,z0-top*sk,c['cap_width']*sk,c['cap_thickness']*sk,'#4083a5')
dim(392,z0,392,z0-H*sk,H,395,223);dim(380,z0-H*sk,380,z0-(H+c['stroke'])*sk,25,367,208)
text(249,245,'Side datums: base z0; nominal surface z73 / z98');text(249,252,'25 mm nominal rise above common lowered datum')
text(249,267,'Fit coupon first: screws, port, TPU welds and cover.');text(249,274,'Hardware envelopes, R12 hose bends and load capacity');text(249,281,'require physical checks before full-prototype printing.')
v.append('</svg>');(R/'export/2026-11-08_grouped/2026-11-08_dimensions.svg').write_text(''.join(v))

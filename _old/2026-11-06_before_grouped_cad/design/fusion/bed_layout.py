"""Derived coordinates only. All authored dimensions live in bed_params.json."""
import math


def layout(p):
    nx, ny, pitch = p['grid_n_x'], p['grid_n_y'], p['cell_pitch']
    roof = p['cell_seat_depth'] + p['cell_floor_t']
    ztop = p['cavity_h'] + roof
    width = (nx-1)*pitch + p['well_open'] + 2*p['deck_rim']
    length = (ny-1)*pitch + p['well_open'] + 2*p['deck_rim']
    max_size = p['print_max_mm']
    if width > max_size:
        raise ValueError('Deck width exceeds print limit. Reduce grid width or pitch; X split is not implemented.')
    per_tile = max(1, int((max_size-p['well_open']-2*p['deck_rim'])//pitch)+1)
    rows = list(range(ny)); tile_count=math.ceil(ny/per_tile)
    balanced=math.ceil(ny/tile_count);groups=[rows[i:i+balanced] for i in range(0,ny,balanced)]
    # Number rows from head (+Y) toward service (-Y).
    ys = [(ny-1)*pitch/2-i*pitch for i in range(ny)]
    tiles = []
    for i,g in enumerate(groups):
        upper = length/2 if i == 0 else (ys[g[0]-1]+ys[g[0]])/2-p['joint_gap']/2
        lower = -length/2 if i == len(groups)-1 else (ys[g[-1]]+ys[g[-1]+1])/2+p['joint_gap']/2
        tiles.append({'name':'BedFrame_CellDeck' if len(groups)==1 else 'BedFrame_CellDeck_'+str(i+1),
                      'rows':g,'ymin':lower,'ymax':upper})
    wall = p['electronics_wall_t']
    sx = max(width,p['e_bay_x']+2*wall)
    sy = p['e_bay_y']+2*wall
    front = -length/2-p['joint_gap']; scy = front-sy/2
    inset=p['fasteners']['perimeter_inset'];hx=sx/2-inset;hy=sy/2-inset
    perimeter=[(-hx,-hy),(0,-hy),(hx,-hy),(-hx,0),(hx,0),(-hx,hy),(0,hy),(hx,hy)]
    xs=p['joint_screw_x']
    if len(xs)!=p['fasteners']['joint_screw_count']:raise ValueError('Joint count / X list disagree')
    if any(abs(x)+5>width/2 for x in xs):raise ValueError('Joint X outside deck')
    if max(sx,sy)>max_size:raise ValueError('Service module exceeds print limit')
    if pitch-p['well_open'] < p['rib_t']:raise ValueError('Cell web thinner than rib_t')
    cols=p['valve_cols'];n=nx*ny;vrows=math.ceil(n/cols)
    if (vrows-1)*p['valve_pitch_y']+p['valve_l']+2*p['valve_fit_clearance'] > p['e_bay_y']-2*p['rim_flange_w']:
        raise ValueError('Valve bank does not fit service cavity')
    cells=[{'id':chr(65+x)+str(y+1),'x':(x-(nx-1)/2)*pitch,'y':ys[y],'col':x,'row':y} for y in rows for x in range(nx)]
    valves=[{'id':c['id'],'x':(i%cols-(cols-1)/2)*p['valve_pitch_x'],
             'y':scy+((vrows-1)/2-i//cols)*p['valve_pitch_y']} for i,c in enumerate(cells)]
    f=p['fasteners']
    if f['primary']!='M2.5' or f['mode']!='thread_forming':raise ValueError('This revision supports M2.5 thread-forming screws only; size inserts explicitly before changing mode.')
    if f['rim_screw_count']!=len(perimeter) or f['panel_screw_count']!=len(perimeter):raise ValueError('Perimeter screw counts must match the shared eight-point table')
    engage=f['screw_length_mm']-p['panel_t']
    if not (0 < engage <= f['boss_h']-1):raise ValueError('Screw length incompatible with panel grip / blind boss')
    return dict(width=width,length=length,roof=roof,ztop=ztop,tiles=tiles,cells=cells,valves=valves,
                service_x=sx,service_y=sy,service_cy=scy,service_front=front,mate_y=-length/2,
                screw_points=[(x,y+scy) for x,y in perimeter],joint_xs=xs,screw_engagement_mm=engage)

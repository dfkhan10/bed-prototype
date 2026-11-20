"""Derived layout and explicit design checks. Dimensions come only from JSON."""
import math

def layout(p):
    g,c,h,q,f,t=p['grid'],p['cell'],p['housing'],p['guide'],p['fasteners'],p['tubes']
    pitch=g['pitch'];width=g['columns']*pitch+2*g['border'];length=g['rows']*pitch+2*g['border']
    cells=[dict(id=chr(65+col)+str(row+1),x=(col-(g['columns']-1)/2)*pitch,y=g['border']+(row+.5)*pitch,group=g['groups'][row][col],row=row,col=col) for row in range(g['rows']) for col in range(g['columns'])]
    low=c['lower_cap_underside_z'];raised=low+c['stroke'];ringtop=c['support_z']+c['clamp_gap']+c['ring_thickness']
    checks={
      'twelve_cells':len(cells)==12,
      'six_in_each_group':all(sum(ce['group']==n for ce in cells)==6 for n in [1,2]),
      'checkerboard':all(g['groups'][r][col]!=g['groups'][rr][cc] for r in range(g['rows']) for col in range(g['columns']) for rr,cc in [(r+1,col),(r,col+1)] if rr<g['rows'] and cc<g['columns']),
      'flange_stack':abs(c['active_width']+2*c['weld_land']+2*c['dry_flange']-c['cup_width'])<1e-6,
      'cap_covers_flange':c['cap_width']>=c['cup_width'],
      'cap_gap_positive':pitch>c['cap_width'],
      'raised_datum':abs(raised+c['cap_thickness']-h['outer_top_z'])<1e-6,
      'stroke_20_to_30':20<=c['stroke']<=30,
      'upper_stop':abs(raised-q['post_length']-q['shoulder_z'])<1e-6,
      'lower_stop_above_ring':low>ringtop,
      'stop_screw_above_base':low-q['post_length']-q['washer_t']-f['head_h']>=h['base_t']+1-1e-6,
      'guide_clearance':q['bore_d']>q['post_d'],
      'dry_guide_holes':q['spacing_half']-q['bore_d']/2>c['active_width']/2+c['weld_land'],
      'dry_clamp_holes':c['clamp_screw_xy']-f['clearance_d']/2>c['active_width']/2+c['weld_land'],
      'tube_bore':t['od']>t['id']>0,
      'clamp_tip_clearance':f['clamp_pilot_depth']-(f['clamp_length']-(ringtop-f['head_h']-c['support_z']))>=1-1e-6,
      'cup_tip_clearance':f['cup_pilot_depth']-(f['cup_length']-h['column_grip'])>=1-1e-6,
      'panel_tip_clearance':h['panel_boss_h']-1-(f['panel_length']-(h['base_t']-f['head_h']))>=1-1e-6,
    }
    if not all(checks.values()):raise ValueError('Layout checks failed: '+', '.join(k for k,v in checks.items() if not v))
    active=c['active_width']**2-(4-math.pi)*c['active_corner_r']**2
    cap=c['cap_width']**2-(4-math.pi)*c['cap_corner_r']**2
    return dict(width=width,field_length=length,service_length=h['service_depth'],length=length+h['service_depth'],height=h['outer_top_z'],cap_gap=pitch-c['cap_width'],cap_edge_border=g['border']+(pitch-c['cap_width'])/2,cap_top_raised=raised+c['cap_thickness'],cap_top_lowered=low+c['cap_thickness'],active_area_per_cell_mm2=active,cap_area_per_cell_mm2=cap,cap_coverage_of_field=12*cap/(width*length),active_coverage_of_field=12*active/(width*length),checks=checks,cells=cells)

"""Preliminary ideal-gas sizing, not measured pump performance or a pressure rating.
Opening width is read from the CAD master. Height/shape/pressure/time below are
explicit sensitivity scenarios; they do not update manufacturing dimensions.
All flow values use the same ambient-pressure, same-temperature gas reference.
"""
from pathlib import Path
import json, math

ROOT=Path(__file__).resolve().parents[2]
P=json.loads((ROOT/'design/bed_params.json').read_text())
PATM_KPA=101.325

def cell_volume_ml(width_mm,rise_mm,shape_factor):
    return width_mm**2*rise_mm*shape_factor/1000

def tube_volume_ml(id_mm,length_mm):
    return math.pi*(id_mm/2)**2*length_mm/1000

def fill_air_ml(final_cell_ml,initial_cell_ml,final_gauge_kpa,initial_gauge_kpa,tube_ml):
    return ((PATM_KPA+final_gauge_kpa)*final_cell_ml-(PATM_KPA+initial_gauge_kpa)*initial_cell_ml+(final_gauge_kpa-initial_gauge_kpa)*tube_ml)/PATM_KPA

def demand_l_min(cells,air_ml,time_s,margin):
    return cells*air_ml/1000*60/time_s*margin

def bank_pumps(required_l_min,installed_pump_l_min):
    return math.ceil(required_l_min/installed_pump_l_min) if required_l_min else 0

def calculate():
    width=P['cell']['active_width'];line=tube_volume_ml(4,600)
    shapes=[('low',20,.5),('nominal',25,.7),('upper',30,1.0)]
    volumes={name:cell_volume_ml(width,h,k) for name,h,k in shapes}
    cases=[]
    for cells in [3,6,12]:
        for time in [10,20,30]:
            row={'simultaneous_inflating_cells':cells,'fill_time_s':time,'flow_l_min_ambient':{}}
            for name,_,_ in shapes:
                air=fill_air_ml(volumes[name],0,10,0,line)
                row['flow_l_min_ambient'][name]=round(demand_l_min(cells,air,time,1.5),4)
            cases.append(row)
    examples=[]
    # Same inflation/evacuation air-demand budget is a conservative placeholder.
    # Actual evacuation must use the vacuum curve and measured initial/final states.
    for nup,ndown in [(3,3),(6,6),(12,0)]:
        assert nup+ndown<=12
        for time in [10,20]:
            for effective in [.5,1.0,2.0]:
                air=fill_air_ml(volumes['nominal'],0,10,0,line)
                qplus=demand_l_min(nup,air,time,1.5);qminus=demand_l_min(ndown,air,time,1.5)
                np=bank_pumps(qplus,effective);nv=bank_pumps(qminus,effective)
                examples.append({'inflating':nup,'deflating':ndown,'seconds':time,'hypothetical_effective_flow_per_pump_l_min_ambient':effective,'pressure_pumps':np,'vacuum_pumps':nv,'total_pumps':np+nv})
    return {'status':'analysis scenarios; exact kit not identified; no pump count selected',
        'confirmed':{'cells':12,'cell_rise_mm':[20,30],'bladder':'heat-welded TPU film','simultaneous_inflate_deflate':True,'controllers':1},
        'assumptions':{'opening_from_current_master_mm':width,'pressure_scenario_kpa_gauge':10,'initial_cell_volume_ml':0,'reserve_factor':1.5,'tube_id_mm':4,'tube_length_mm':600,'shape_factor_range':[.5,1.0],'nominal_shape_factor':.7,'nominal_rise_mm':25,'ambient_pressure_kpa':PATM_KPA},
        'volume_scenarios_ml':volumes,'tube_volume_ml':line,'fill_cases':cases,'hypothetical_pump_count_examples':examples,
        'ideal_force_scale_not_load_rating':[{'gauge_kpa':g,'ideal_force_n_per_cell':g*1000*(width/1000)**2} for g in [5,10,20]],
        'limitations':['A pillow is not a rectangular piston; shape factors are unmeasured.','Gussets/preforming/film stretch affect volume and force.','Pump flow is required at the operating pressure/vacuum after tubing/valves, with flow-reference conversion.','Reserve factor is provisional; leakage was not measured.','Vacuum count examples use a placeholder equal air-demand budget, not a measured vacuum fill model.']}

if __name__=='__main__':
    # Dimensional sanity checks: 1 litre at 1 atm, compressed to 2 atm, needs 1 extra litre.
    assert abs(fill_air_ml(1000,1000,PATM_KPA,0,0)-1000)<1e-9
    assert abs(cell_volume_ml(100,100,1)-1000)<1e-9
    assert bank_pumps(1.65,1)==2 and bank_pumps(1.65,2)==1
    report=calculate()
    (ROOT/'work/2026-11-06_pump_sizing_scenarios.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Volume scenarios ml:',report['volume_scenarios_ml'])
    for r in report['fill_cases']:
        if r['fill_time_s'] in [10,20]:print(r)

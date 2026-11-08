"""Reproducible planning estimate, RUB. No measured model effects are assumed."""
from decimal import Decimal as D
import json
from pathlib import Path

def calculate():
    setup_roles = {'data': (2,220000), 'ml': (2,280000), 'backend': (2,260000),
                   'ui': (1,240000), 'sre': (1,280000), 'security': (.5,320000),
                   'qa': (1,180000), 'pm': (.5,240000)}
    setup = sum(D(str(n))*D(rate) for n,rate in setup_roles.values())
    # 730 is a planning average; actual billing is time-based.
    compute = (D(32)*D('1.24')+D(128)*D('.33'))*730
    snapshot = D(2048)*D('.0051')*730
    infra = (compute+snapshot)*2  # 100% explicit overhead estimate, not a provider tariff
    support = D(107000)
    quarterly_regression = D(140000)
    monthly = infra+support+quarterly_regression/3
    pilot_expert_hours = D(720)
    baseline_month_hours = D(10000)*12/60
    effective_hour = D(45000000)/(12*baseline_month_hours)
    migration = D(400000)
    out = dict(setup_roles_rub=setup, compute_month=compute, snapshots_month=snapshot,
        infra_month=infra, support_month=support, regression_quarter=quarterly_regression,
        run_month=monthly, baseline_month_hours=baseline_month_hours,
        effective_hour=effective_hour, pilot_expert_opportunity=pilot_expert_hours*effective_hour)
    for months in (12,24):
        tco = setup+monthly*months+migration
        out[f'tco_{months}_direct']=tco
        out[f'tco_{months}_with_pilot_opportunity']=tco+pilot_expert_hours*effective_hour
        out[f'current_process_{months}']=D(45000000)*D(months)/12
        out[f'combined_{months}']=out[f'current_process_{months}']+tco
        out[f'increment_per_all_operation_{months}']=tco/(D(22500000)*months)
        out[f'increment_per_review_{months}']=tco/(D(10000)*months)
    # Capacity value only: 4 minutes saved per review, no payroll reduction assumed.
    out['capacity_hours_month_4min']=D(10000)*4/60
    out['capacity_value_year_4min']=out['capacity_hours_month_4min']*effective_hour*12
    # Alternative mutually exclusive scenario: extra useful investigations valued externally.
    out['required_net_value_per_extra_case_100_month_24']=out['tco_24_direct']/(24*100)
    out['infra_double_24_direct']=out['tco_24_direct']+infra*24
    out['rates_plus30pct_24_direct']=out['tco_24_direct']+(setup+support*24+quarterly_regression*8)*D('.30')
    out['six_month_delay_24_direct']=out['tco_24_direct']+monthly*6
    return out

if __name__=='__main__':
    values={k:float(v.quantize(D('.000001') if 'per_all_operation' in k else D('.01'))) for k,v in calculate().items()}
    result=json.dumps(values,ensure_ascii=False,indent=2)+'\n'
    (Path(__file__).parent/'calculation.json').write_text(result,encoding='utf-8')
    print(result)

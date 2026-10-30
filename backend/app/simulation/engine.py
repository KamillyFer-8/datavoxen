"""Modelo 2026.1: adaptação fiel do núcleo auditado, sem dependências de I/O."""
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE = json.loads((Path(__file__).with_name('premissas.json')).read_text(encoding='utf-8'))
VERSION = '2026.1'
MODEL_HASH = hashlib.sha256(json.dumps(BASE, sort_keys=True).encode()).hexdigest()
CAT = BASE['catalogo']
STRATEGIES = BASE['estrategias']
SCENARIOS = BASE['cenarios']
MONEY = {'gross', 'refunds', 'platform', 'tax', 'net', 'variable', 'production',
         'content', 'operations', 'marketing', 'costs', 'flow', 'cash', 'usable_cash'}


def money(value):
    return float(Decimal(str(value)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))


def parameters(strategy='A', scenario='central', overrides=None):
    p = dict(SCENARIOS[scenario])
    p.update(price_mult={k: 1.0 for k in CAT}, elasticity=1.25,
             activity=BASE['retencao_mensal_hipotetica'][:], capital=BASE['capital'],
             reserve=BASE['reserva'], fee=BASE['taxas']['plataforma'],
             tax=BASE['taxas']['tributos'], refund=BASE['taxas']['reembolso'],
             operations=BASE['custo_operacional_mensal'], production=STRATEGIES[strategy][2],
             content=STRATEGIES[strategy][3], unit_cost={k: v['unit_cost'] for k,v in CAT.items()},
             attractiveness={k: v['base'] for k,v in CAT.items()})
    p.update(overrides or {})
    p.pop('init', None)  # Parâmetro legado sem efeito no motor original.
    return p


def shares(keys, p):
    outside = 1-sum(p['attractiveness'].values())
    weights = {k: p['attractiveness'][k]/outside*p['eng']*p['price_mult'][k]**(-p['elasticity']) for k in keys}
    den = 1+sum(weights.values())
    return {k:v/den for k,v in weights.items()}, 1/den


def run(strategy='A', scenario='central', overrides=None):
    p = parameters(strategy, scenario, overrides)
    keys = STRATEGIES[strategy][1]
    probs, none = shares(keys, p)
    out = []
    cash = p['capital']
    for m in range(1,13):
        active = sum(p['acq']*p['activity'][m-j-1] for j in range(m))
        units = {k:active*probs[k] for k in keys}
        gross = sum(units[k]*CAT[k]['price']*p['price_mult'][k] for k in keys)*p['spend']
        refunds = gross*p['refund']
        platform = (gross-refunds)*p['fee']
        tax = (gross-refunds)*p['tax']
        variable = sum(units[k]*p['unit_cost'][k] for k in keys)
        net = gross-refunds-platform-tax
        production = p['production'] if m == 1 else 0
        content = p['content'] if m in (4,7,10) else 0
        operations = p['operations']*p['opex']
        marketing = p['acq']*p['cac']
        costs = variable+production+content+operations+marketing
        flow = net-costs
        cash += flow
        out.append(dict(strategy=strategy, scenario=scenario, month=m, new=p['acq'], active=active,
                        p_buy=1-none, buyers=sum(units.values()),
                        **{f'units_{k}':units.get(k,0) for k in CAT}, gross=gross, refunds=refunds,
                        platform=platform,tax=tax,net=net,variable=variable,production=production,
                        content=content,operations=operations,marketing=marketing,costs=costs,
                        flow=flow,cash=cash,usable_cash=cash-p['reserve']))
    return out


def cohorts(strategy, scenario, p):
    probs, _ = shares(STRATEGIES[strategy][1], p)
    data = []
    for start in range(1,13):
        active = sum(p['acq']*p['activity'][age] for age in range(13-start))
        gross = sum(active*probs[k]*CAT[k]['price']*p['price_mult'][k] for k in probs)*p['spend']
        contribution = gross*(1-p['refund'])*(1-p['fee']-p['tax'])-sum(active*probs[k]*p['unit_cost'][k] for k in probs)
        data.append(dict(cohort_month=start, horizon_months=13-start, acquired=p['acq'],
                         active_player_months=active, gross=money(gross), contribution_before_CAC=money(contribution),
                         contribution_per_acquired=money(contribution/p['acq']), CAC=p['cac'],
                         net_after_CAC=money(contribution-p['acq']*p['cac'])))
    return data


def result(strategy='A', scenario='central', overrides=None):
    p = parameters(strategy, scenario, overrides)
    rows = run(strategy, scenario, p)
    totals = {k:money(sum(r[k] for r in rows)) for k in MONEY if k not in ('cash','usable_cash')}
    active_months = sum(r['active'] for r in rows)
    acquired = sum(r['new'] for r in rows)
    buyer_months = sum(r['buyers'] for r in rows)
    # Trabalhar sem arredondamento intermediário preserva o motor original.
    contribution = sum(r['net']-r['variable'] for r in rows)
    fixed = sum(r['operations']+r['production']+r['content'] for r in rows)
    marginal_per_acquired = contribution/acquired
    net_acquisition = marginal_per_acquired-p['cac']
    summary = dict(**totals, active_player_months=active_months, acquired=acquired,
                   buyers_months=buyer_months, cac=p['cac'], contribution=money(contribution),
                   recoverable_contribution=money(marginal_per_acquired),
                   ltv_partial=cohorts(strategy,scenario,p)[0]['contribution_per_acquired'],
                   arpu=money(sum(r['gross'] for r in rows)/active_months) if active_months else 0,
                   arppu=money(sum(r['gross'] for r in rows)/buyer_months) if buyer_months else None,
                   cash=money(rows[-1]['cash']), reserve=p['reserve'],
                   insufficient_month=next((r['month'] for r in rows if r['usable_cash']<0),None),
                   cash_negative_month=next((r['month'] for r in rows if r['cash']<0),None),
                   max_cac_after_fixed=money((contribution-fixed)/acquired),
                   break_even_acquired= fixed/net_acquisition if net_acquisition>0 else None,
                   break_even_active_months=(fixed+acquired*p['cac'])/(contribution/active_months) if contribution>0 and active_months else None)
    probs, none = shares(STRATEGIES[strategy][1],p)
    products = [dict(id=k, name=CAT[k]['name'], price=CAT[k]['price']*p['price_mult'][k],
                     probability=probs[k], units=sum(r[f'units_{k}'] for r in rows),
                     gross=money(sum(r[f'units_{k}']*CAT[k]['price']*p['price_mult'][k]*p['spend'] for r in rows))) for k in probs]
    monthly=[{**{k:money(v) if k in MONEY else v for k,v in r.items()},'cumulative_flow':money(sum(x['flow'] for x in rows[:i+1]))} for i,r in enumerate(rows)]
    return dict(model_version=VERSION, model_hash=MODEL_HASH, strategy=strategy,scenario=scenario,
                parameters=p,summary=summary,months=monthly,
                cohorts=cohorts(strategy,scenario,p),products=products,none_probability=none)


def sensitivity(strategy, scenario, p):
    base = sum(r['flow'] for r in run(strategy,scenario,p))
    out = []
    for key, name in [('cac','CAC'),('acq','Novos jogadores'),('eng','Atratividade'),('operations','Operação'),('price_mult','Preços')]:
        values = []
        for factor in (.85,1.15):
            alt = dict(p)
            alt[key] = {k:v*factor for k,v in p[key].items()} if key=='price_mult' else p[key]*factor
            values.append(money(sum(r['flow'] for r in run(strategy,scenario,alt))-base))
        out.append(dict(parameter=key,name=name,lower=values[0],upper=values[1]))
    return out

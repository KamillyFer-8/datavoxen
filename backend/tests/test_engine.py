import csv
import json
import math
from pathlib import Path
import pytest
from app.simulation.engine import CAT, SCENARIOS, STRATEGIES, money, parameters, result, run, shares, sensitivity

ROOT=Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('st',STRATEGIES)
@pytest.mark.parametrize('sc',SCENARIOS)
def test_original_all_rows(st,sc):
    with (ROOT/'docs/references/original/modelo/projecao_12_meses.csv').open() as f:
        expected=[r for r in csv.DictReader(f) if r['strategy']==st and r['scenario']==sc]
    actual=run(st,sc)
    assert len(expected)==len(actual)==12
    for old,new in zip(expected,actual):
        for key in old:
            if key not in ('strategy','scenario'): assert math.isclose(float(old[key]),new[key],rel_tol=1e-12,abs_tol=1e-8),key
    targets=json.loads((ROOT/'docs/methodology/regression.json').read_text())
    assert sum(r['flow'] for r in actual)==pytest.approx(targets[f'{st}/{sc}'],abs=1e-8)


def test_cohorts_original():
    with (ROOT/'docs/references/original/modelo/coortes_e_ltv.csv').open() as f:
        for row in csv.DictReader(f):
            actual=result(row['strategy'])['cohorts'][int(row['cohort_month'])-1]
            for key in actual:
                if key in row: assert actual[key]==pytest.approx(float(row[key]),abs=.0051)


def test_original_price_sensitivity():
    with (ROOT/'docs/references/original/modelo/sensibilidade_precos.csv').open() as f:
        for row in csv.DictReader(f):
            actual=run(row['strategy'],overrides={'price_mult':{k:float(row['price_factor']) for k in CAT},'elasticity':float(row['elasticity'])})
            assert sum(x['flow'] for x in actual)==pytest.approx(float(row['financial']),abs=1e-8)
            assert sum(x['gross'] for x in actual)==pytest.approx(float(row['gross']),abs=1e-8)


def test_prices_and_substitution():
    p=parameters('C'); base,_=shares(CAT,p)
    p['price_mult']['traje']=1.2
    alt,none=shares(CAT,p)
    assert alt['traje']<base['traje']
    assert alt['efeito']>base['efeito']
    assert sum(alt.values())+none==pytest.approx(1)
    assert result('C',overrides={'price_mult':p['price_mult']})['summary']['gross']!=result('C')['summary']['gross']


def test_financial_identities_and_break_even():
    r=result()
    for row in run():
        assert row['net']==pytest.approx(row['gross']*.7742)
        assert row['flow']==pytest.approx(row['net']-row['costs'])
        assert row['buyers']<=row['active']
    assert r['summary']['break_even_acquired'] is None
    assert r['summary']['max_cac_after_fixed']<0
    assert r['summary']['insufficient_month'] is not None
    assert money(2.675)==2.68
    assert money(-2.675)==-2.68
    assert result(overrides={'cac':12})['summary']['flow']==pytest.approx(r['summary']['flow']-144000,abs=.01)
    s=sensitivity('A','central',r['parameters'])
    assert next(x for x in s if x['parameter']=='cac')['upper']<0


def test_break_even_keeps_acquisition_costs():
    p={'cac':.01,'eng':50}
    r=result(overrides=p)
    n=r['summary']['break_even_acquired']
    assert n is not None
    exact=run(overrides={**p,'acq':n/12})
    assert sum(x['flow'] for x in exact)==pytest.approx(0,abs=1e-6)

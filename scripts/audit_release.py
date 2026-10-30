"""Verifica fontes, hashes, base e motor sem modificar resultados de referência."""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app import archive
from app.simulation.engine import STRATEGIES,SCENARIOS,result


def main():
    manifest=json.loads((archive.DATA/'manifest.json').read_text(encoding='utf-8'))
    checks={}
    for name,meta in manifest.items():
        content=(archive.DATA/name).read_bytes()
        checks['sha256:'+name]=len(content)==meta['bytes'] and hashlib.sha256(content).hexdigest()==meta['sha256']
    with zipfile.ZipFile(ROOT/'docs/references/Modelo_Datavoxen.zip') as source:
        for name in source.namelist():
            if name.endswith('/'): continue
            checks['zip:'+name]=source.read(name)==(ROOT/'docs/references/original'/name).read_bytes()
    checks['pdf_original']= (archive.DATA/'estudo-original.pdf').read_bytes()==(ROOT/'docs/references/Datavoxen_Relatorio_Encerrado_2026.pdf').read_bytes()
    for strategy in STRATEGIES:
        for scenario in SCENARIOS:
            checks[f'resultado:{strategy}/{scenario}']=archive.reference(strategy,scenario)==result(strategy,scenario)
    with archive.connect() as db:
        checks['integrity']=db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        checks['foreign_keys']=not db.execute('PRAGMA foreign_key_check').fetchall()
        counts={name:db.execute(f'SELECT COUNT(*) FROM {name}').fetchone()[0] for name in ['studies','reference_runs','monthly_results','cohort_results','product_results','benchmarks']}
    report={'date':'2026-10-30','checks':checks,'counts':counts,'central':{st:archive.reference(st)['summary'] for st in STRATEGIES},'all_results':archive.rows('SELECT strategy,scenario,gross,net,costs,flow,cash FROM financial_comparison ORDER BY strategy,scenario')}
    target=ROOT/'docs/audit/data-evidence.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True),encoding='utf-8')
    failures=[name for name,passed in checks.items() if not passed]
    print(f'{len(checks)} verificações de fontes/dados; falhas: {failures}; contagens: {counts}')
    if failures: raise SystemExit(1)


if __name__=='__main__': main()

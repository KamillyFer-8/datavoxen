"""Gera a base pública imutável e os arquivos de distribuição do estudo."""
import csv
import hashlib
import json
import shutil
import sqlite3
import sys
import tempfile
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.simulation.engine import BASE, CAT, STRATEGIES, SCENARIOS, VERSION, MODEL_HASH, result
DATA = ROOT / 'backend/data'


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def insert(connection, table, row):
    keys = list(row)
    connection.execute(f'INSERT INTO {table} ({",".join(keys)}) VALUES ({",".join("?" for _ in keys)})', list(row.values()))


def build_database(target):
    with closing(sqlite3.connect(target)) as db:
        db.executescript((ROOT / 'backend/database/schema.sql').read_text(encoding='utf-8'))
        insert(db, 'studies', dict(id='ilhas-de-orion', name='Ilhas de Órion', studio='Estúdio Horizonte', nature='Estudo fictício, hipóteses não calibradas', study_date='2026-10-29', months=12))
        insert(db, 'model_versions', dict(id=VERSION, study_id='ilhas-de-orion', checksum=MODEL_HASH, assumptions_json=encode(BASE)))
        for key, item in CAT.items(): insert(db, 'products', dict(id=key, **item))
        for key, (name, products, production, content) in STRATEGIES.items():
            insert(db, 'strategies', dict(id=key, name=name, production=production, content=content))
            for position, product in enumerate(products): insert(db, 'strategy_products', dict(strategy_id=key, product_id=product, position=position))
        for key, value in SCENARIOS.items(): insert(db, 'scenarios', dict(id=key, parameters_json=encode(value)))
        for strategy in STRATEGIES:
            for scenario in SCENARIOS:
                data = result(strategy, scenario)
                run_id = f'{strategy}-{scenario}'
                insert(db, 'reference_runs', dict(id=run_id, model_version=VERSION, strategy=strategy, scenario=scenario, parameters_json=encode(data['parameters']), summary_json=encode(data['summary']), none_probability=data['none_probability']))
                for row in data['months']:
                    insert(db, 'monthly_results', dict(run_id=run_id, **{k:v for k,v in row.items() if k not in ('strategy','scenario')}))
                for row in data['cohorts']: insert(db, 'cohort_results', dict(run_id=run_id, **row))
                for row in data['products']:
                    insert(db, 'product_results', dict(run_id=run_id, product_id=row['id'], **{k:v for k,v in row.items() if k not in ('id','name')}))
        offers = json.loads((ROOT/'backend/app/benchmarks.json').read_text(encoding='utf-8'))
        sources = {}
        for item in offers:
            url = item['source_url']
            if url not in sources:
                source_id = f'benchmark-{len(sources)+1}'
                sources[url] = source_id
                insert(db, 'sources', dict(id=source_id, title=f"{item['game']} · {item['channel']}", url=url, consulted_at=item['consulted_at'], status='Histórico documentado no estudo; sem reconfirmação atual'))
            insert(db, 'benchmarks', dict(source_id=sources[url], **{k:v for k,v in item.items() if k != 'source_url'}))
        insert(db, 'sources', dict(id='study-pdf', title='Relatório encerrado Datavoxen 2026 — documento fornecido', url='estudo-original.pdf', consulted_at='2026-10-29', status='Original preservado, sem edição'))
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
        db.commit()


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=DATA) as temporary:
        target = Path(temporary) / 'study.sqlite3'
        build_database(target)
        target.replace(DATA / 'datavoxen.sqlite3')
    originals = ROOT / 'docs/references'
    copies = {
        'estudo-original.pdf': originals/'Datavoxen_Relatorio_Encerrado_2026.pdf',
        'modelo-original.zip': originals/'Modelo_Datavoxen.zip',
        'premissas.json': originals/'original/modelo/premissas.json',
        'projecao-original.csv': originals/'original/modelo/projecao_12_meses.csv',
        'coortes-originais.csv': originals/'original/modelo/coortes_e_ltv.csv',
        'sensibilidade-original.csv': originals/'original/modelo/sensibilidade_precos.csv',
    }
    for name, source in copies.items(): shutil.copyfile(source, DATA/name)
    rows = [dict(strategy=st, scenario=sc, **result(st,sc)['summary']) for st in STRATEGIES for sc in SCENARIOS]
    with (DATA/'comparacao-cenarios.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer=csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter=';')
        writer.writeheader(); writer.writerows(rows)
    public_names = sorted([*copies, 'datavoxen.sqlite3', 'comparacao-cenarios.csv'])
    manifest = {name: {'bytes':(DATA/name).stat().st_size, 'sha256':hashlib.sha256((DATA/name).read_bytes()).hexdigest()} for name in public_names}
    (DATA/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Base: {DATA / "datavoxen.sqlite3"} ({manifest["datavoxen.sqlite3"]["bytes"]} bytes)')
    print('12 execuções, 144 resultados mensais, 144 coortes, 40 resultados por produto e 14 benchmarks.')


if __name__ == '__main__': main()

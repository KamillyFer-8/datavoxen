"""Consulta de uma edição pública do estudo. Nunca cria nem altera o banco."""
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data'
DATABASE = DATA / 'datavoxen.sqlite3'


class ArchiveVersionError(RuntimeError):
    pass


@contextmanager
def connect():
    db = sqlite3.connect(DATABASE.as_uri() + '?mode=ro&immutable=1', uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute('PRAGMA query_only = ON')
        from .simulation.engine import MODEL_HASH, VERSION
        version=db.execute('SELECT id,checksum FROM model_versions').fetchall()
        if len(version)!=1 or version[0]['id']!=VERSION or version[0]['checksum']!=MODEL_HASH:
            raise ArchiveVersionError('Versão da base divergente')
        yield db
    finally:
        db.close()


def rows(sql, values=()):
    with connect() as db:
        return [dict(row) for row in db.execute(sql, values).fetchall()]


def reference(strategy='A', scenario='central'):
    from .simulation.engine import MODEL_HASH, VERSION
    with connect() as db:
        record = db.execute('SELECT r.*, m.checksum FROM reference_runs r JOIN model_versions m ON m.id=r.model_version WHERE r.strategy=? AND r.scenario=?', (strategy, scenario)).fetchone()
        if record is None: raise LookupError('Referência não encontrada')
        if record['model_version'] != VERSION or record['checksum'] != MODEL_HASH:
            raise ArchiveVersionError('Versão do banco e motor divergentes; regenere a base do estudo.')
        run_id = record['id']
        months = []
        for item in db.execute('SELECT * FROM monthly_results WHERE run_id=? ORDER BY month', (run_id,)):
            months.append(dict(strategy=strategy, scenario=scenario, **{k:v for k,v in dict(item).items() if k!='run_id'}))
        cohorts = [{k:v for k,v in dict(item).items() if k!='run_id'} for item in db.execute('SELECT * FROM cohort_results WHERE run_id=? ORDER BY cohort_month', (run_id,))]
        products = [dict(item) for item in db.execute('SELECT p.product_id AS id, c.name, p.price, p.probability, p.units, p.gross FROM product_results p JOIN products c ON c.id=p.product_id JOIN strategy_products s ON s.product_id=c.id AND s.strategy_id=? WHERE p.run_id=? ORDER BY s.position', (strategy,run_id))]
        return dict(model_version=record['model_version'], model_hash=record['checksum'], strategy=strategy, scenario=scenario, parameters=json.loads(record['parameters_json']), summary=json.loads(record['summary_json']), months=months, cohorts=cohorts, products=products, none_probability=record['none_probability'])

import sqlite3
from contextlib import closing
import sys
from pathlib import Path
import pytest
from app import archive
from app.simulation.engine import STRATEGIES, SCENARIOS, result

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from build_study import build_database


@pytest.mark.parametrize('strategy',STRATEGIES)
@pytest.mark.parametrize('scenario',SCENARIOS)
def test_all_stored_results_match_engine(strategy,scenario):
    assert archive.reference(strategy,scenario)==result(strategy,scenario)


def test_schema_constraints_and_counts():
    with archive.connect() as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
        assert db.execute('PRAGMA user_version').fetchone()[0]==1
        for table,count in [('studies',1),('reference_runs',12),('monthly_results',144),('cohort_results',144),('product_results',40),('benchmarks',14)]:
            assert db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]==count
        with pytest.raises(sqlite3.OperationalError): db.execute('DELETE FROM reference_runs')


def test_database_regeneration_is_reproducible(tmp_path):
    first,second=tmp_path/'first.sqlite3',tmp_path/'second.sqlite3'
    build_database(first);build_database(second)
    assert first.read_bytes()==second.read_bytes()
    # Cabeçalhos SQLite podem variar entre versões da biblioteca nos sistemas.
    # O conteúdo da edição entregue deve permanecer idêntico em qualquer SO.
    def snapshot(path):
        with closing(sqlite3.connect(path)) as db:
            tables=[row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
            return {table:db.execute(f'SELECT * FROM {table} ORDER BY rowid').fetchall() for table in tables}
    assert snapshot(first)==snapshot(archive.DATABASE)

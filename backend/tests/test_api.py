import csv
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c: yield c


def test_preview_exports(client):
    r=client.post('/api/simulations/preview',json={})
    assert r.status_code==200
    assert r.json()['summary']['flow']==-1160759.47
    exported=client.post('/api/export',json={}).content.decode('utf-8-sig')
    data=list(csv.DictReader(io.StringIO(exported),delimiter=';'))
    assert float(data[0]['gross'])==r.json()['months'][0]['gross']
    from pypdf import PdfReader
    pdf=client.post('/api/export?format=pdf',json={})
    assert pdf.content.startswith(b'%PDF')
    assert 'Hipóteses' in ''.join(p.extract_text() for p in PdfReader(io.BytesIO(pdf.content)).pages)


@pytest.mark.parametrize('payload',[{'overrides':{'acq':0}},{'overrides':{'price_mult':{'traje':0}}},{'overrides':{'fee':.8,'tax':.8}},{'strategy':'D'},{'overrides':{'activity':[1]}},{'overrides':{'reserve':1000000}},{'overrides':{'unknown':1}},{'name':' '}])
def test_invalid(client,payload): assert client.post('/api/simulations/preview',json=payload).status_code==422


def test_public_study_needs_no_credentials(client,monkeypatch):
    for key in ('DATABASE_URL','SUPABASE_URL','SUPABASE_ANON_KEY'):
        monkeypatch.delenv(key,raising=False)
    health=client.get('/api/health').json()
    assert health['database']=='sqlite' and health['read_only'] is True
    assert health['authentication_required'] is False
    assert client.post('/api/simulations',json={}).status_code==404
    assert len(client.get('/api/comparison').json())==12
    assert len(client.get('/api/products').json())==5
    assert len(client.get('/api/strategies').json())==3
    assert len(client.get('/api/benchmarks').json())==14


def test_public_downloads_and_original_pdf(client):
    import hashlib
    from pathlib import Path
    resources=client.get('/api/files').json()
    assert len(resources)==8
    for resource in resources:
        response=client.get(resource['url'])
        assert response.status_code==200
        assert len(response.content)==resource['bytes']
        assert hashlib.sha256(response.content).hexdigest()==resource['sha256']
    pdf=client.get('/api/files/estudo-original.pdf')
    original=Path(__file__).resolve().parents[2]/'docs/references/Datavoxen_Relatorio_Encerrado_2026.pdf'
    assert pdf.content==original.read_bytes()
    assert pdf.headers['content-disposition'].startswith('inline')
    assert client.get('/api/files/unknown.env').status_code==404


def test_custom_parameters_never_modify_archive(client):
    import hashlib
    from app.archive import DATABASE
    before=hashlib.sha256(DATABASE.read_bytes()).hexdigest()
    original=client.get('/api/reference').json()
    params=original['parameters'];params['cac']=12
    custom=client.post('/api/simulations/preview',json={'overrides':params})
    assert custom.status_code==200
    assert custom.json()['summary']['flow']==-1304759.47
    assert client.get('/api/reference').json()['summary']['flow']==-1160759.47
    assert hashlib.sha256(DATABASE.read_bytes()).hexdigest()==before


def test_missing_archive_is_explicit(client,tmp_path,monkeypatch):
    from app import archive
    monkeypatch.setattr(archive,'DATABASE',tmp_path/'missing.sqlite3')
    assert client.get('/api/reference').status_code==503

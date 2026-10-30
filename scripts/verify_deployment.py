"""Confere uma API publicada contra o snapshot local, sem persistir simulações."""
import argparse
import csv
import hashlib
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app import archive
from app.simulation.engine import STRATEGIES, SCENARIOS, result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api', required=True)
    parser.add_argument('--frontend')
    parser.add_argument('--output', type=Path, default=ROOT/'docs/audit/production-evidence.json')
    args = parser.parse_args()
    api = args.api.rstrip('/')
    checks = {}

    def request(path, body=None, method=None, headers=None):
        data = json.dumps(body).encode() if body is not None else None
        req = Request(api + path, data=data, method=method, headers={'Content-Type':'application/json', **(headers or {})})
        try:
            with urlopen(req, timeout=45) as response:
                return response.status, response.read(), dict(response.headers)
        except HTTPError as error:
            return error.code, error.read(), dict(error.headers)

    def get_json(path):
        status, content, _ = request(path)
        if status != 200:
            raise RuntimeError(f'{path}: HTTP {status}')
        return json.loads(content)

    health = get_json('/api/health')
    checks['health_read_only'] = health['read_only'] is True and health['database'] == 'sqlite'
    for strategy in STRATEGIES:
        for scenario in SCENARIOS:
            observed = get_json(f'/api/reference?strategy={strategy}&scenario={scenario}')
            checks[f'reference:{strategy}/{scenario}'] = observed == archive.reference(strategy, scenario)
    for path, count in [('/api/comparison',12),('/api/products',5),('/api/strategies',3),('/api/benchmarks',14)]:
        checks[path] = len(get_json(path)) == count
    resources = get_json('/api/files')
    manifest = json.loads((archive.DATA/'manifest.json').read_text(encoding='utf-8'))
    checks['files_count'] = len(resources) == 8
    for resource in resources:
        status, content, _ = request(resource['url'])
        meta = manifest[resource['name']]
        checks['download:'+resource['name']] = status == 200 and len(content) == meta['bytes'] and hashlib.sha256(content).hexdigest() == meta['sha256']
    status, database_before, _ = request('/api/files/datavoxen.sqlite3')
    body = {'strategy':'A','scenario':'central','overrides':{'cac':12}}
    status, content, _ = request('/api/simulations/preview', body)
    checks['custom_simulation'] = status == 200 and json.loads(content) == result('A','central',{'cac':12})
    status, content, _ = request('/api/export?format=csv', body)
    rows = list(csv.DictReader(io.StringIO(content.decode('utf-8-sig')), delimiter=';')) if status == 200 else []
    expected = result('A','central',{'cac':12})
    checks['export_csv'] = len(rows) == 12 and all(float(row['flow']) == month['flow'] for row,month in zip(rows, expected['months']))
    status, content, _ = request('/api/export?format=pdf', body)
    from pypdf import PdfReader
    checks['export_pdf'] = status == 200 and content.startswith(b'%PDF') and 'Hipóteses' in ''.join(page.extract_text() for page in PdfReader(io.BytesIO(content)).pages)
    status, content, _ = request('/api/sensitivity', body)
    checks['sensitivity'] = status == 200 and bool(json.loads(content))
    status, database_after, _ = request('/api/files/datavoxen.sqlite3')
    checks['database_unchanged_after_simulation'] = status == 200 and database_before == database_after
    checks['invalid_input_422'] = request('/api/simulations/preview', {'strategy':'D'})[0] == 422
    checks['body_limit_413'] = request('/api/simulations/preview', {'name':'x'*140000})[0] == 413
    checks['unknown_download_404'] = request('/api/files/unknown.env')[0] == 404
    if args.frontend:
        origin = args.frontend.rstrip('/')
        status, _, headers = request('/api/simulations/preview', method='OPTIONS', headers={'Origin':origin,'Access-Control-Request-Method':'POST'})
        checks['cors_frontend'] = status == 200 and {k.lower():v for k,v in headers.items()}.get('access-control-allow-origin') == origin
        status, _, headers = request('/api/simulations/preview', method='OPTIONS', headers={'Origin':'https://untrusted.example','Access-Control-Request-Method':'POST'})
        checks['cors_other_origin_denied'] = 'access-control-allow-origin' not in {k.lower():v for k,v in headers.items()}
        for route in ['/', '/simulador', '/relatorios']:
            with urlopen(origin+route, timeout=45) as response:
                checks['spa:'+route] = response.status == 200 and b'<div id="root">' in response.read()
    report = {'verified_at':datetime.now(timezone.utc).isoformat(),'api':api,'frontend':args.frontend,'checks':checks,'failures':[key for key,value in checks.items() if not value]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'checks':len(checks),'failures':report['failures']},ensure_ascii=False))
    if report['failures']: raise SystemExit(1)


if __name__ == '__main__': main()

import csv
import io
import json
import os
from typing import Literal
from xml.sax.saxutils import escape
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, FileResponse
import sqlite3
from . import archive
from .limits import BodySizeLimit
from .schemas import SimulationInput, SimulationResult
from .simulation.engine import BASE, CAT, MODEL_HASH, SCENARIOS, STRATEGIES, VERSION, result, sensitivity

app = FastAPI(title='Datavoxen API',version=VERSION,description='Simulações hipotéticas do estudo Ilhas de Órion. Não são resultados observados de mercado.')
app.add_middleware(BodySizeLimit)
app.add_middleware(CORSMiddleware,allow_origins=[origin.strip() for origin in os.getenv('CORS_ORIGINS','http://127.0.0.1:5173,http://localhost:5173').split(',') if origin.strip()],allow_methods=['GET','POST'],allow_headers=['Content-Type'])


@app.exception_handler(sqlite3.Error)
def db_error(request: Request, exc: sqlite3.Error):
    return JSONResponse(status_code=503,content={'detail':'Base do estudo indisponível. Execute python scripts/build_study.py na raiz do projeto.'})


@app.exception_handler(archive.ArchiveVersionError)
def version_error(request: Request, exc: archive.ArchiveVersionError):
    return JSONResponse(status_code=503,content={'detail':'A edição da base precisa ser regenerada para esta versão do motor.'})


@app.exception_handler(RequestValidationError)
def validation_error(request: Request, exc: RequestValidationError):
    # Não ecoar corpos ou NaN/Infinity, que não são números JSON serializáveis.
    errors=[{'location':list(error['loc']),'message':error['msg'],'type':error['type']} for error in exc.errors()]
    return JSONResponse(status_code=422,content={'detail':'Confira os valores: há parâmetros inválidos.','errors':errors})


@app.get('/api/health')
def health():
    version=archive.rows('SELECT id FROM model_versions')[0]['id']
    return {'status':'ok','model_version':version,'database':'sqlite','read_only':True,'authentication_required':False}


@app.get('/api/studies')
def studies():
    return archive.rows('SELECT s.*, m.id AS model_version, m.checksum AS model_hash FROM studies s JOIN model_versions m ON m.study_id=s.id')


@app.get('/api/strategies')
def strategies():
    items=archive.rows('SELECT * FROM strategies ORDER BY id')
    for item in items:
        item['products']=[p['product_id'] for p in archive.rows('SELECT product_id FROM strategy_products WHERE strategy_id=? ORDER BY position',(item['id'],))]
    return items


@app.get('/api/products')
def products():
    return [dict(**v,candidate_prices=[round(v['price']*f,2) for f in (.85,1,1.15)]) for v in archive.rows('SELECT * FROM products ORDER BY rowid')]


@app.get('/api/scenarios')
def scenarios():
    items=archive.rows('SELECT id, parameters_json FROM scenarios ORDER BY rowid')
    assumptions=archive.rows('SELECT assumptions_json FROM model_versions WHERE id=?',(VERSION,))[0]
    return {'scenarios':{v['id']:json.loads(v['parameters_json']) for v in items},'assumptions':json.loads(assumptions['assumptions_json'])}


@app.get('/api/benchmarks')
def benchmarks():
    return archive.rows('SELECT b.game,b.product,b.offer_type,b.price,b.currency,b.channel,b.consulted_at,s.url AS source_url,b.verification_status,b.limitations FROM benchmarks b JOIN sources s ON s.id=b.source_id ORDER BY b.id')


@app.get('/api/reference',response_model=SimulationResult)
def reference(strategy:Literal['A','B','C']='A',scenario:Literal['central','conservador','otimista','estresse']='central'):
    return archive.reference(strategy,scenario)


FILES = {
    'estudo-original.pdf': ('Estudo original em PDF','Documento que fundamenta a análise. Arquivo original preservado.'),
    'datavoxen.sqlite3': ('Base SQLite do estudo','Premissas, catálogo, cenários e resultados oficiais para consulta SQL.'),
    'modelo-original.zip': ('Modelo e auditoria originais','ZIP fornecido com o motor Python e os testes do estudo.'),
    'premissas.json': ('Premissas originais','Parâmetros econômicos sintéticos do modelo original.'),
    'projecao-original.csv': ('Projeções mensais originais','144 linhas financeiras: três estratégias, quatro cenários e 12 meses.'),
    'coortes-originais.csv': ('Coortes originais','36 coortes do cenário central, conforme o ZIP original.'),
    'sensibilidade-original.csv': ('Sensibilidade original','45 configurações de preço e sensibilidade do modelo original.'),
    'comparacao-cenarios.csv': ('Comparação dos 12 cenários','Resultados oficiais com o mesmo arredondamento da aplicação.'),
}


@app.get('/api/files')
def files():
    try:
        manifest=json.loads((archive.DATA/'manifest.json').read_text(encoding='utf-8'))
        return [dict(name=name,title=title,description=description,url='/api/files/'+name,**manifest[name]) for name,(title,description) in FILES.items()]
    except (OSError,ValueError,KeyError,TypeError):
        raise HTTPException(503,'Manifesto dos arquivos do estudo indisponível.')


@app.get('/api/files/{name}')
def file(name:str):
    if name not in FILES: raise HTTPException(404,'Arquivo não encontrado.')
    path=archive.DATA/name
    if not path.is_file(): raise HTTPException(503,'Arquivo do estudo indisponível.')
    media={'pdf':'application/pdf','sqlite3':'application/vnd.sqlite3','json':'application/json','csv':'text/csv','zip':'application/zip'}[name.rsplit('.',1)[1]]
    return FileResponse(path,media_type=media,filename=name,content_disposition_type='inline' if name.endswith('.pdf') else 'attachment')


@app.post('/api/simulations/preview',response_model=SimulationResult)
def preview(body: SimulationInput):
    overrides=body.overrides.model_dump(exclude_none=True)
    return result(body.strategy,body.scenario,overrides) if overrides else archive.reference(body.strategy,body.scenario)


@app.get('/api/comparison')
def comparison():
    return [dict(strategy=r['strategy'],scenario=r['scenario'],**json.loads(r['summary_json'])) for r in archive.rows('SELECT strategy,scenario,summary_json FROM reference_runs ORDER BY rowid')]


@app.post('/api/sensitivity')
def preview_sensitivity(body: SimulationInput):
    r = preview(body)
    return sensitivity(body.strategy,body.scenario,r['parameters'])


def export_result(r,format,dataset):
    rows=r[dataset] if dataset!='comparison' else comparison()
    if format=='csv':
        stream=io.StringIO(newline='')
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),delimiter=';'); writer.writeheader(); writer.writerows(rows)
        return Response('\ufeff'+stream.getvalue(),media_type='text/csv; charset=utf-8',headers={'Content-Disposition':f'attachment; filename="datavoxen-{dataset}.csv"'})
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    stream=io.BytesIO(); styles=getSampleStyleSheet()
    story=[Paragraph('DATAVOXEN | Relatório de simulação',styles['Title']),Paragraph(f"Estratégia {r['strategy']} · Cenário {r['scenario']} · Modelo {VERSION}",styles['Normal']),Spacer(1,12),Paragraph('Estudo fictício. Hipóteses não calibradas com dados de jogadores reais. Consistência matemática não comprova validade empírica.',styles['Normal']),Spacer(1,12)]
    table=[['Mês','Receita bruta','Após deduções','Custos','Resultado','Caixa']]
    for x in r['months']:
        table.append([str(x['month'])]+[f'{x[k]:,.2f}'.replace(',','_').replace('.',',').replace('_','.') for k in ['gross','net','costs','flow','cash']])
    t=Table(table,repeatRows=1,colWidths=[30,90,90,90,90,90]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee')),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    def currency(v): return 'R$ '+f'{v:,.2f}'.replace(',','_').replace('.',',').replace('_','.')
    labels={'cac':'CAC por adquirido','acq':'Novos jogadores por mês','eng':'Multiplicador de atratividade','spend':'Multiplicador de gasto','opex':'Multiplicador operacional','price_mult':'Fator de preço por produto','elasticity':'Sensibilidade de escolha','activity':'Atividade mensal por idade (M0 a M11)','capital':'Capital inicial','reserve':'Reserva protegida','fee':'Tarifa da plataforma','tax':'Tributos','refund':'Reembolsos','operations':'Operação mensal','production':'Produção inicial','content':'Conteúdo por atualização','unit_cost':'Custo variável por unidade','attractiveness':'Atratividade assumida por produto'}
    story += [t,Spacer(1,16),Paragraph(f"Resultado acumulado: {currency(r['summary']['flow'])} | Receita bruta: {currency(r['summary']['gross'])}",styles['Normal']),Spacer(1,16),Paragraph('O resultado não inclui capital como receita. A reserva protegida não é despesa. O fluxo assume recebimentos no mesmo mês das vendas. Valores fracionários de compradores e unidades são expectativas do modelo.',styles['Normal']),PageBreak(),Paragraph('Hipóteses completas da execução',styles['Heading2'])]
    for k,v in r['parameters'].items():
        if isinstance(v,dict):
            value='; '.join(f"{CAT[key]['name']}: "+(currency(item) if k=='unit_cost' else f'{item*100:.2f}%' if k=='attractiveness' else f'{item:.2f}x') for key,item in v.items())
        elif isinstance(v,list): value='; '.join(f'M{i}: {item*100:.1f}%' for i,item in enumerate(v))
        elif k in ('cac','capital','reserve','operations','production','content'): value=currency(v)
        elif k in ('fee','tax','refund'): value=f'{v*100:.2f}%'
        else: value=str(v)
        story += [Paragraph(escape(f'{labels.get(k,k)}: {value}'),styles['Normal']),Spacer(1,8)]
    story += [Spacer(1,12),Paragraph(f"Identificador das premissas: {r['model_hash']}",styles['Normal']),Paragraph('Fonte: motor original e premissas do estudo fornecido pela proprietária. Valores em reais. Arredondamento HALF_UP somente na saída; totais calculados antes do arredondamento mensal.',styles['Normal'])]
    SimpleDocTemplate(stream,pagesize=(650,842),rightMargin=40,leftMargin=40).build(story)
    return Response(stream.getvalue(),media_type='application/pdf',headers={'Content-Disposition':'attachment; filename="datavoxen-relatorio.pdf"'})


@app.post('/api/export')
def export_preview(body:SimulationInput,format:Literal['csv','pdf']='csv',dataset:Literal['months','cohorts','products','comparison']='months'):
    return export_result(preview(body),format,dataset)

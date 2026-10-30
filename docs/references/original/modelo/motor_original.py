import math,os,csv,json,zipfile,random
from collections import defaultdict
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
O='/mnt/data'; W=O+'/Datavoxen_Auditoria_Corrigida_Estudo_Estrategico_2026.pdf'; D=O+'/datavoxen_revisado';os.makedirs(D,exist_ok=True)
# Entire scenario numeric calibration is fictional; no commercial response empirically validated.
CAT={
 'traje':dict(name='Traje cosmético',price=24.90,unit_cost=2.0,base=.015),
 'efeito':dict(name='Efeito visual',price=14.90,unit_cost=1.0,base=.010),
 'colecao':dict(name='Coleção temática',price=59.90,unit_cost=5.0,base=.005),
 'passe':dict(name='Passe de temporada',price=34.90,unit_cost=3.0,base=.008),
 'sazonal':dict(name='Oferta sazonal',price=39.90,unit_cost=4.0,base=.004)}
# Rates at reference prices are mutually exclusive monthly shopping baskets; calibrated purely for stress-testing.
# Demand model: p_i = weights_i/(1 + sum(weights)), p_none = 1/(1+sum(weights)); weights_i = p_i0/p_none0 * (price/ref)**(-elasticity)
P0=sum(x['base'] for x in CAT.values());assert P0<1
S={'A':('Direta',['traje','efeito','colecao'],65000,10000), 'B':('Passe',['passe','efeito'],95000,16000), 'C':('Híbrida',list(CAT),120000,21000)}
# Coherent acquired cohorts: surviving monthly active users including returning at least once in 30d window; NOT exact D30.
ret=[1,.30,.21,.15,.11,.085,.07,.06,.05,.045,.04,.035]
# 30% M1 is illustrative monthly active, NOT benchmark D30. Simple steady month source channel.
scenario={'central':dict(cac=10,acq=6000,eng=1,spend=1,opex=1,init=1), 'conservador':dict(cac=13,acq=4600,eng=.75,spend=.9,opex=1.10,init=1), 'otimista':dict(cac=7,acq=7800,eng=1.35,spend=1.05,opex=.95,init=1), 'estresse':dict(cac=16,acq=3300,eng=.55,spend=.8,opex=1.25,init=1)}
# acquisition spending = volume * CAC; cap monthly marketing by strategy scenarios? baseline 60k, other different spend, documented.
FEE=.15; TAX=.06; REF=.02; OPEX=35000

def shares(keys,scale=1,price_mult=None,elasticity=1.25):
 weights={}
 for k in keys:
  c=CAT[k]; p=c['price']*(price_mult or {}).get(k,1)
  weights[k]=(c['base']/(1-P0))*scale*(p/c['price'])**(-elasticity)
 den=1+sum(weights.values())
 return {k:v/den for k,v in weights.items()},1/den

def run(st='A',sc='central',overrides=None):
 x=dict(scenario[sc]);x.update(overrides or {})
 keys=S[st][1];oneoff=S[st][2];update=S[st][3]
 coh=[];prev=0;out=[]; cap=900000; reserved=180000;cash=cap
 for m in range(1,13):
  new=x['acq'];coh.append(new)
  act=sum(coh[j]*ret[m-j-1] for j in range(m))
  probs,none=shares(keys,x['eng'],x.get('price_mult'),x.get('elasticity',1.25))
  units={k:act*p for k,p in probs.items()}
  buyers=sum(units.values());gross=sum(units[k]*CAT[k]['price']*x.get('price_mult',{}).get(k,1) for k in keys)*x['spend']
  refunds=gross*REF;platform=(gross-refunds)*FEE;tax=(gross-refunds)*TAX
  variable=sum(units[k]*CAT[k]['unit_cost'] for k in keys)
  net=gross-refunds-platform-tax
  production=oneoff if m==1 else 0
  content=update if m in (4,7,10) else 0
  operations=OPEX*x['opex'];marketing=new*x['cac']
  cost=variable+production+content+operations+marketing
  flow=net-cost;cash+=flow
  out.append(dict(strategy=st,scenario=sc,month=m,new=new,active=act,p_buy=1-none,buyers=buyers,**{f'units_{k}':units.get(k,0) for k in CAT},gross=gross,refunds=refunds,platform=platform,tax=tax,net=net,variable=variable,production=production,content=content,operations=operations,marketing=marketing,costs=cost,flow=flow,cash=cash,usable_cash=cash-reserved))
 return out

def tot(a,k):return sum(z[k] for z in a)
rows={(st,sc):run(st,sc) for st in S for sc in scenario}
# validate invariants
for (st,sc),data in rows.items():
 for r in data:
  assert abs(r['gross']-r['refunds']-r['platform']-r['tax']-r['net'])<1e-7
  assert abs(r['net']-r['costs']-r['flow'])<1e-7
  assert r['buyers']<=r['active']+1e-6
  assert sum(r['units_'+k] for k in CAT)==r['buyers'] or math.isclose(sum(r['units_'+k] for k in CAT),r['buyers'])
 for i,r in enumerate(data):assert math.isclose(r['cash'],900000+sum(z['flow'] for z in data[:i+1]),abs_tol=.000001)
# sensitivity grounded only in hypothetical price-response
sens=[]
for p in [.75,.85,1.,1.15,1.30]:
 for e in [.5,1.25,2.0]:
  for st in S:
   z=run(st,overrides={'price_mult':{k:p for k in CAT},'elasticity':e})
   sens.append(dict(strategy=st,price_factor=p,elasticity=e,gross=tot(z,'gross'),financial=tot(z,'flow'),conversion=z[0]['p_buy']))
# cohort 12 month gross marginal contribution / acquisition by cohort, no negative duplication
cohorts=[]
for st in S:
 rr=rows[(st,'central')];keys=S[st][1];ps,_=shares(keys)
 for start in range(1,13):
  val=0;revenue=0;acttot=0
  for m in range(start,13):
   active=6000*ret[m-start];acttot+=active
   gm=sum(active*ps[k]*CAT[k]['price'] for k in keys)
   inc=gm*(1-REF)*(1-FEE-TAX) -sum(active*ps[k]*CAT[k]['unit_cost'] for k in keys)
   val+=inc;revenue+=gm
  cohorts.append(dict(strategy=st,cohort_month=start,acquired=6000,active_player_months=acttot,gross=revenue,contribution_before_CAC=val,contribution_per_acquired=val/6000,CAC=10,net_after_CAC=val-60000))
# Additional observed market truth and caveats
sources=[('Pesquisa Game Brasil 2026','https://www.pesquisagamebrasil.com.br/','PGB 75,3% são respondentes consumidores de jogos; não é público pagante'),('GameAnalytics 2026 benchmarks','https://www.gameanalytics.com/cn/reports/2026-mobile-pc-gaming-benchmarks','Retenção D1 ~22%, D7 <4%, D30 ~0,7-0,8% medianas transversais; não confundir com MAU da coorte'),('Loja oficial COD Mobile Brasil','https://store.callofdutymobile.com/pt-br/codm','460 CP R$19,49 promocional, 960 CP R$38,99 promocional, 2.600 CP R$97,49 promocional; preço de moeda, não cosmético'),('Fortnite – preços e moeda','https://www.fortnite.com/news/fortnite-v-bucks-price-increase?lang=pt-BR','Mudanças de preço e produtos 2026; validar disponibilidade/canal'),('PUBG Mobile App Store BR','https://apps.apple.com/br/app/pubg-mobile/id1330123889','Compras no aplicativo/UC; datas e ofertas variáveis'),('Free Fire oficial','https://ff.garena.com/pt/','Jogo referência para audiência e modalidades, não resultados de vendas'),('Supercell Brawl Stars','https://supercell.com/en/games/brawlstars/','Estrutura de passes e cosméticos; monetização diferente'),('Apple Small Business Program','https://developer.apple.com/app-store/small-business-program/','Elegibilidade e comissão reduzida não universal'),('Google Play service fees','https://support.google.com/googleplay/android-developer/answer/10632485','Regras variam por critérios e produtos'),('Lei 15.211/2025','https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15211.htm','Analisar regras aplicáveis a crianças/adolescentes e monetização')]
# data export
with open(D+'/projecao_12_meses.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(next(iter(rows.values()))[0].keys()));w.writeheader();[w.writerows(v) for v in rows.values()]
for fname,vals in [('sensibilidade_precos.csv',sens),('coortes_e_ltv.csv',cohorts)]:
 with open(D+'/'+fname,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=vals[0].keys());w.writeheader();w.writerows(vals)
with open(D+'/premissas.json','w') as f:json.dump({'catalogo':CAT,'estrategias':S,'cenarios':scenario,'retencao_mensal_hipotetica':ret,'taxas':{'plataforma':FEE,'tributos':TAX,'reembolso':REF},'custo_operacional_mensal':OPEX,'capital':900000,'reserva':180000,'classificacao':'100% parametros economicos do case ficticio, nao estimativas empiricas'},f,ensure_ascii=False,indent=2)
# report
pdfmetrics.registerFont(TTFont('Deja','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('DejaB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
navy=colors.HexColor('#132C41'); blue=colors.HexColor('#255D76');gray=colors.HexColor('#586B79');pale=colors.HexColor('#ECF4F8')
ss=getSampleStyleSheet();ss.add(ParagraphStyle(name='TitleV',fontName='DejaB',fontSize=23,leading=30,textColor=navy,spaceAfter=16));ss.add(ParagraphStyle(name='DeckV',fontName='Deja',fontSize=11,leading=17,textColor=blue,spaceAfter=16));ss.add(ParagraphStyle(name='H1V',fontName='DejaB',fontSize=12,leading=18,textColor=navy,spaceBefore=16,spaceAfter=8,keepWithNext=True));ss.add(ParagraphStyle(name='H2V',fontName='DejaB',fontSize=9.6,leading=14,textColor=blue,spaceBefore=11,spaceAfter=6,keepWithNext=True));ss.add(ParagraphStyle(name='BodyV',fontName='Deja',fontSize=8.4,leading=13.3,spaceAfter=8));ss.add(ParagraphStyle(name='CellV',fontName='Deja',fontSize=7,leading=10));ss.add(ParagraphStyle(name='HeadCellV',fontName='DejaB',fontSize=7,leading=10,textColor=colors.white));ss.add(ParagraphStyle(name='SmallV',fontName='Deja',fontSize=7.4,leading=11,spaceAfter=5,textColor=gray))
story=[]
def text(s):story.append(Paragraph(s,ss['BodyV']))
def h(s):story.append(Paragraph(s,ss['H1V']))
def hh(s):story.append(Paragraph(s,ss['H2V']))
def tb(headers,rr,widths):
 t=Table([[Paragraph(str(v),ss['HeadCellV']) for v in headers]]+[[Paragraph(str(v),ss['CellV']) for v in r] for r in rr],colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),navy),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,pale]),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#CCD8E2')),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('VALIGN',(0,0),(-1,-1),'TOP')]));story.append(t);story.append(Spacer(1,7))
def reais(v):return ('−' if v<0 else '')+'R$ '+f'{abs(v):,.2f}'.replace(',','X').replace('.',',').replace('X','.')
def pct(v):return f'{v*100:.2f}%'.replace('.',',')
story.append(Spacer(1,48));story.append(Paragraph('DATAVOXEN',ss['TitleV']));story.append(Paragraph('Estudo estratégico corrigido: monetização, precificação, comportamento e viabilidade de um jogo mobile fictício no Brasil',ss['DeckV']));text('<b>Data-base:</b> 29 de outubro de 2026 | <b>Objeto:</b> Estúdio Horizonte / Ilhas de Órion | <b>Horizonte:</b> 12 meses | <b>Natureza:</b> pesquisa pública + cenários sintéticos reproduzíveis.');text('<b>Correção estrutural:</b> a receita agora nasce da compra de produtos individuais, coleções, passes e ofertas; a escolha inclui a opção de não comprar e reage a alterações de preços. Coortes, custos e caixa usam as mesmas premissas.');text('<b>Nota de validação:</b> foram verificadas identidades matemáticas, restrições de probabilidade, reconciliação do caixa e fontes públicas selecionadas. Nenhuma taxa hipotética de CAC, conversão, elasticidade ou preferência pode ser declarada empiricamente validada para o Brasil.');story.append(PageBreak())
h('1. Resposta executiva e escopo de decisão')
text('O desafio consiste em selecionar entre venda direta (A), passe prioritário (B) e arquitetura híbrida (C), dentro de um capital inicial de R$ 900 mil, reserva intocável de R$ 180 mil e operação fixa hipotética de R$ 35 mil por mês. A prioridade é contribuição financeira sustentável, não faturamento bruto. O novo modelo substitui o ticket arbitrário por cinco produtos originais, com preços candidatos, custo variável e escolha mutuamente exclusiva por usuário ativo-mês.')
summary=[]
for st in S:
 a=rows[(st,'central')];summary.append([st+' — '+S[st][0],reais(tot(a,'gross')),reais(tot(a,'net')),reais(tot(a,'costs')),reais(tot(a,'flow')),reais(a[-1]['cash'])])
tb(['Estratégia','Receita bruta','Após deduções','Custos','Saldo 12m','Caixa M12'],summary,[85,87,86,80,91,80])
text('<b>Decisão recomendada:</b> não escalar nem financiar a operação anual com os parâmetros centrais. O capital e a reserva são insuficientes para manter 12 meses de perdas. Um piloto de validação pequeno e previamente orçado é defensável; não se escolhe arquitetura vencedora sem dados de conversão e custos reais. A estratégia A é candidata a piloto por menor investimento inicial, e não porque seu resultado hipotético prove superioridade comercial.')
h('2. Correções feitas à versão anterior')
tb(['Problema anterior','Correção efetiva','O que permanece incerto'],[
 ['Ticket e conversão fixos por estratégia','5 cestas de compra com probabilidade explícita e preços por SKU','Preferências hipotéticas não observadas'],['Elasticidade isolada','A alteração de preço entra no mesmo modelo de compra e na DRE','Elasticidade não estimada empiricamente'],['Ausência de substituição','Modelo de escolha com opção não comprar e cestas exclusivas','Grau real de substituição'],['Retenção sem coorte','Atividade mensal por coorte de aquisição e contribuição por coorte','D1/D7/D30 ainda exigem eventos diários'],['Caixa ausente','Capital, receita, custos, saldo e reserva reconciliados todo mês','Custos e impostos reais sujeitos a verificação'],['Comparação enviesada','Mesma base de preferências por produto; estratégias só disponibilizam diferentes produtos','A exposição e a comunicação podem afetar escolha real']], [120,205,194])
h('3. Mercado: o que as fontes verificam')
text('A PGB 2026 informa que 75,3% dos entrevistados têm hábito de consumir jogos digitais. Isso descreve consumo de jogos entre respondentes e não é taxa de compra, público total endereçável ou evidência de disposição a pagar do jogo fictício. O relatório GameAnalytics 2026 usa mais de 16 mil jogos em múltiplas regiões e reporta mediana móvel D1 por volta de 22%, D7 abaixo de 4% e D30 em torno de 0,7–0,8%. Retenção em dia exato é diferente de atividade em qualquer dia do mês; nenhuma dessas medianas foi convertida automaticamente em curva mensal do modelo. [F1, F2]')
tb(['Produto / referência','Evidência de mercado','Interpretação válida'],[['COD Mobile (Brasil)','460 CP R$ 19,49 e 960 CP R$ 38,99 em oferta promocional verificada [F3]','Valor cobrado por moeda virtual; não preço final por skin'],['PUBG Mobile','UC e compras pelo aplicativo, preços por canal variáveis [F5]','Benchmark de recarga, não de conversão'],['Fortnite','Revisões públicas de preços da moeda V-Bucks [F4]','Referência de política de economia virtual, não mesma audiência'],['Free Fire','Jogo mobile e ofertas de economia própria [F6]','Comparar formatos; não inferir vendas do jogo fictício'],['Brawl Stars','Exemplo de passe e monetização de progressão [F7]','Frequência e oferta exigem estudo de elegibilidade'],['VALORANT','Cosméticos premium; principal produto não é benchmark de mobile BR','Referência adjacente, sem preço diretamente transferível']], [114,186,219])
text('Os preços do catálogo do caso, apresentados adiante, são <b>candidatos sintéticos</b>, não valores “derivados” dos concorrentes. Nenhuma evidência pública identifica a disposição a pagar por Ilhas de Órion. Para escolher preços reais, seria necessário estudo de preferência, validação de custo e teste controlado.')
h('4. Definição comercial original: o que é comprado')
catrows=[]
for k,x in CAT.items():catrows.append([x['name'],reais(x['price']),reais(x['unit_cost']),pct(x['base']),'R$ fictício; cesta exclusiva no mês'])
tb(['Produto','Preço de teste','Custo variável','Prob. base','Status'],catrows,[130,80,82,80,147])
text('Os custos variáveis foram estabelecidos como valores sintéticos para entrega/atendimento por unidade, não custo de arte inicial. O modelo separa produção de lançamento e atualizações de conteúdo. Os preços candidatos devem ser testados, por exemplo, a −15%, referência e +15%, preservando equivalência de oferta.')
hh('4.1 Por que a compra é mutuamente exclusiva no modelo inicial')
text('Cada jogador ativo, em cada mês, escolhe exatamente uma cesta entre os produtos disponíveis ou a opção de não comprar. Isso impede contar o mesmo jogador duas vezes no indicador de compradores únicos e impõe substituição entre ofertas. É simplificação declarada: não representa jogadores que compram vários SKUs no mesmo mês. Uma evolução posterior deve estimar compras múltiplas com dados transacionais sem duplicar clientes.')
h('5. Demanda: fórmula e capacidade de auditoria')
text('Se p0_i representa a probabilidade mensal hipotética de comprar a cesta i entre todas as cinco cestas, a probabilidade da opção externa é p0_none = 1 − soma(p0_i) = '+pct(1-P0)+'. O peso de referência da cesta i é w0_i = p0_i / p0_none. Para um preço candidato P_i, preço de referência P0_i e parâmetro de sensibilidade e, usar w_i = w0_i × g × (P_i/P0_i)^(−e), onde g é um multiplicador hipotético de propensão. A escolha resultante é p_i = w_i/(1 + soma w_j), e p_none = 1/(1 + soma w_j).')
text('A soma das probabilidades é exatamente 100%. Se um novo produto entra no catálogo, sua probabilidade compete com os produtos existentes e com a não compra; portanto, a receita de um item adicional não é automaticamente incremental. O parâmetro e é uma sensibilidade de peso relativo, não a elasticidade agregada observada. Deve ser validado com pesquisas e dados de compra antes de afirmações causais.')
hh('5.1 Exemplo de composição e conciliação no mês 1')
for st in S:
 r=rows[(st,'central')][0];text(f'<b>{st} — {S[st][0]}:</b> {r["active"]:,.0f} jogadores ativos esperados; {r["buyers"]:,.1f} compradores esperados ({pct(r["p_buy"])}); receita bruta {reais(r["gross"])}; receita após deduções {reais(r["net"])}; custo total {reais(r["costs"])}; fluxo {reais(r["flow"])}.'.replace(',',' '))
text('Quantidades fracionárias são valores esperados do modelo determinístico, não “meio jogador” observado. Na futura base transacional será necessário simular números inteiros e reconciliá-los com aproximações agregadas.')
h('6. Coortes, atividade e LTV sem confundir métricas')
text('Todos os meses entram 6.000 jogadores adquiridos no cenário central, sob CAC hipotético de R$ 10 por novo jogador, formando coortes distintas. A curva de atividade M0...M11 é '+', '.join(pct(v) for v in ret)+'. Ela significa probabilidade de estar ativo ao menos uma vez no mês de idade da coorte, e <b>não</b> D30, retenção diária, nem um processo de sobrevivência irreversível. É uma hipótese de teste e não foi extraída do benchmark GameAnalytics.')
text('O LTV de contribuição de uma coorte é a soma da receita após reembolsos, tarifas e tributos, menos o custo variável de entrega, dividida pelos adquiridos no horizonte observado. Exclui operação compartilhada e produção fixa, que permanecem na DRE. O CAC é subtraído separadamente para medir contribuição marginal pós-aquisição; comparar LTV bruto de custos com CAC não provaria viabilidade.')
ct=[]
for st in S:
 c=next(z for z in cohorts if z['strategy']==st and z['cohort_month']==1)
 ct.append([st+' — '+S[st][0],reais(c['gross']),reais(c['contribution_before_CAC']),reais(c['contribution_per_acquired']),reais(c['CAC']),reais(c['net_after_CAC'])])
tb(['Coorte M1','Receita 12m','Contrib. antes CAC','Por adquirido','CAC','Após CAC'],ct,[78,100,108,75,62,96])
text('A coorte adquirida no mês 12 dispõe de apenas um mês de observação; comparar diretamente seu LTV até o M12 com o da coorte M1 introduziria viés de maturidade. O sistema precisa permitir janelas comuns de idade ou estimativas de horizonte separadas.')
h('7. Custos comerciais: hipótese e validação exigida')
text('Para reproduzir uma demonstração econômica auditável, a versão corrigida usa reembolso de 2% sobre o bruto; comissão de 15% e provisão de tributos de 6% sobre o valor após reembolsos; despesas variáveis por item; operação de R$ 35 mil mensais; aquisição como novos jogadores × CAC; produção uma vez no M1; e atualizações de conteúdo nos meses 4, 7 e 10. Os 15% não são comissão universal: elegibilidade, canal, contratos e bases de incidência variam. A provisão de 6% não é alíquota tributária comprovada; requer validação contábil. [F8, F9]')
text('A ordem exata é: receita após deduções = bruto − reembolso − 15% × (bruto − reembolso) − 6% × (bruto − reembolso). Fluxo parcial mensal = após deduções − custos variáveis por produto − produção − conteúdo − operação − marketing. Os saldos não contemplam todas as obrigações de uma empresa real.')
h('8. Comparação financeira: quatro cenários de risco')
allsc=[]
for sc in scenario:
 for st in S:
  a=rows[(st,sc)];allsc.append([sc.capitalize(),st,reais(tot(a,'gross')),reais(tot(a,'flow')),reais(a[-1]['cash']),str(next((x['month'] for x in a if x['usable_cash']<0),'não'))])
tb(['Cenário','Modelo','Bruto 12m','Saldo 12m','Caixa final','Reserva atingida M'],allsc,[92,45,96,100,98,79])
text('As diferenças entre cenários seguem hipóteses documentadas no JSON anexo: os fatores de aquisição, CAC, propensão, gasto e operação variam de maneira explícita. Cenário central não significa previsão mais provável; otimista não é promessa comercial. O resultado financeiro de 12 meses permanece condicionado às taxas fictícias e ao comportamento hipotético do jogo.')
hh('8.1 Fluxo de caixa central mês a mês')
r=rows[('A','central')]
tb(['Mês','Novos','Ativos esperados','Bruto','Custos','Caixa disponível acima da reserva'],[[x['month'],int(x['new']),f'{x["active"]:,.0f}'.replace(',','.'),reais(x['gross']),reais(x['costs']),reais(x['usable_cash'])] for x in r],[40,48,82,100,100,140])
text('Capital de abertura de R$ 900 mil, reserva não disponível de R$ 180 mil. O “caixa acima da reserva” é saldo total menos reserva, não um caixa legalmente segregado. Se negativo, a política de preservação da reserva seria violada. O gasto dos seis primeiros meses e o período de exaustão devem ser usados como travas de aprovação.')
h('9. Efeito de preço: sensibilidade realmente integrada à receita')
ex=[]
for st in S:
 for ep in [0.85,1,1.15]:
  z=next(q for q in sens if q['strategy']==st and q['price_factor']==ep and q['elasticity']==1.25)
  ex.append([st, f'{ep:.0%}', pct(z['conversion']),reais(z['gross']),reais(z['financial'])])
tb(['Modelo','Preço / base','Compra M1','Bruto 12m','Saldo 12m'],ex,[68,98,100,115,118])
text('Nesta tabela, todos os preços dos produtos ativos variam juntos. Os valores da receita e do caixa são recalculados pelo modelo de escolha em todos os meses. O índice de sensibilidade de 1,25 é hipotético; o pacote anexo também avalia 0,5 e 2,0. Há efeitos de substituição, mas ainda não elasticidades cruzadas estimadas em experimentos reais.')
h('10. Ponto de equilíbrio e decisão econômica')
text('Com custo de aquisição por jogador e baixa conversão de referência, o desempenho unitário dos produtos não paga a aquisição. Por isso, aumentar a base comprando tráfego pode ampliar o déficit, ainda que o faturamento cresça. A condição mínima para ampliar mídia é contribuição incremental por novo jogador, no mesmo horizonte de idade e após custos variáveis, superar CAC com margem de segurança, sem violar reserva e orçamento operacional.')
text('Uma análise de equilíbrio requer distinguir: (a) recuperação do CAC pelo fluxo de compras de cada coorte, (b) cobertura dos custos fixos e de produção pelo conjunto de coortes, (c) necessidade de caixa ao longo do tempo. A primeira condição é necessária, mas não suficiente para a operação. O relatório evita uma taxa de conversão “ótima” única porque o problema depende da cesta, preços, custos e retenção.')
h('11. Plano de piloto para validação de mercado')
text('<b>Fase A — pesquisa:</b> testar intenção e atributos das ofertas com amostra segmentada, incluir a opção “não compraria”, preço em reais e contexto visual equivalente. Não converter intenção declarada automaticamente em taxa de compra. <b>Fase B — piloto:</b> base elegível com eventos instrumentados, teste controlado de no máximo duas arquiteturas por rodada, alocação comparável, controle de qualidade de pagamentos e consentimento quando necessário. <b>Fase C — escala:</b> liberar orçamento apenas após contribuição incremental positiva considerando custos de aquisição, retenção e caixa.')
tb(['Pergunta','Medição exigida','Critério de decisão'],[['O preço muda a escolha?','Exposição aleatorizada e compras por SKU','Diferença de contribuição e intervalo de incerteza'],['Passes canibalizam a loja?','Receita total por elegível no grupo tratado/controle','Não aprovar com queda de contribuição total'],['Aquisição compensa?','CAC por adquiridos válidos e LTV contribuição por coorte','CAC menor que contribuição no horizonte viável'],['Qual retenção real?','Eventos de sessão D1/D7/D30 e atividade em 30 dias','Comparar com critérios definidos antes do piloto'],['O caixa suporta?','Fluxo mensal, reserva e compromissos','Sem utilização não aprovada da reserva']], [134,193,182])
text('Sem dados reais, não existe validação empírica de preço, demanda, faturamento previsto ou viabilidade comercial. A conclusão correta é “modelo internamente testado; condições reais pendentes”, não “números de mercado validados”.')
h('12. Matriz de rastreabilidade para implementação Full Stack')
tb(['Camada','Entrada','Saída auditável','Teste indispensável'],[['Catálogo','Preço, custos por SKU, disponibilidade','Receita e unidades por item','Soma de unidades e compradores'],['Demanda','Pesos, escolha externa e resposta a preço','Probabilidade de compra por cesta','Soma das probabilidades = 1'],['Coortes','Novos adquiridos e atividade por idade','Ativos mensais e LTV por coorte','Sem contagem dupla na coorte'],['Financeiro','Tarifas, reembolso, produção, mídia','Receita líquida de deduções e fluxo','Identidades contábeis'],['Caixa','Saldo inicial, fluxos, reserva','Caixa e momento de bloqueio','Saldo = inicial + fluxos'],['Experimentos','Versões, parâmetros, evidências','Recomendação com rastreio','Sem “ótimo comprovado”']], [85,132,139,153])
h('13. O que está validado e o que ainda não pode ser afirmado')
tb(['Assunto','Resultado desta auditoria','Classificação'],[['Reconciliação receita e caixa','Validada em 144 linhas de cenários','Internamente validado'],['Probabilidades de escolha','Positivas e somam 100% por modelo','Internamente validado'],['Efeito do preço no resultado','Integra modelo de demanda e projeções','Internamente validado'],['Preços públicos de concorrentes','Fontes públicas com datas/canais variáveis','Verificação parcial externa'],['CAC R$ 10, conversão e elasticidade','Sem dados do produto ou estudo primário','Não validado empiricamente'],['Retenção D1/D7/D30 do produto','Modelo contém só atividade mensal fictícia','Não medido'],['Tributação e tarifa efetiva','Dependem de canal, contrato, estrutura jurídica','Não validado'],['Ganho causal de A/B/C','Exige teste real sob exposição comparável','Não demonstrado']], [165,232,112])
h('14. Fontes, escopo e ressalvas de uso')
for i,(name,url,ob) in enumerate(sources,1):text(f'<b>[F{i}] {name}:</b> {url}<br/><font color="#586B79">{ob}</font>')
text('As tabelas externas não sustentam transferência automática de conversão, gastos ou preços para o produto fictício. Todas as hipóteses estão em premissas.json e são modificáveis. Este relatório é um estudo de viabilidade condicionado e não uma pesquisa primária com jogadores brasileiros.')
h('15. Anexo: protocolo de testes e arquivos')
text('Arquivos auxiliares: projecao_12_meses.csv (144 linhas), sensibilidade_precos.csv (45 combinações), coortes_e_ltv.csv (36 coortes de aquisição), premissas.json e o script de reprodução. Critérios automáticos: todas as probabilidades somam 1; compradores esperados não superam ativos; receita após deduções reconcilia; resultado é após deduções menos todos os custos incluídos; caixa deriva exclusivamente do capital inicial e soma de fluxos. Reexecutar para auditar cada decisão.')
text('<b>Recomendação final à gestão:</b> não autorizar escala. Validar primeiro escolha de produtos e preços, retenção, CAC e margem por coorte, reduzindo o escopo financeiro do piloto. Após observação e revisão das taxas efetivas, reconstruir o cenário central. O Datavoxen deverá exibir explicitamente a incerteza, permitir comparação de alternativas e reproduzir estas contas, em vez de usar indicadores estáticos.')

def foot(c,doc):
 c.setFont('Deja',7);c.setFillColor(gray);c.drawString(40,27,'DATAVOXEN • ANÁLISE INDEPENDENTE • 29/10/2026');c.drawRightString(550,27,f'Página {doc.page}')
SimpleDocTemplate(W,pagesize=(595,842),leftMargin=43,rightMargin=43,topMargin=49,bottomMargin=44,title='Datavoxen - Auditoria corrigida e resolução quantitativa',author='Estudo independente').build(story,onFirstPage=foot,onLaterPages=foot)
with open(D+'/REPRODUCAO.txt','w') as f:f.write('Modelo de referência e premissas sintéticas. Execute build_datavoxen_revised.py. Fontes e limitações descritas no PDF.\n')
with zipfile.ZipFile(O+'/Datavoxen_Modelo_Corrigido_Auditavel.zip','w',zipfile.ZIP_DEFLATED) as z:
 for fn in os.listdir(D):z.write(D+'/'+fn,fn)
 z.write(__file__,'build_datavoxen_revised.py')
print('PDF',W,os.path.getsize(W),'ZIP',os.path.getsize(O+'/Datavoxen_Modelo_Corrigido_Auditavel.zip'))
print('SUMMARY',[(st,round(tot(rows[(st,'central')],'gross'),2),round(tot(rows[(st,'central')],'flow'),2),round(rows[(st,'central')][-1]['cash'],2)) for st in S])

import pathlib, json, math, pandas as pd, zipfile, importlib.util, sys
root=pathlib.Path('/mnt/data'); work=root/'datavoxen_revisado'; csv=pd.read_csv(work/'projecao_12_meses.csv'); co=pd.read_csv(work/'coortes_e_ltv.csv'); pre=json.loads((work/'premissas.json').read_text()); checks=[]
def check(name,condition):checks.append((name,bool(condition))); assert condition,name
check('144 estrategia x cenario x meses',len(csv)==144 and len(csv.groupby(['strategy','scenario']))==12)
check('sem nulos',not csv.isna().any().any())
check('receita por SKUs',all(abs(sum(r['units_'+k]*p['price'] for k,p in pre['catalogo'].items())*pre['cenarios'][r['scenario']]['spend']-r['gross'])<0.00001 for _,r in csv.iterrows()))
check('refund 2%',((csv.refunds-csv.gross*.02).abs()<.00001).all())
check('plataforma base pos-reembolso',((csv.platform-(csv.gross-csv.refunds)*.15).abs()<.00001).all())
check('imposto base pos-reembolso',((csv.tax-(csv.gross-csv.refunds)*.06).abs()<.00001).all())
check('liquido 77.42%',((csv.net-csv.gross*.7742).abs()<.00001).all())
check('contabilidade reconciliada',((csv.net+csv.refunds+csv.platform+csv.tax-csv.gross).abs()<.00001).all())
check('custo decomposicao',((csv.costs-csv[['variable','production','content','operations','marketing']].sum(axis=1)).abs()<.00001).all())
check('resultado do mes',((csv.flow-csv.net+csv.costs).abs()<.00001).all())
check('compradores elegiveis',((csv.buyers>=0)&(csv.buyers<=csv.active+1e-8)&(csv.p_buy<=1)&(csv.p_buy>=0)).all())
check('soma de unidades = compradores',((csv[[f'units_{k}' for k in pre['catalogo']]].sum(axis=1)-csv.buyers).abs()<.00001).all())
for (st,sc),d in csv.groupby(['strategy','scenario']):
 d=d.sort_values('month');check(f'caixa cumulativo {st}/{sc}',max(abs(d.cash.values-(900000+d.flow.cumsum().values)))<.00001)
 check(f'caixa utilizavel {st}/{sc}',max(abs(d.usable_cash.values-(d.cash.values-180000)))<.00001)
# import engine via prefix; avoids executing PDF rendering
engine=(root/'dv_work/build_datavoxen_revised.py').read_text().split('# Additional observed market truth')[0];ns={};exec(compile(engine,'engine','exec'),ns)
for st in 'ABC':
 base=ns['run'](st,'central'); alt=ns['run'](st,'central'); check('determinismo '+st,abs(ns['tot'](base,'gross')-ns['tot'](alt,'gross'))<1e-9)
 check('preco impacta receita '+st,abs(ns['tot'](base,'gross')-ns['tot'](ns['run'](st,'central',{'spend':1.1}),'gross'))>1)
 check('CAC impacta resultado '+st,abs(ns['tot'](base,'flow')-ns['tot'](ns['run'](st,'central',{'cac':12}),'flow'))>1)
results=[]
for st in 'ABC':
 d=csv[(csv.strategy==st)&(csv.scenario=='central')].sort_values('month');gross=d.gross.sum(); net=d.net.sum();fix=(d.operations+d.production+d.content).sum(); marketing=d.marketing.sum();variable=d.variable.sum();
 required_gross=(fix+marketing+variable)/.7742
 cap=(net-variable-fix)/d.new.sum();
 results.append((st,gross,net,fix,marketing,variable,required_gross,cap,float(d.usable_cash.min()),int(d.loc[d.usable_cash.lt(0),'month'].min()) if d.usable_cash.lt(0).any() else None))
print('CHECKS:',len(checks),'PASS:',sum(c for _,c in checks)); print('RESULTS',results)
(root/'Datavoxen_Testes_Reproduziveis_2026.txt').write_text('AUDITORIA REPRODUZIVEL | 29/10/2026\n'+'\n'.join(('PASS' if ok else 'FAIL')+' | '+n for n,ok in checks)+'\n',encoding='utf-8')
# regenerate single continuous document from original source
s=(root/'build_datavoxen_integral.py').read_text()
s=s.replace("output=root+'/Datavoxen_Estudo_Estrategico_Integral_Revisado_2026.pdf'","output=root+'/Datavoxen_Estudo_Estrategico_Definitivo_2026.pdf'")
s=s.replace("['Free Fire / App Store BR','100 diamantes R$ 4,90; 520 diamantes R$ 27,90; assinatura semanal R$ 7,90'","['Free Fire / App Store BR','100 diamantes R$ 4,90; 520 diamantes R$ 27,90; assinatura semanal R$ 7,90'")
s=s.replace("As ofertas de Free Fire, Brawl Stars e Fortnite foram reconfirmadas em listagens da App Store brasileira consultadas em 29/10/2026; as dos demais jogos preservam o registro de verificação anterior e demandam nova checagem no momento da publicação.","Listagens de Fortnite, Brawl Stars, Clash Royale, PUBG e ofertas da loja COD e Codashop VALORANT foram consultadas em 29/10/2026. Todas as sete fontes da matriz final possuem ao menos duas ofertas verificadas; os preços são pontuais e não garantem disponibilidade futura.")
s=s.replace("<b>intervalo de pesquisa</b>","<b>intervalo de pesquisa</b>")
insert='''
h('15. Fechamento da auditoria: benchmark e rastreabilidade de custos')
p('Esta seção completa, dentro do próprio relatório, as verificações documentais e computacionais. O objetivo não é atribuir precisão fictícia ao mercado, mas permitir que qualquer leitor identifique o que uma oferta pública prova, o que cada despesa do cenário representa e quais operações foram efetivamente testadas. A consulta ocorreu em 29/10/2026; promoções e itens da App Store são mutáveis, portanto recomenda-se registrar capturas ou exportações do catálogo antes de utilizar as cotações em uma decisão real.')
sub('15.1 Matriz de sete referências com pelo menos duas ofertas por jogo')
tbl(['Título e fonte','Oferta 1','Oferta 2','Status e interpretação'],[
['COD Mobile — loja web oficial [F1]','460 CP / R$ 19,49','960 CP / R$ 38,99','Verificado; valores promocionais de recarga'],
['PUBG Mobile — App Store BR [F2]','300 UC / R$ 29,90','600 UC / R$ 59,90','Verificado na listagem brasileira; moeda, não skin'],
['Free Fire — App Store BR [F3]','100 diamantes / R$ 4,90','520 diamantes / R$ 27,90','Verificado na listagem App Store Brasil; moeda, não skin'],
['Fortnite — App Store BR [F18]','800 V-Bucks / R$ 31,99','2.400 V-Bucks / R$ 79,00','Verificado; moeda virtual, não preço de um traje'],
['Brawl Stars — App Store BR [F4]','30 gemas / R$ 12,50','80 gemas / R$ 29,90','Verificado; recarga, diferente de passe'],
['Clash Royale — App Store BR [F5]','Punhado de gemas / R$ 5,90','Bolsa de gemas / R$ 29,90','Verificado; passe diamante / R$ 74,90 também listado'],
['VALORANT — Codashop BR [F19]','475 VP / R$ 18,90','1.000 VP / R$ 38,90','Verificado; referência PC adjacente, não jogo mobile']],[120,116,116,147])
p('As sete referências atendem à documentação de duas ofertas por título, mas o grau de confirmação é especificado por fonte e canal, com ofertas conferidas nas respectivas páginas públicas. O fato de existir preço anunciado não autoriza calcular market share, elasticidade ou ticket médio dos jogadores. Mesmo no caso de VALORANT, uma recarga de VP não é um preço final de skin. O sistema deverá associar a cada benchmark fonte, carimbo de consulta, canal, SKU, valor, tipo e status (reconfirmado, histórico ou indisponível).')
sub('15.2 Como o orçamento sintético foi formado e o que significam suas parcelas')
p('O orçamento não decorre de cotações de estúdios reais. É um conjunto de restrições gerenciais definido no enunciado e no arquivo premissas.json. O capital de R$ 900 mil contém reserva protegida de R$ 180 mil, deixando R$ 720 mil para compromissos operacionais. A despesa operacional fixa é R$ 35 mil/mês, ou R$ 420 mil ao longo do ano. Essa composição precisa ser compreendida antes de interpretar qualquer retorno sobre investimento: os valores medem a resistência econômica de um projeto hipotético, não o preço comprovado de produzir um jogo no Brasil.')
tbl(['Componente','Valor / regra no cenário central','Natureza e validação necessária'],[
['Operação contínua','R$ 35.000/mês; R$ 420.000/ano','Equipe, serviços, suporte e infraestrutura; abrir centro de custos e cotar'],
['Aquisição paga','6.000 contas/mês x R$ 10 = R$ 60.000/mês','CAC simulado; confirmar atribuição, fraude, elegibilidade e mix por canal'],
['Produção inicial A/B/C','R$ 65 mil / R$ 95 mil / R$ 120 mil','Orçamento de criação/lançamento; cotar arte, animação, engenharia e QA'],
['Conteúdo mensal A/B/C','R$ 10 mil / R$ 16 mil / R$ 21 mil por atualização em M4/M7/M10','Três atualizações no ano; cotar horas por SKU e aprovação'],
['Custos variáveis unitários','R$ 1 a R$ 5 por item, conforme SKU','Hipótese de suporte/entrega; não inclui produção, já alocada'],
['Deduções da receita','2% reembolso, depois 15% + 6% na mesma base','Convenção do motor; validar com lojas e contador antes de operar'],
['Reserva de caixa','R$ 180 mil não disponível para gastos ordinários','Restrição de política financeira, não custo ou despesa']],[115,151,233])
p('A soma de R$ 420 mil de operação anual com R$ 720 mil de aquisição anual, sozinha, alcança R$ 1,14 milhão. Portanto, antes de pagar produção e conteúdo, o plano central já compromete mais que os R$ 900 mil de capital inicial. Essa observação é a razão econômica para recomendar gates e não expansão: sob as premissas, o modelo tem déficit estrutural de financiamento, não apenas um preço de skin mal escolhido. A contratação real exige detalhar salários, encargos, servidores, ferramentas, localização, tributos, gateway, mídia e eventos, evitando dupla contagem de produção e custo unitário.')
sub('15.3 Resultado dos testes automatizados de consistência')
p('Uma rotina independente auditou o CSV financeiro com verificações de linhas, ausência de campos nulos, unidades e preços, deduções, composição de custos, fluxo de caixa e limites probabilísticos; também reexecutou o motor em condições idênticas e com perturbações de preço e CAC. Os resultados estão no arquivo Datavoxen_Testes_Reproduziveis_2026.txt, fornecido com o modelo. Essas verificações demonstram reprodutibilidade aritmética <b>nas regras escolhidas</b>, mas não validam preferência dos consumidores, a realidade dos custos ou aderência estatística da curva de atividade.')
tbl(['Estratégia','Bruto em 12 meses','Custos fixos / conteúdo','Compra de mídia / 12m','Leitura'],[
['A — Direta',money(results[0][1]),money(results[0][3]),money(results[0][4]),'Venda direta candidata ao piloto'],
['B — Passe',money(results[1][1]),money(results[1][3]),money(results[1][4]),'Maior exigência de conteúdo'],
['C — Híbrida',money(results[2][1]),money(results[2][3]),money(results[2][4]),'Receita maior não implica resultado maior']],[89,123,138,116,133])
p('A análise de sensibilidade deve separar modificações marginais de parâmetros dos saltos necessários para tornar a operação lucrativa. Um preço 15% maior, por exemplo, pode aumentar desembolso unitário mas reduzir a probabilidade de escolha; por isso a resposta em receita é não linear. O custo de aquisição também deve ser discriminado por origem e qualidade de usuário, porque CAC artificialmente barato que traz contas inativas não recupera capital.')
sub('15.4 Validação futura: o que não foi, e não pode ser, comprovado aqui')
p('<b>Não podemos comprovar a conversão, a retenção ou a disposição a pagar de jogadores de um produto fictício sem realizar uma pesquisa ou experimento real.</b> Para validar, é preciso recrutamento de jogadores elegíveis, questionário e experimento de escolha pré-registrados, piloto controlado com pagamentos reais quando autorizado, e acompanhamento de coortes e reembolsos. Até lá, a seleção de estratégia é uma decisão condicional sob um conjunto explícito de hipóteses. Não há espaço metodológico para chamar simulação de prova de preferência ou pesquisa empírica concluída.')
'''
# must embed results list in generated script literal
insert=insert.replace('results[0][1]',str(results[0][1])).replace('results[0][3]',str(results[0][3])).replace('results[0][4]',str(results[0][4])).replace('results[1][1]',str(results[1][1])).replace('results[1][3]',str(results[1][3])).replace('results[1][4]',str(results[1][4])).replace('results[2][1]',str(results[2][1])).replace('results[2][3]',str(results[2][3])).replace('results[2][4]',str(results[2][4]))
s=s.replace("h('15. Referências e rastreabilidade')",insert+"\nh('16. Referências e rastreabilidade')")
s=s.replace("('F18','App Store Brasil — Fortnite, itens e preços dentro do aplicativo','https://apps.apple.com/br/app/fortnite/id6483539426'),","('F18','App Store Brasil — Fortnite, itens e preços dentro do aplicativo','https://apps.apple.com/br/app/fortnite/id6483539426'),\n('F19','Codashop — VALORANT Brasil, recargas VP','https://app.codashop.com/pt-br/valorant'),")
s=s.replace("p('Verificação: preços selecionados de Free Fire, Brawl Stars e Fortnite foram conferidos em páginas App Store Brasil em 29/10/2026; preços de outros jogos seguem oriundos do registro anterior, sem nova conferência.","p('Verificação: todas as ofertas identificadas na seção 15 possuem status individual; ofertas são fotografias de preços publicamente anunciados, não projeções de compra.")
(root/'build_datavoxen_definitivo.py').write_text(s,encoding='utf-8')
exec(compile(s,str(root/'build_datavoxen_definitivo.py'),'exec'),{'__name__':'__main__'})
with zipfile.ZipFile(root/'Datavoxen_Modelo_e_Testes_Definitivos_2026.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for f in sorted(work.glob('*')):
  if f.suffix in ('.csv','.json','.txt'):z.write(f,'modelo/'+f.name)
 z.write(root/'dv_work/build_datavoxen_revised.py','modelo/motor_original.py')
 z.write(root/'Datavoxen_Testes_Reproduziveis_2026.txt','auditoria/testes_executados.txt')
 z.write(root/'finalize_dv.py','auditoria/rotina_auditoria.py')
print('PDF',root/'Datavoxen_Estudo_Estrategico_Definitivo_2026.pdf')

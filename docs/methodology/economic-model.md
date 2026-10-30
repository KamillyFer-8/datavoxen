# Modelo econômico e regras matemáticas

Referência executável: [engine.py](../../backend/app/simulation/engine.py). Premissas preservadas: [JSON original](../../backend/data/premissas.json). Não houve alteração de fórmulas na auditoria final.

## Entrada, escolha e atividade

O motor resolve os parâmetros do cenário e sobrepõe alterações validadas. Calcula 12 meses e cinco categorias possíveis; cada estratégia usa apenas seu portfólio. Para uma coorte adquirida em j, a contribuição para a atividade em m é aquisição × atividade[m−j]. Somar as coortes presentes fornece jogadores-mês elegíveis.

O denominador externo é 1 menos a soma das cinco atratividades. Cada peso é atratividade/externo × engajamento × multiplicador de preço elevado a menos elasticidade. Os pesos disponíveis competem com peso externo igual a 1. A divisão pelo denominador comum gera probabilidades de produtos e não compra, cuja soma é 1. A forma é inspirada em modelos de escolha, mas os parâmetros são heurísticos, sem estimação por respostas de consumidores.

Cada jogador-mês tem uma cesta exclusiva. Unidades são expectativas contínuas, não contagens de transações reais. Introduzir uma alternativa reduz as probabilidades dos itens anteriores e de não compra; o PDF contém uma explicação diferente desse último efeito. A implementação segue o núcleo original.

## Receita, deduções e custos

Receita bruta soma unidades × preço × multiplicador e aplica spend. Reembolsos incidem sobre a receita bruta. Plataforma e tributos incidem separadamente sobre a mesma base após reembolso. Custos variáveis são unidades × custo unitário. Produção ocorre em M1; conteúdo em M4, M7 e M10; operação e aquisição em todos os meses. Aquisição custa novas contas × CAC. Fluxo é líquido menos todos esses custos; caixa parte do capital e acumula fluxos. Reserva é subtraída do caixa para medir a parcela utilizável, sem duplicá-la como despesa.

No original, spend não altera unidades ou custo variável. O parâmetro init não participa do cálculo. Preservar essas particularidades garante fidelidade, sem atribuir-lhes interpretação empírica adicional.

## Indicadores e equilíbrio

Contribuição é receita líquida menos variável, antes de fixos e CAC. LTV parcial é contribuição da primeira coorte dividida por adquiridos, com janela de 12 meses. Coortes posteriores possuem menos meses disponíveis. Contribuição recuperável média usa contribuição total / total adquirido no horizonte, portanto inclui coortes incompletas.

ARPU = bruto / jogadores-mês ativos. ARPPU = bruto / compradores-mês. Não são razões por pessoas únicas anuais. O motor retorna ARPU zero se não há atividade e ARPPU nulo se não há compradores; são convenções de apresentação, sem receita demonstrada.

No equilíbrio por aquisição, a margem é contribuição por adquirido menos CAC. Se não positiva, não há escala finita de aquisição capaz de pagar custos fixos sob os mesmos parâmetros. O equilíbrio equivalente de jogadores-mês mantém o orçamento de mídia constante; não é previsão de aquisição e não deve ser confundido com a primeira medida.

## Sensibilidade e precisão

A interface calcula mudanças isoladas de ±15%, mantendo os demais parâmetros. A matriz original explora preços e elasticidades 0,5 / 1,25 / 2,0; o PDF sugere outro conjunto em um exercício de pesquisa. Resultados desses ensaios não devem ser apresentados como se fossem a mesma tabela.

As operações internas usam ponto flutuante, como no núcleo original. Valores monetários de saída passam por Decimal(str(valor)) com ROUND_HALF_UP em duas casas. Os totais derivam dos valores internos, sem somar parcelas mensais já arredondadas. Preços candidatos comerciais do PDF são aproximados; a API aplica precisamente fatores 0,85 / 1 / 1,15. Nenhuma grade substitui silenciosamente a outra.

Regressões: 12 resultados, 144 linhas mensais, 36 coortes centrais originais e 45 combinações originais de sensibilidade. A distribuição materializa 144 coortes para todas as combinações, não apenas as 36 do CSV original.

# Auditoria do modelo

Referências originais preservadas em `docs/references/original/`, sem alterações. O PDF tem 14 páginas. As duas imagens visuais foram recebidas em 30/10/2026 e usadas como inspiração de composição. Permanecem apenas localmente, excluídas da publicação por ausência de licença documentada. O texto do PDF foi extraído para consulta; a primeira página também foi renderizada e conferida. A auditoria final está em [relatório final](../audit/final-report.md).

## Reprodução antes da adaptação

`python scripts/audit_original.py` executa o prefixo numérico original e as 45 verificações da rotina de auditoria original. Todos passaram. Somente as referências a caminhos `/mnt/data` e a importação do núcleo foram ajustadas no executor. O arquivo original permanece intacto. As etapas legadas que geram outros documentos e ZIPs não são executadas: dependem de arquivos ausentes e não fazem parte dos checks matemáticos.

`original-audit.json` registra as verificações. `regression.json` registra os 12 resultados sem arredondamento. A regressão testa também cada campo numérico das 144 linhas do CSV e as 36 coortes centrais, em vez de conferir apenas os totais finais.

## Precisão e compatibilidade

O motor usa a aritmética de ponto flutuante do original, sem arredondar dentro dos cálculos. A saída monetária é convertida por `Decimal(str(valor))` e `ROUND_HALF_UP` a dois decimais. Quantidades e probabilidades mantêm precisão contínua. Totais usam valores não arredondados, portanto a soma dos números mensais exibidos pode diferir por centavos do total exibido.

As fórmulas de deduções, pesos de escolha, custos, atualizações e coortes foram preservadas. O modelo adaptado não importa Pandas, NumPy, renderizadores ou arquivos externos no cálculo. Pandas existe apenas nas dependências de desenvolvimento para reexecutar a auditoria original, que o utiliza.

## Divergências e particularidades encontradas

- Os resultados financeiros centrais do PDF, CSV e código coincidem. As 12 combinações também coincidem.
- O PDF faz referência a outros nomes de ZIP em seu apêndice. A proveniência desta implementação é o ZIP efetivamente fornecido, `Modelo_Datavoxen.zip`.
- O script da auditoria usa caminhos de geração de documentos não incluídos no ZIP. O executor compatível executa todos os checks originais, sem simular a existência desses documentos auxiliares.
- `init` aparece nas premissas originais, mas não é lido por `run`. Não lhe foi atribuída uma fórmula nova. Produção inicial é exposta separadamente no simulador.
- `spend` multiplica a receita sem mudar unidades ou custos variáveis no original. Foi mantido como multiplicador de gasto, com essa limitação explícita.
- O PDF menciona diferentes intervalos para pesquisas e uma sensibilidade tornado com variações específicas. A ferramenta usa uma análise marginal uniforme de ±15%, identificada no título; não a apresenta como reprodução daquela tabela.
- A matriz de benchmark da seção 15.1 foi transcrita com os links finais da seção 16. Não houve confirmação atual de preços. A classificação da aplicação é histórico documentado no estudo, sem elevar o registro textual a evidência forense.

## Métricas

ARPU: receita bruta dividida por jogadores-mês ativos. ARPPU: receita bruta dividida por compradores-mês. Compradores únicos no horizonte inteiro não podem ser inferidos dessas cestas agregadas.

LTV parcial da primeira coorte: contribuição antes de CAC e custos fixos por adquirido, com 12 meses de observação. As outras coortes têm horizontes menores. Contribuição recuperável média no horizonte: contribuição agregada / contas adquiridas; não é o mesmo número que o LTV da primeira coorte.

O ponto de equilíbrio por aquisição mantém o custo de mídia proporcional a novos jogadores. Se a contribuição por adquirido não cobre CAC, escala não resolve o déficit. A base equivalente de jogadores-mês ativos é outra medida, contábil, mantendo o orçamento de mídia atual; ela não constitui um plano de aquisição.

Atividade mensal não determina D1, D7 ou D30. O fluxo assume recebimentos no mesmo mês da receita. Todos os parâmetros econômicos são hipóteses do caso fictício.

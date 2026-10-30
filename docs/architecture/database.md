# Banco SQLite da edição 2026.1

O [esquema completo](../../backend/database/schema.sql) é a definição das tabelas, restrições e view. O [gerador](../../scripts/build_study.py) cria uma edição explicitamente; a API não executa migrações nem escreve no banco.

| Relação | Finalidade e vínculos |
|---|---|
| studies → model_versions | Estudo, versão, hash das premissas e JSON original |
| products; strategies; strategy_products | Catálogo e associação entre estratégia e produtos |
| scenarios → reference_runs | Cenários e 12 execuções, vinculadas também à versão e estratégia |
| reference_runs → monthly_results | 12 meses por execução, chave composta execução/mês |
| reference_runs → cohort_results | 12 coortes por execução, com horizonte próprio |
| reference_runs → product_results | Produtos efetivamente disponíveis em cada execução |
| sources → benchmarks | Origem, data, canal e limites de 14 ofertas |
| financial_comparison | View de resumo, sem outra cópia independente dos cálculos |

JSONs têm CHECK json_valid; meses e categorias possuem restrições; referências usam chaves estrangeiras. A verificação de distribuição executa integrity_check e foreign_key_check. Quantidades de linhas e correspondência dos resultados com o motor são verificadas fora das restrições SQL, pelos testes e auditoria.

A abertura usa URI mode=ro&immutable=1, PRAGMA query_only e fechamento em finally. immutable pressupõe que o arquivo não muda durante a operação: uma nova edição exige reconstrução controlada e reinício/deploy. Todas as conexões conferem versão e checksum de premissas, sem alegar que esse checksum seja o hash de todo o arquivo. O SHA-256 binário fica no manifesto e é conferido pela auditoria de distribuição.

```sql
SELECT strategy, scenario, gross, net, costs, flow, cash
FROM financial_comparison ORDER BY flow DESC;

SELECT strategy_id, product_id, position
FROM strategy_products ORDER BY strategy_id, position;
```

O arquivo distribuído ocupa 167.936 bytes. Não guarda contas ou dados pessoais de visitantes. Simulações personalizadas são calculadas em memória, e parâmetros podem ser guardados pelo visitante em JSON. Não é necessário instalar um servidor de banco.

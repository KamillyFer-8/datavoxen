# Verificação da edição pública

Nova auditoria pré-publicação de 30/10/2026: 52 testes Pytest, quatro Vitest, 14 casos Playwright na execução completa, build TypeScript/Vite, 45 verificações originais e 32 verificações de distribuição aprovados. npm audit e pip-audit de runtime não apontaram vulnerabilidades conhecidas. GitHub Actions reproduziu Pytest, Vitest, auditorias e build em checkout limpo no Linux.

O [relatório final](audit/final-report.md) registra problemas, correções, avisos de dependências e limites. As [evidências de dados](audit/data-evidence.json) incluem os 12 resultados e checks de hashes, integridade e equivalência ao motor.

API e SQLite também foram verificados na Vercel: 39 checks de API/SPA e 14 E2E desktop/mobile passaram nas URLs públicas. Doze combinações foram selecionadas no dashboard, e um PDF baixado pela interface. Capturas de apresentação foram preservadas; novas imagens de teste ficam somente em output. URLs, configurações e evidências estão no [relatório de publicação](audit/publication-report.md) e no [guia de deploy](architecture/deploy.md).

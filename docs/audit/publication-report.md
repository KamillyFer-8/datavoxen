# Ajustes finais e publicação

Auditoria pré-publicação de 30/10/2026, posterior à [auditoria técnica inicial](final-report.md). A responsável autorizou criação de repositório público, commits, push e deploy de produção. Este documento será atualizado com os resultados efetivamente confirmados no remoto.

## Ajustes desta etapa

README: nova seção Origem e natureza dos dados; hierarquia explícita PDF estratégico → motor Python auditado → resultados distribuídos no SQLite; endereços locais conferidos no comando Vite e no Uvicorn. A opção de não compra, spend e arredondamento continuam explicados conforme o motor, sem alterar fórmulas.

Testes: configuração E2E aceita E2E_BASE_URL para testar a implantação real sem iniciar servidores locais. Capturas de regressão passaram a ser gravadas em output, preservando as imagens já preparadas em docs/screenshots. .gitignore também exclui variantes de .env, mantendo os exemplos públicos.

O novo scripts/verify_deployment.py compara as 12 referências completas, downloads e hashes com a base local, além de simulação personalizada, CSV, PDF, sensibilidade, limites, CORS e rotas SPA. O download do SQLite antes/depois de simular permite conferir que o arquivo distribuído não mudou.

## Nova execução local

| Verificação | Resultado |
|---|---|
| Núcleo original | 45 checks aprovados |
| Reconstrução e distribuição | 32 verificações aprovadas |
| Pytest | 52 aprovados |
| Vitest | Quatro aprovados |
| Build TypeScript/Vite | Aprovado |
| E2E completo | 14 aprovados, sete desktop e sete mobile |
| npm audit | Zero vulnerabilidades reportadas |
| pip-audit das dependências de runtime | Nenhuma vulnerabilidade conhecida reportada |
| Roteiro de deploy, ensaio local | 39 verificações aprovadas; registro em local-preflight.json |

Os valores financeiros centrais continuam A −R$ 1.160.759,47; B −R$ 1.243.869,19; C −R$ 1.211.175,43. O SQLite é somente leitura e continua com 167.936 bytes. Os testes de downloads/exportações e integridade fazem parte dessas suítes. As capturas de apresentação foram preservadas.

## Publicação remota

Em execução. Resultados de GitHub Actions, URLs, commit e verificações em produção serão registrados após confirmação. Não inferir publicação a partir dos resultados locais acima.

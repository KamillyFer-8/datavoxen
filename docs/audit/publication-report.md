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

O repositório público [KamillyFer-8/datavoxen](https://github.com/KamillyFer-8/datavoxen) foi criado e o commit inicial `4897b429a76df30d63140eec6d2f90aebb39b5b9` enviado à branch main. O GitHub confirmou visibilidade pública e branch. O HTML do README contém a nova seção de dados, a hierarquia e as duas imagens desktop; os 12 binários remotos foram comparados aos hashes locais sem divergência.

O [workflow inicial](https://github.com/KamillyFer-8/datavoxen/actions/runs/41102892363) concluiu com sucesso nos jobs backend e frontend. Os logs confirmam 45 checks originais, 32 verificações de distribuição, 52 testes Pytest, quatro Vitest e build, em checkout limpo no Linux.

A integração Vercel recusou criação de projeto com 403; a responsável autorizou o login da CLI oficial, que realizou a implantação na mesma equipe ME. Não foram desativadas proteções para contornar o erro. As URLs canônicas de produção estão acessíveis anonimamente.

| Recurso | Destino verificado |
|---|---|
| Repositório público | https://github.com/KamillyFer-8/datavoxen |
| Frontend | https://datavoxen.vercel.app |
| API / OpenAPI | https://datavoxen-api.vercel.app/docs |
| Projeto API | datavoxen-api; root backend; Python 3.13; FastAPI |
| Projeto web | datavoxen; root frontend; Node.js 24; Vite; npm ci; dist |
| Variáveis | VITE_API_URL = origem canônica da API; CORS_ORIGINS = origem canônica do frontend |

O build remoto Python produziu uma função de aproximadamente 18,93 MB. O runtime serviu os oito arquivos públicos com os hashes esperados, demonstrando a inclusão dos dados necessários no bundle. A leitura das 12 referências completas coincidiu com a base local. CSV/PDF gerados em produção passaram; o download do SQLite permaneceu idêntico antes e depois de simular. Nenhuma persistência de escrita foi introduzida.

## Validação real em produção

| Verificação | Resultado |
|---|---|
| scripts/verify_deployment.py | 39 verificações aprovadas, incluindo CORS e SPA |
| Suíte Playwright na URL pública | 14 testes aprovados em uma execução completa, desktop/mobile |
| Matriz de dashboard | 12 combinações selecionadas e valores conferidos |
| PDF pela interface | Download concluído, além do teste do PDF via API |
| Console do navegador na matriz | Nenhum erro de execução |

Evidências: [API](production-evidence.json), [matriz do navegador](browser-matrix.json). As suítes exercitam dashboard, estratégias, produtos, coortes, finanças, benchmarking, relatórios, metodologia, acervo, JSON de hipóteses, erros, CSV, downloads, navegação e responsividade. Recarregamento de rotas internas foi conferido por requisição direta à SPA e navegação automatizada.

O código da aplicação implantado foi inicialmente o commit `4897b429a76df30d63140eec6d2f90aebb39b5b9`. A revisão posterior de documentação, evidências e configuração dos testes é enviada à main e usada em novos deploys dos dois projetos, com o SHA final conferido no gitSource antes da entrega. O commit final é informado na conclusão da publicação, sem tentar gravar um hash de commit dentro do próprio commit.

## Limites e operação

Não há pendência de credencial para a publicação executada. Não houve teste de carga ou pentest; os resultados financeiros permanecem sintéticos. macOS não foi executado nativamente. Os avisos de depreciação do TestClient e comentários de dependências no build não impediram os checks.

GitHub Actions está habilitado. Os projetos Vercel estão ligados ao GitHub, com produção implantada explicitamente pela CLI; deploy automático por push não foi habilitado. A configuração de SQLite continua somente leitura. Atualizações futuras exigem nova conferência e implantação, conforme o [guia de deploy](../architecture/deploy.md).

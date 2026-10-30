# Auditoria final do Datavoxen

Data: 30/10/2026. Escopo: código existente, fontes financeiras, documentação e preparação de publicação. Preservados design monocromático, motor financeiro e SQLite somente leitura. O [registro anterior às correções](initial-findings.md) separa os achados iniciais das ações posteriores.

Este é o registro histórico anterior à autorização de publicação. O estado posterior de GitHub, CI e Vercel está no [relatório de publicação](publication-report.md).

## Achados por severidade e correções

| Severidade | Problema | Correção e evidência |
|---|---|---|
| Alta | Corpo POST sem limite antes do parser | Middleware ASGI de 128 KiB, inclusive sem Content-Length; testes com corpo direto e streaming retornam 413 |
| Média | Resposta inadequada a NaN/Infinity e captura genérica de ValueError | Validação 422 sem ecoar entrada/contexto; exceção específica ArchiveVersionError; testes dos três valores não finitos |
| Média | Health não validava compatibilidade de edição | Toda conexão confere versão e hash de premissas; banco com checksum alterado retorna 503 |
| Média | Formulário podia conservar parâmetros de outra execução em cache | Reset quando os parâmetros exibidos mudam; E2E alterna estratégias e confirma restauração |
| Média | Artefatos e referências visuais sem licença na seleção pública | .gitignore exclui output, caches, imagens de inspiração e extrações auxiliares; inventário público separado |
| Média | Licença ausente | MIT autorizada para código, com THIRD_PARTY_NOTICES separando os materiais |
| Baixa | Divisão por zero na barra de composição de custos | Largura zero para total de custos zero |
| Baixa | Menu móvel sem gestão de teclado | Foco inicial, contenção de Tab, Escape, retorno de foco, conteúdo externo inert; E2E de Escape e navegação |
| Baixa | Erros nativos de rede sem contexto em português | Mensagem de indisponibilidade e timeout de 20 segundos; testes de transporte |
| Baixa | Rewrite SPA desnecessariamente complexo | Regra Vite oficial para index.html |
| Baixa | Auditoria original regravava a regressão ao executar | Comparação com regressão preservada e falha explícita se houver divergência |
| Baixa | Manifesto incluía qualquer arquivo encontrado em data | Geração limitada aos oito nomes públicos esperados |
| Documentação | README insuficiente para entender pesquisa e decisão | Reestruturação completa, com 17 temas solicitados, duas imagens desktop e documentos complementares |

Nenhum problema crítico foi comprovado. Classificação é qualitativa e relativa ao uso público deste projeto; não é certificação de segurança.

## Resultados efetivamente executados

| Verificação | Resultado nesta auditoria |
|---|---|
| Auditoria numérica original | 45 verificações aprovadas; regressão preservada |
| Fontes e distribuição | 32 verificações aprovadas: hashes, ZIP, PDF, SQLite e motor |
| Pytest | 52 aprovados |
| Vitest | Quatro aprovados em dois arquivos |
| TypeScript e Vite | Build aprovado |
| Playwright | 14 casos aprovados entre desktop e mobile; dez telas capturadas por viewport |

A execução completa de E2E aprovou os 12 casos existentes; os dois casos novos falharam inicialmente por seletor que encontrava o mesmo valor em dois elementos. O seletor passou a identificar o resultado principal; somente esses dois casos foram repetidos e ambos passaram. Não se trata de 14 testes de uma única execução integral após a correção. A correção foi restrita ao teste.

O Pytest registra depreciação do TestClient/Starlette relacionada ao transporte httpx. O build registra comentários PURE não interpretados em Zod, removidos pelo Rollup, e conclui normalmente. Não foi feita troca de dependências sem necessidade para silenciar avisos. Não houve ensaio de carga, pentest, auditoria completa das licenças transitivas nem execução nativa em macOS/Linux.

## Fidelidade financeira e SQLite

As três referências centrais continuam A −R$ 1.160.759,47; B −R$ 1.243.869,19; C −R$ 1.211.175,43. Nenhuma fórmula foi alterada para obter aprovação. As 12 referências completas coincidem com o motor, além dos testes de campos mensais, coortes e sensibilidade originais.

SQLite ocupa 167.936 bytes. Integridade e chaves estrangeiras foram aprovadas. As contagens são 12 execuções, 144 resultados mensais, 144 coortes, 40 resultados por produto e 14 benchmarks. Abertura somente leitura, tentativa de escrita rejeitada, fechamento de conexão e ausência de alteração após simulações são cobertos. SHA-256 binário é verificado pelo manifesto; a checagem online de versão/hash não substitui essa auditoria integral.

Diferenças entre texto e modelo foram documentadas: grade comercial versus multiplicadores exatos; direção da opção externa ao acrescentar produto; grades distintas de sensibilidade; 36 coortes centrais originais versus 144 materializadas; parâmetros legados spend/init e caminhos de geração de documentos. Originais não foram editados.

## API pública

Contratos restringem estratégias, cenários, categorias, horizonte, tamanhos de vetores e limites numéricos. Valores não finitos, chaves inesperadas e relações inválidas retornam 422. Corpos grandes retornam 413 antes do parser. Consultas variáveis usam parâmetros SQL; downloads usam lista fechada. Exportações são produzidas em memória e não gravam simulações. CORS restringe origens configuradas, sem autenticar clientes externos.

Não há dados privados ou credenciais necessárias à operação. A API pública continua sujeita a abuso de volume; não foi implantado um limitador distribuído ou firewall de provedor, pois não houve publicação. O limite de corpo é uma proteção delimitada, sem garantia de disponibilidade sob ataque.

## Publicação e pendências externas

GitHub: arquivos e workflow preparados; inventário de candidatos e binários em [publication-inventory.json](publication-inventory.json). O scanner procura padrões específicos e links locais; não garante ausência de qualquer dado sensível. Dependências e ambientes foram excluídos da seleção Git, sem apagar cópias locais. MIT aplica-se ao código; o aviso de terceiros explicita a ausência de licença geral dos materiais originais. A intenção de distribuí-los foi autorizada pela responsável, sem comprovação independente de titularidade nesta auditoria.

Vercel: configuração de dois projetos revisada, com SQLite como recurso fixo somente leitura. Não foi executado build Vercel remoto/local vinculado a projeto, inspecionado bundle do provedor ou testado cold start remoto. A inclusão declarada de data/** precisa ser conferida no preview. O build Vite local não prova que o bundle Python remoto inclui todos os dados.

Dependem de conta/credenciais e autorização: definir remoto GitHub, criar primeiro commit/publicação, executar Actions no serviço, vincular os dois projetos Vercel, configurar origens e variáveis, gerar preview e validar exports/downloads/rotas no provedor. Push e produção não foram realizados. Não se apresenta a aplicação como já publicada.

## Resumo das alterações por arquivo

| Arquivos | Alteração |
|---|---|
| backend/app/limits.py | Novo limite ASGI antes do parser |
| backend/app/main.py | Instalação do limite, CORS aparado, validação segura e falha de manifesto |
| backend/app/archive.py | Exceção própria, compatibilidade da edição e fechamento protegido |
| backend/tests/test_hardening.py | Oito casos de corpo, não finitos, CORS, manifesto e edição |
| frontend/src/main.tsx; styles.css | Teclado e acessibilidade do menu móvel |
| frontend/src/pages/simulator.tsx | Sincronização do formulário com a execução exibida |
| frontend/src/pages/analytics.tsx | Composição de custos com denominador zero |
| frontend/src/services/api.ts; api.test.ts | Timeout, mensagem de rede e testes |
| frontend/vitest.config.ts | Descoberta de testes .ts e .tsx |
| frontend/e2e/regression.spec.ts | Regressão de troca de referência e Escape |
| frontend/vercel.json | Rewrite SPA oficial |
| backend/.python-version | Python 3.13 declarado para manter paridade com o ambiente testado |
| frontend/package.json; package-lock.json | Declaração MIT do pacote autoral |
| scripts/audit_original.py | Preservação da regressão existente |
| scripts/build_study.py | Manifesto com nomes explícitos |
| scripts/audit_release.py | Auditoria cruzada e evidências de dados |
| scripts/audit_publication.py | Inventário público, padrões de segredos e links |
| scripts/render_readme.py | PDF de revisão adaptado às novas seções e duas capturas desktop |
| .github/workflows/ci.yml | Auditoria de distribuição após reconstrução |
| .gitignore | Exclusão de gerados e referências visuais sem licença |
| LICENSE; THIRD_PARTY_NOTICES.md | MIT e escopo dos materiais |
| README.md | Pesquisa, método, interpretação, aplicação e reprodução |
| docs/methodology/{strategy,economic-model,sources}.md | Fundamentação, regras e proveniência |
| docs/architecture/{database,deploy,visual-direction}.md | Banco, deploy e referências visuais |
| docs/methodology/audit.md; docs/verification.md | Atualização dos limites e resultados |
| docs/audit/*.md; *.json | Achados, evidências e inventário |
| docs/screenshots/*-desktop.png | Capturas reais atualizadas pelos testes |

O checkout não possui commit-base, portanto a lista descreve as intervenções desta auditoria, não um diff contra uma versão remota. A configuração original backend/vercel.json e o motor econômico foram preservados.

O PDF de revisão local em output/pdf foi atualizado para dez páginas e renderizado com Poppler para inspeção visual. Ele permanece fora da seleção do Git, como os demais artefatos gerados. O inventário final reúne 101 candidatos, 12 binários, nenhum achado nos padrões pesquisados e nenhum link local quebrado; isso não equivale a varredura universal de segredos.

# Preparação para GitHub e Vercel

Estado em 30/10/2026: execução e build locais verificados; sem push, sem deploy e sem inspeção de bundle remoto. Esta preparação não afirma que exista uma URL pública funcionando.

## Dois projetos no mesmo repositório

| Configuração | API | Interface |
|---|---|---|
| Root Directory | backend | frontend |
| Integração | FastAPI, entrada index.py | Vite |
| Instalação | requirements.txt | npm ci |
| Versão declarada | Python 3.13 em .python-version | Node.js 24 no ambiente de build |
| Build/saída | Detecção FastAPI | npm run build / dist |
| Variáveis | CORS_ORIGINS | VITE_API_URL |
| Arquivos explícitos | vercel.json inclui data/** | SPA rewrite para index.html |

CORS_ORIGINS recebe origens HTTPS completas, separadas por vírgula, sem caminhos ou barra final. Configure a origem de produção e apenas previews efetivamente autorizados. VITE_API_URL recebe a origem da API; mudar essa variável exige novo build. Nunca coloque segredos em VITE_*, que é público no JavaScript.

A [integração FastAPI oficial](https://vercel.com/docs/frameworks/backend/fastapi) admite entrypoints Python. A [configuração de funções](https://vercel.com/docs/project-configuration/vercel-json#functions) define includeFiles e maxDuration. A configuração atual limita a função a 30 segundos e inclui data/**. A [seleção de Python](https://vercel.com/docs/functions/runtimes/python/python-version) usa .python-version para manter a versão 3.13, em vez do padrão do provedor. Verifique no preview a presença do SQLite, manifesto, PDF, ZIP e CSVs; a declaração no arquivo não substitui inspeção do artefato produzido pelo provedor.

O snapshot é aberto somente leitura e não requer persistência entre invocações. A [restrição de SQLite na Vercel](https://vercel.com/kb/guide/is-sqlite-supported-in-vercel) impede tratá-lo como banco gravável persistente. Não criar tabelas, gravar simulações ou reconstruir a base em uma requisição. Uma nova edição é gerada localmente/CI e publicada como novo código.

Os cálculos têm horizonte e catálogo fixos, validação numérica e limite de corpo de 128 KiB. Exports são produzidos em memória. CORS não impede clientes fora de navegador; controles de tráfego e custos são responsabilidade da configuração do provedor. Nenhum ensaio de carga ou de ataque foi executado.

## Verificações após preview autorizado

1. Confirmar conta, projeto, commit e ambiente de destino.
2. Conferir logs e arquivos incluídos no bundle.
3. Consultar /api/health, /api/reference e comparação das 12 execuções.
4. Baixar os oito recursos e comparar tamanho/SHA-256 com manifest.json.
5. Alterar CAC, importar/exportar JSON e conferir CSV/PDF calculados.
6. Recarregar /simulador e /relatorios diretamente, conforme o [rewrite oficial Vite](https://vercel.com/docs/frameworks/frontend/vite).
7. Verificar CORS nas origens previstas, erros 422/413 e acesso por teclado/mobile.
8. Só depois avaliar promoção a produção mediante autorização.

## GitHub

.gitignore exclui ambientes, dependências, caches, segredos locais, builds, output e imagens visuais de terceiros sem licença documentada. Não exclui o SQLite oficial. LICENSE contém MIT para o código; THIRD_PARTY_NOTICES.md separa os materiais do estudo.

O workflow executa auditoria original, reconstrução, auditoria de distribuição, Pytest, Vitest e build. Nenhum segredo de deploy é necessário para essas verificações. A execução real no GitHub Actions só poderá ser confirmada após publicação autorizada. O ambiente Windows foi testado; os comandos macOS/Linux foram revisados, sem execução nesses sistemas nesta auditoria.

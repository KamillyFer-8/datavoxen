# Arquitetura da edição pública SQLite

O objetivo foi esclarecido pela proprietária: um estudo fechado para portfólio e análise pública, sem manutenção de contas ou serviço de banco na nuvem. Esta edição substitui a arquitetura inicial Supabase/PostgreSQL por uma base SQLite distribuída com o repositório. A fórmula financeira permanece a mesma.

## Fluxo dos dados

`scripts/build_study.py` cria o SQLite a partir do núcleo auditado e das premissas, usando o esquema versionado em `backend/database/schema.sql`. A geração é explícita e reproduzível, sem migrações executadas em requisições. Os originais permanecem em docs/references; cópias de distribuição em backend/data mantêm os mesmos bytes.

A API usa sqlite3 da biblioteca padrão: URI com `mode=ro&immutable=1`, `query_only=ON`, conexão por operação e fechamento em finally. O arquivo é parte imutável de uma edição do estudo. Não há senhas, perfis, registros privados ou escrita de simulações compartilhadas.

Referências oficiais vêm de reference_runs e suas tabelas filhas monthly_results, cohort_results e product_results. Premissas, catálogo, portfólios, cenários e fontes têm tabelas próprias com chaves, restrições e relações. Resumos e parâmetros completos são JSON versionado; resultados financeiros publicados são materializados como parte da edição auditável. A view financial_comparison facilita consultas externas.

O frontend consulta GET /api/reference para a seleção oficial. POST /api/simulations/preview executa alterações no motor Python; sem alterações, retorna a referência do banco. Nenhuma dessas requisições modifica o SQLite. A comparação lê os 12 resultados oficiais da base. Não existe motor financeiro no navegador.

## Acervo e exportação

GET /api/files lista arquivos de um catálogo fechado. GET /api/files/{name} serve apenas esses nomes, sem aceitar caminhos arbitrários: PDF original, SQLite, ZIP original, premissas e CSVs. O manifesto registra tamanho e SHA-256. O PDF é servido inline e os demais como download.

O visitante pode exportar resultados CSV/PDF e guardar suas hipóteses em JSON. Importação confere versão/hash e valida os parâmetros na API antes de recalcular. Cada pessoa controla seus arquivos baixados; nenhum cadastro é exigido. Recarregar a aplicação restaura a referência oficial.

## Deploy e operação

Frontend e API permanecem compatíveis com projetos Vercel separados. O bundle Python inclui backend/data; o SQLite é um recurso somente leitura, sem depender de persistência entre invocações. Não há uso de /tmp para guardar resultados ou tentativa de compartilhar gravações entre instâncias.

Horizonte de 12 meses, cinco produtos e limites de entradas mantêm o cálculo pequeno e determinístico. O backend não exige PostgreSQL, SQLAlchemy, Alembic, psycopg, Supabase, Redis ou Docker. Runtime: FastAPI, Pydantic transitivo, Uvicorn e ReportLab. Pandas só reexecuta a auditoria original em desenvolvimento.

## Verificação

A base entregue é comparada em conteúdo com duas regenerações binariamente idênticas no mesmo ambiente; cabeçalhos SQLite podem variar entre versões da biblioteca nos sistemas. Integridade, chaves estrangeiras, contagens e equivalência dos 12 resultados completos são testadas. Tentativa de escrita falha. Downloads têm checksum verificado, inclusive correspondência byte a byte com o PDF original.

A publicação real no provedor e a criação do remoto GitHub continuam etapas externas. A execução e análise local não precisam de credenciais.

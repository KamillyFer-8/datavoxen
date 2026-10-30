# Fontes e proveniência

O [PDF original](../references/Datavoxen_Relatorio_Encerrado_2026.pdf), especialmente as seções 15 e 16, preserva o registro de fontes do estudo. As ofertas do banco têm data de consulta 29/10/2026, canal, URL e limitações. São registros históricos documentados, sem reconfirmação atual dos preços. Não há evidência de compra real ou amostra própria de consumidores.

| ID no relatório | Fonte externa | Natureza |
|---|---|---|
| F1 | [Call of Duty: Mobile](https://store.callofdutymobile.com/pt-br/codm) | Recargas na loja web oficial, com condições promocionais |
| F2 | [PUBG Mobile](https://apps.apple.com/br/app/pubg-mobile/id1330123889) | Ofertas App Store Brasil |
| F3 | [Free Fire](https://apps.apple.com/br/app/free-fire/id1300146617) | Ofertas App Store Brasil |
| F4 | [Brawl Stars](https://apps.apple.com/br/app/brawl-stars/id1229016807) | Ofertas App Store Brasil |
| F5 | [Clash Royale](https://apps.apple.com/br/app/clash-royale/id1053012308) | Ofertas App Store Brasil |
| F6 | [VALORANT](https://playvalorant.com/) | Contexto do produto, complementar de PC |
| F7 | [Apple: pagamentos no Brasil](https://developer.apple.com/br/support/payment-options-on-the-app-store-in-brazil/) | Condições de distribuição e pagamento |
| F8 | [Google Play: taxa de serviço](https://support.google.com/googleplay/android-developer/answer/112622) | Contexto de plataforma; não valida taxa universal do modelo |
| F9 | [Lei 15.211/2025](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15211.htm) | Referência normativa citada no estudo, sem parecer jurídico nesta auditoria |
| F10 | [Código de Defesa do Consumidor](https://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm) | Referência de proteção ao consumidor |
| F11 | [Pesquisa Game Brasil](https://www.pesquisagamebrasil.com.br/) | Contexto de consumo e plataforma preferida |
| F12 | [gamescom latam](https://latam.gamescom.global/) | Divulgação de contexto do mercado |
| F13 | [StatCounter Brasil mobile](https://gs.statcounter.com/os-market-share/mobile/brazil) | Tráfego por sistema operacional, série de setembro de 2026 no PDF |
| F14 | [Banco Central: Pix](https://www.bcb.gov.br/estabilidadefinanceira/pix) | Contexto qualitativo de pagamento |
| F15 | [McFadden: conditional logit](https://eml.berkeley.edu/reprints/mcfadden/zarembka.pdf) | Referência metodológica; parâmetros do caso não foram estimados |
| F16 | [GameAnalytics benchmarks](https://www.gameanalytics.com/benchmarks) | Contexto de métricas; não transforma atividade hipotética em retenção real |
| F17 | [Fortnite](https://apps.apple.com/br/app/fortnite/id6483539426) | Ofertas App Store Brasil |
| F18 | [Codashop: VALORANT](https://app.codashop.com/pt-br/valorant) | Recargas históricas complementares de PC |

A lista conserva os endereços do PDF, inclusive páginas genéricas que limitam a reconstrução histórica. Não afirma que todas as páginas continuem iguais ou que tenham sido integralmente verificadas nesta auditoria. A [publicação específica da gamescom](https://latam.gamescom.global/pt/mercado-de-games-na-america-latina-quem-sao-os-jogadores-e-como-conectar-marcas-a-esse-publico/) foi consultada na auditoria de 30/10/2026 para conferir a divulgação da PGB 2026. Não foram obtidos microdados ou questionário completo.

## Arquivos do próprio estudo

PDF e ZIP foram fornecidos para fundamentar o projeto. O ZIP mantém núcleo Python, premissas, CSVs e rotina de auditoria. A cópia extraída é comparada byte a byte com seus membros por audit_release.py. As cópias públicas em backend/data são comparadas ao manifesto SHA-256.

SQLite, comparação dos cenários, capturas da aplicação e documentação técnica são artefatos da implementação. Resultados do motor são cálculos sintéticos, não observações de mercado. O [aviso de direitos](../../THIRD_PARTY_NOTICES.md) separa licença do código e materiais de referência.

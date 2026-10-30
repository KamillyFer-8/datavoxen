# Achados anteriores às correções - 30/10/2026

Fontes examinadas: README, PDF original (14 páginas), ZIP e núcleo numérico, premissas, CSVs, SQLite, manifesto, documentação, testes e capturas desktop. O PDF e os arquivos originais serão preservados.

## Dados e diferenças de interpretação

- Os 12 resultados oficiais coincidem com o motor e a regressão existente. O cenário central preserva A = -1.160.759,47; B = -1.243.869,19; C = -1.211.175,43.
- A grade comercial arredondada do PDF (seção 3) não é a mesma coisa que aplicar precisamente os fatores 0,85/1/1,15 no motor. Isso precisa aparecer na documentação; não se deve substituir os preços internos para igualar a grade do texto.
- O PDF usa nomes legados para o ZIP e caminhos `/mnt/data`, ausentes no checkout. O executor compatível preserva os checks numéricos, sem rodar a geração legada de documentos.
- A seção 4.1 do PDF sugere deslocamento para não compra ao adicionar uma alternativa. No código, mantendo os pesos anteriores, a entrada de um produto reduz tanto a probabilidade dos outros produtos quanto a não compra. A interpretação no README seguirá o código; o PDF original não será editado.
- A sensibilidade de preço do PDF cita faixas de ensaio diferentes do CSV. A interface calcula perturbações uniformes de 15%; esses conjuntos não devem ser apresentados como uma única tabela idêntica.
- A base tem 144 coortes nas 12 combinações; o CSV original de coortes tem 36 linhas, apenas para o central. Não é inconsistência numérica.

## Problemas a verificar e corrigir

| Severidade | Achado | Ação delimitada |
|---|---|---|
| Alta | API pública sem limite de bytes antes do parser JSON | Limitar o corpo sem alterar o cálculo |
| Média | Erros de validação com valores não finitos podem ter resposta inadequada; ValueError genérico tratado como erro de versão | Respostas 422 seguras e exceção específica da base |
| Média | Health confirma a existência de uma versão, mas não confirma seu checksum | Validar versão/checksum nas conexões |
| Média | Formulário usa defaultValues iniciais e pode manter valores antigos quando troca para uma referência já em cache | Sincronizar com a execução efetivamente exibida |
| Média | Publicação incluiria artefatos gerados, duplicações e imagens de referência sem licença documentada | Curar arquivos pelo .gitignore, preservar cópias locais |
| Média | Ausência de licença do código | Aplicar MIT autorizada pela proprietária, separada dos materiais do estudo |
| Baixa | Barra de custos pode produzir NaN% quando todos os custos são zero | Representar largura zero |
| Baixa | Menu mobile não gerencia Escape e foco como painel modal | Corrigir teclado e verificar E2E |
| Baixa | Falha de rede no fetch mostra mensagem nativa em inglês | Mensagens em português e timeout |
| Baixa | Rewrite SPA mais complexo que o exemplo oficial da Vercel | Adotar regra oficial simples |
| Documentação | README apresenta pouco contexto econômico e insuficiente fundamentação estratégica | Reestruturar a sequência pesquisa, método, decisão e software |

Nenhuma falha crítica foi comprovada nesta etapa. O relatório final registrará o que foi corrigido e o que não pôde ser validado em produção. Não haverá push ou deploy em produção sem autorização.

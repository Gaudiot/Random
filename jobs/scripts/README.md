# Scripts de apoio

## Estimar linhas e páginas de um texto

```powershell
python jobs/scripts/estimate_text_layout.py --text "Texto de um bloco do currículo."
python jobs/scripts/estimate_text_layout.py --file jobs/job-description.txt
Get-Content -Raw jobs/job-description.txt | python jobs/scripts/estimate_text_layout.py
```

Aceita texto direto, arquivo de texto UTF-8 ou entrada padrão e retorna JSON com
`total_lines`, `total_pages`, `page_equivalent` e `word_count`. Não modifica arquivos.
Também pode ser importado: `estimate_text_layout(text)`.

O padrão é **52 linhas por página** e **15,5 palavras por linha**, a média entre
15 e 16. Cada quebra explícita começa outra linha; uma linha longa ocupa
`ceil(palavras / 15,5)` linhas. Linhas vazias ou apenas com espaços contam como
uma linha. Texto vazio ocupa zero linhas. Uma quebra final apenas encerra a
última linha: `texto\n` ocupa uma linha e `texto\n\n` ocupa duas.

`total_pages` arredonda para cima: 53 linhas precisam de duas páginas.
`page_equivalent` mostra a fração ocupada (53/52 = 1,0192).
Use `--words-per-line 15` ou `--words-per-line 16` para outras estimativas;
`--lines-per-page` também pode ser configurado.

Esta é uma estimativa por palavras, sem medir fonte, largura, margens ou estilos.
Ela ajuda a planejar um texto ou bloco, mas não substitui a renderização do DOCX
no Word para confirmar o limite de duas páginas.

## Scripts do role-finder

Requerem Python 3.10+ e usam apenas a biblioteca padrão. Execute os comandos abaixo na raiz do repositório. Os caminhos de entrada padrão são resolvidos em relação aos scripts; `--output`, `--selection`, `--source` e `--roles` explícitos são relativos ao diretório de execução.

## Selecionar empresas

```powershell
python jobs/scripts/select_companies.py --limit 20 --output jobs/selected_companies.json
```

Seleciona, na ordem original, empresas de tipo `Company` (ignorando capitalização e espaços), com nome, URL HTTP(S) válida e `available_from` em `YYYY-MM-DD` menor ou igual à data local da execução. Entradas inválidas e datas futuras são ignoradas com diagnóstico em stderr. Duplicatas com o mesmo nome, URL e data são removidas antes do limite. Se o mesmo nome/URL tiver datas conflitantes, todo o grupo é ignorado até a origem ser corrigida. Omita `--limit` para selecionar todas; sem `--output`, o manifesto é impresso em stdout. O script não acessa sites nem altera `opportunities.json`.

O manifesto contém a data, o hash SHA256 da origem e as empresas com seus índices originais. Use esse escopo para a busca do agente e grave em `jobs/open_roles.json` as vagas verificadas e as empresas cujo acesso permaneceu bloqueado ou indisponível após as tentativas limitadas.

Vagas verificadas usam o título e o link de candidatura. Empresas para revisão manual usam os mesmos três campos, mas com `role` igual a `Revisão manual — acesso bloqueado ou indisponível` e `url` igual à URL inicial da empresa no manifesto. Essa entrada não representa uma vaga confirmada. Uma tentativa que falha não basta para marcar bloqueio quando outra fonte oficial funciona; paginação incompleta ou falta de tempo também não são bloqueio.

## Adiar empresas incluídas no resultado

Depois de concluir e validar a busca:

```powershell
python jobs/scripts/update_available_from.py --selection jobs/selected_companies.json --dry-run
python jobs/scripts/update_available_from.py --selection jobs/selected_companies.json
```

A primeira chamada mostra as alterações sem gravar. A segunda atualiza apenas `available_from` das empresas selecionadas que aparecem em `open_roles.json`, para a data local da execução mais 14 dias. Isso inclui empresas bloqueadas com entrada de revisão manual, mesmo quando nenhuma vaga pôde ser verificada. Várias entradas da mesma empresa geram uma única atualização. Empresas apenas visitadas, verificadas sem vagas compatíveis ou pendentes fora do resultado mantêm a data. Um resultado vazio preserva o arquivo byte a byte.

O atualizador recusa manifesto de outro dia, origem alterada, empresas desconhecidas ou ambíguas e resultados com formato inválido. Uma fonte duplicada de empresa/URL também impede a atualização daquela execução, inclusive quando a cópia está fora do limite selecionado; nenhuma entrada extra é alterada silenciosamente. As três chaves de cada vaga devem ser `company_name`, `role` e `url`. Campos alheios, incluindo `applied_qtt` e `last_updated`, são preservados; a gravação é atômica, com formatação JSON em quatro espaços.

Após uma atualização bem-sucedida, o manifesto antigo fica obsoleto porque a origem mudou. Para uma nova busca, gere nova seleção e novos resultados. Não regenere apenas o manifesto para reaplicar resultados antigos: o script valida o escopo, mas a verificação da busca atual cabe ao agente. Os scripts também não decidem aderência ao currículo nem enviam candidaturas.

## Remover arquivos de apoio ao finalizar

`selected_companies.json`, `role_finder_checkpoint.json` e `role_finder_report.md` são temporários. O agente pode criá-los durante a execução, mas deve removê-los ao terminar, depois da atualização e das verificações, inclusive quando finalizar com uma falha explicitamente informada. Primeiro conserve em memória o resumo necessário para a resposta. Os scripts de seleção/atualização não fazem essa limpeza sozinhos: precisam do manifesto até concluir o trabalho.

Na raiz do repositório, após finalizar as verificações:

```powershell
Remove-Item -LiteralPath jobs/selected_companies.json,jobs/role_finder_checkpoint.json,jobs/role_finder_report.md -ErrorAction SilentlyContinue
```

Confirme que esses caminhos não existem mais. Preserve `open_roles.json`, `opportunities.json`, o currículo, scripts, testes e outros arquivos do usuário. Um checkpoint pode ajudar se a execução for interrompida antes dessa finalização; execuções concluídas não deixam checkpoint nem prometem retomada a partir dele.

## Validação

```powershell
python -m unittest discover -s jobs/tests -p 'test_*.py' -v
```

Os testes usam arquivos temporários, sem alterar os dados reais de oportunidades.

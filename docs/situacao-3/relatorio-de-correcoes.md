# Relatório de correções

Consolidação dos problemas apontados pelos testadores e encontrados em revisão interna, com o que foi feito em cada caso. Cada correção foi feita em um commit próprio e ganhou um teste automatizado de regressão, para o erro não voltar.

> Preencha a coluna **Encontrado por** com o nome do testador (ou "revisão interna", se nenhum testador encontrou) e o número do laudo.

## Bugs

| # | Problema | Encontrado por | Gravidade | Causa | Correção | Teste de regressão |
|---|---|---|---|---|---|---|
| 1 | Diminuir a quantidade até 0 mantinha o item na cesta, e o pedido era gravado com "0×" | | Média | `diminuir()` usava `Math.max(0, …)` e nunca removia o item; a API aceitava quantidade 0 (`ge=0`) | O item sai da cesta ao chegar a zero; a API exige quantidade mínima 1 (`ge=1`) | `test_recusa_quantidade_zero` |
| 2 | Buscar "tomate" (minúsculo) não encontrava "Tomate orgânico" | | Baixa | `LIKE` no PostgreSQL diferencia maiúsculas de minúsculas | Busca com `ILIKE` | `test_busca_ignora_maiusculas` |
| 3 | O estoque não diminuía depois da compra, permitindo vender mais do que existe | | **Alta** | `criar_pedido()` verificava o estoque, mas não o descontava | Estoque descontado na mesma transação do pedido; linhas travadas com `SELECT … FOR UPDATE` para pedidos simultâneos | `test_compra_desconta_estoque`, `test_pedido_recusado_nao_desconta_estoque` |
| 4 | O telefone aceitava letras | | Média | Validação só de tamanho, no front e na API | API exige 10 ou 11 dígitos e recusa letras; campo `type="tel"` com `pattern` no formulário | `test_recusa_telefone_invalido` (3 casos) |
| 5 | Cesta de exatamente R$ 150,00 mostrava frete grátis, mas o pedido cobrava R$ 12,00 | | Média | Servidor usava `>` e o front usava `>=` na regra "grátis **a partir de** R$ 150" | Servidor passou a usar `>=`, igual ao front e à regra RN01 | `test_frete_gratis_exatamente_no_limite` |

### Commits

| # | Commit |
|---|---|
| 1 | `fix: remove item da cesta ao chegar a zero e recusa quantidade 0 na API (#1)` |
| 2 | `fix: busca de produtos ignora maiúsculas e minúsculas (#2)` |
| 3 | `fix: desconta o estoque ao confirmar o pedido (#3)` |
| 4 | `fix: valida telefone com DDD e sem letras (#4)` |
| 5 | `fix: frete grátis também para pedidos de exatamente R$ 150,00 (#5)` |

## Sugestões de melhoria

| # | Sugestão | Testador | Adotada? | Justificativa |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |

## Resultado dos testes após as correções

```
$ pytest
.................................................                        [100%]
49 passed
```

Antes das correções eram 41 testes; foram adicionados 8 testes de regressão (incluindo os casos parametrizados). Os testes também rodam automaticamente no GitHub Actions a cada envio de código.

## Lições aprendidas

- **Regra de negócio em um lugar só.** O bug do frete aconteceu porque a regra existia duplicada no front e no back, com operadores diferentes. O valor que vale é sempre o do servidor; o front só exibe.
- **Validar no servidor, não só no formulário.** A validação do navegador melhora a experiência, mas pode ser contornada; a API precisa recusar dados inválidos por conta própria.
- **Testar os limites.** Quantidade 0 e valor exatamente igual ao limite (R$ 150,00) são os casos que mais escondem erros.
- **Testes com usuários reais encontram o que os testes automatizados não cobrem.** Cada bug encontrado virou um teste novo, para não voltar.

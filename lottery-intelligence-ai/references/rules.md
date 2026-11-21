# Regras oficiais e eras de matriz

> Verifique sempre no site oficial antes de uma análise: as loterias mudam regras periodicamente.
> Fontes: https://www.megamillions.com/How-to-Play.aspx · https://www.powerball.com/powerball

## Mega Millions

| Item | Valor vigente |
|---|---|
| Números principais | 5 distintos de **1 a 70** |
| Mega Ball | 1 de **1 a 24** |
| Preço | **US$ 5** por aposta (desde 08/04/2025) |
| Multiplicador | Embutido em toda aposta (2x a 10x) nos prêmios que não são o jackpot; **Megaplier extinto** |
| Sorteios | Terça e sexta, 23h00 ET |
| Chance do jackpot | C(70,5) × 24 = **1 em 290.472.336** |

**Eras (para o motor):**
- 31/10/2017 → hoje: principais 1–70 (antes 1–75) → `main_since = 2017-10-31`
- 31/10/2017 → 07/04/2025: Mega Ball 1–25
- 08/04/2025 → hoje: Mega Ball **1–24** → `special_since = 2025-04-08`

Consequência: a amostra da Mega Ball na matriz atual é pequena. O motor avisa (`small_sample_warning`).

## Powerball

| Item | Valor vigente |
|---|---|
| Números principais | 5 distintos de **1 a 69** |
| Powerball | 1 de **1 a 26** |
| Preço | **US$ 2** por aposta; Power Play +US$ 1; Double Play onde disponível |
| Sorteios | Segunda, quarta e sábado, 22h59 ET |
| Chance do jackpot | C(69,5) × 26 = **1 em 292.201.338** |

**Era:** 07/10/2015 → hoje (antes: 1–59 e Powerball 1–35) → `main_since = special_since = 2015-10-07`.

## Faixas de acerto (ambos os jogos)

| Acertos | Faixa |
|---|---|
| 5 + especial | Jackpot |
| 5 | 2º prêmio |
| 4 + especial / 4 | prêmios fixos (multiplicáveis) |
| 3 + especial / 3 | prêmios fixos |
| 2 + especial / 1 + especial / só especial | prêmios fixos |

Valores exatos: consultar a tabela oficial do jogo e do estado (Califórnia usa prêmios pari-mutuel).
O motor informa apenas a **faixa**, nunca um valor que não tenha sido lido na fonte oficial.

## Checklist de mudança de regra
- [ ] Faixa de números principais mudou? → editar `main_max` e `main_since` em `GAMES`.
- [ ] Faixa da bola especial mudou? → editar `special_max` e `special_since`.
- [ ] Preço mudou? → editar `price_usd`.
- [ ] Rodar `rules --game ...` e conferir a chance calculada com a publicada no site.

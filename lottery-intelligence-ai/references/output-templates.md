# Modelos de saída

> Os números abaixo são **ilustrativos de formato**, não recomendações. Em uso real, todos os números vêm
> do motor.

## Relatório completo (Modo 1 / Modo 3)

```markdown
# 🎯 LOTTERY INTELLIGENCE AI — Relatório de <data>

**Fonte:** NY Open Data + conferência em megamillions.com / powerball.com · consulta em <data/hora>
**Último sorteio incluído:** MM <data> · PB <data>
**Próximo sorteio:** MM <dia, data, 23h00 ET> · PB <dia, data, 22h59 ET>

## MEGA MILLIONS
<saída de `analyze --format md`>

## POWERBALL
<saída de `analyze --format md`>

## 🎟️ Combinações recomendadas
<saída de `generate --format md` para cada jogo>

## ✅ Fatos × 💡 Sugestões
- ✅ <3–5 fatos objetivos do relatório>
- 💡 <por que estas combinações — critério, diversidade, anti-rateio>

## ⚠️ Probabilidade
Cada combinação: 1 em 290.472.336 (MM) / 1 em 292.201.338 (PB). Estatística organiza escolhas; não prevê.

> Jogue apenas o que pode perder. 1-800-GAMBLER.
```

## Bloco de combinação (padrão fixo)

```text
MEGA MILLIONS — Combinação 1 · Estatística
Números principais: 08 - 17 - 29 - 46 - 63
Mega Ball: 12
```
Critério: … · Perfil: pares/ímpares 2/3 · baixos/altos 2/3 · soma 163 (percentil 41) · 5 faixas

## Análise de cartela (Modo 2)

```markdown
## 📷 Cartela identificada: POWERBALL (grade 1–69 + 1–26) · playslip · 5 painéis

| Painel | Marcados (certos) | Incertos | Powerball | Status |
|---|---|---|---|---|
| A | 03 - 19 - 27 - 41 - 58 | — | 10 | ✅ válido |
| B | 07 - 22 - 35 | 50? | — | ⚠️ incompleto / 1 incerto |
| C–E | — | — | — | disponível |

### Problemas encontrados
- Painel B: faltam 2 números e a Powerball; marcação no 50 está fraca — confirme.

### ✍️ O que marcar
PAINEL B — completar com: 46 - 61   |  Powerball: 18
PAINEL C — marcar: 11 - 24 - 38 - 52 - 66 | Powerball: 04
```

## Comparação (Modo 4)

| Combinação | Pares/Ímp | Baixos/Altos | Soma (pct) | Faixas | Sequência | Popularidade | Melhor acerto histórico |
|---|---|---|---|---|---|---|---|

Seguir com: **ajustes sugeridos** (trocar X → Y, motivo) e lembrete de que a chance é idêntica.

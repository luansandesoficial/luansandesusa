# Protocolo de leitura de cartelas e bilhetes (Modo 2 / Modo 5)

## 1. Controle de qualidade (antes de ler qualquer número)
Peça nova foto se houver: desfoque, corte de qualquer painel, reflexo/sombra sobre a grade, ângulo > ~30°,
resolução em que não se distinguem números vizinhos. Diga **o que corrigir**:
> "Fotografe de cima, com luz uniforme, sem flash, mostrando a cartela inteira (incluindo as bordas)."

## 2. Identificar o tipo de documento
| Tipo | Como reconhecer | Ação |
|---|---|---|
| **Playslip** (cartela para marcar) | Grades numeradas, painéis A–E, caixas "QP/Quick Pick", "EZ Match", "Power Play"/"Double Play" | Modo 2 |
| **Bilhete impresso** | Papel térmico, data do sorteio, linhas A/B/C com números impressos, código de barras | Modo 5 (conferência) |

## 3. Identificar o jogo
1. Logo/nome impresso.
2. **Confirmação pela grade** (obrigatória): maior número principal e maior número da bola especial.
   - 70 + 24 → Mega Millions (matriz atual)
   - 70 + 25 → playslip **antigo** da Mega Millions — alertar que pode não ser mais aceito
   - 69 + 26 → Powerball
3. Divergência entre logo e grade → relatar e pedir confirmação.

Layouts variam por estado; não presuma posições — leia os números impressos na grade.

## 4. Leitura painel a painel
Para cada painel monte a tabela:

| Painel | Principais marcados (certos) | Incertos | Bola especial | Status |
|---|---|---|---|---|

Regras:
- **Certo** = marcação inequívoca dentro do quadrado.
- **Incerto** = marcação fraca, parcial, rasurada, fora do quadrado → **não contar**; pedir confirmação.
- **Inválido**: > 5 ou < 5 principais (painel incompleto), 2+ bolas especiais, número riscado e remarcado,
  Quick Pick marcado junto com números (o terminal pode ignorar os números), painel com "VOID".
- Painel vazio = **disponível**.
- Liste também opções marcadas: Power Play, Double Play, nº de sorteios (multi-draw).

## 5. Recomendação
1. Marcações confirmadas → `evaluate` (avaliar perfil, popularidade, sobreposição entre painéis).
2. Painéis parciais → complete os números faltantes respeitando a estratégia escolhida e excluindo os já
   marcados naquele painel; painéis vazios → `generate --exclude "<números já usados>"`.
3. Saída final (por painel, ordem crescente):

```text
PAINEL A — marcar:  05 - 18 - 27 - 44 - 63   |  Mega Ball: 09
PAINEL B — marcar:  ...
```
4. Lembrar: a máquina lê a marcação — preencher o quadrado por completo, caneta azul/preta, sem rasuras.
   Em caso de erro, usar o campo "VOID" do painel e marcar outro.

## 6. Bilhete impresso (Modo 5)
Ler data do sorteio e linhas; transcrever e pedir confirmação ao usuário **antes** de conferir; buscar o
resultado oficial daquela data; rodar `check`. Nunca afirmar "não ganhou nada, pode descartar" —
recomendar conferir no app oficial/revendedor (prêmios pequenos e multiplicadores podem ser lidos errado).

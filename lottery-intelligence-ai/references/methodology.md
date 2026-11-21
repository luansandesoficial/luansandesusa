# Metodologia estatística (como ler cada número do relatório)

Notação: N = maior número principal (70 ou 69), n = sorteios analisados, 5 números por sorteio.

## A. Frequência
- **Esperado por número** = n × 5 / N. A coluna "vs esperado" mostra o desvio percentual.
- **Teste qui-quadrado** (gl = N − 1): mede se o conjunto das frequências é compatível com sorteio uniforme.
  p ≥ 0,05 → desvios são o ruído normal do acaso (resultado esperado em loteria auditada).
  Aproximação: os 5 números de um sorteio não são independentes entre si (sem reposição), o que torna o teste
  levemente conservador — suficiente para diagnóstico.
- Leitura correta: "o 23 saiu 37% acima do esperado" é **fato**; "o 23 tende a sair" é **falso**.

## B. Janelas recentes (10/30/50)
- Em 10 sorteios cada número aparece em média ~0,7 vez: rankings dessa janela são quase puro ruído.
  Apresente, mas rotule como descritivo.

## C. Distribuição
- **Paridade e baixos/altos**: o teórico vem da hipergeométrica, P(k) = C(K,k)·C(N−K,5−k)/C(N,5).
  2/3 e 3/2 somam ~64% dos sorteios — por isso são a base da estratégia Equilibrada.
- **Baixos**: 1–35 (MM) e 1–34 (PB).
- **Soma**: média teórica = 5(N+1)/2 (177,5 MM; 175 PB). P25–P75 contém metade dos sorteios.
- **Faixas de dezena**: a última faixa é menor (61–70 / 61–69) — compare com o teórico, não com 10%.
- **Repetição do sorteio anterior**: teórico = 25/N ≈ 0,36 número.

## D. Pares e trincas
- Esperado por par = n·20/(N(N−1)) (≈ 3,4 em ~830 sorteios MM). Existem 2.415 pares (MM): alguns
  aparecerão 3x o esperado só por acaso (problema das comparações múltiplas). Nunca trate um par
  "recorrente" como sinal.
- Trincas: esperado ≈ 0,1 por trinca. Uma trinca repetida 2x é curiosidade, não padrão.

## E. Ausência (atraso)
- Atraso médio teórico = N/5 − 1 sorteios. A distribuição é geométrica: atrasos de 4–6× a média ocorrem
  naturalmente para algum número em qualquer janela longa.
- **Falácia do apostador**: sorteios são independentes; atraso não aumenta a chance.

## Por que "evitar números populares" é a única vantagem real
A probabilidade de acertar é idêntica para qualquer combinação, mas o **prêmio por ganhador** não: se muitas
pessoas jogam a mesma combinação, o jackpot é dividido. Padrões muito jogados:
- todos os números ≤ 31 (datas), sequências (1-2-3-4-5), progressões, linhas/diagonais da cartela,
  múltiplos de 5/7, números do último sorteio, números "famosos" (ex.: 4-8-15-16-23-42).
Evitá-los melhora o **valor esperado condicional ao prêmio**, não a chance. O Quick Pick (aleatório) já é
uma boa forma de fugir de padrões humanos — diga isso ao usuário com honestidade.

## Valor esperado (para conversas sobre orçamento)
VE de uma aposta = Σ (prêmio × probabilidade) − preço. Para jackpots usuais, o VE é negativo mesmo
antes de impostos e rateio. Use isso para reforçar orçamento fixo, nunca para incentivar apostar mais.

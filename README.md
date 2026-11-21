# 🎯 LOTTERY INTELLIGENCE AI — Skill para Claude

Analista estatístico da **Mega Millions** e da **Powerball**: frequências, janelas recentes, atrasos,
distribuição, pares/trincas, gerador de combinações, leitura de **fotos de cartelas** e conferência de bilhetes.
Tudo calculado por um motor Python determinístico a partir de dados oficiais — sem estatísticas inventadas.

## Estrutura

```
lottery-intelligence-ai/
├── SKILL.md                      # instruções principais (modos 1–5, regras de confiabilidade)
├── scripts/lottery_engine.py     # motor estatístico (Python 3.9+, só biblioteca padrão)
└── references/
    ├── rules.md                  # regras vigentes + eras de matriz
    ├── data-sources.md           # fontes oficiais e protocolo de atualização
    ├── methodology.md            # como interpretar cada estatística
    ├── ticket-vision.md          # protocolo de leitura de cartelas/bilhetes por foto
    └── output-templates.md       # modelos de saída
dist/lottery-intelligence-ai.zip  # pacote pronto para upload
```

## Instalação

| Onde | Como |
|---|---|
| **claude.ai** | Configurações → Capacidades → Skills → *Upload skill* → enviar `dist/lottery-intelligence-ai.zip` (requer execução de código ativada) |
| **Claude Code** | Copiar a pasta `lottery-intelligence-ai/` para `~/.claude/skills/` (pessoal) ou `.claude/skills/` (projeto) |

## Uso rápido do motor

```bash
cd lottery-intelligence-ai
curl -L -o pb.csv "https://data.ny.gov/api/views/d6yy-54nr/rows.csv?accessType=DOWNLOAD"
curl -L -o mm.csv "https://data.ny.gov/api/views/5xaw-6ayf/rows.csv?accessType=DOWNLOAD"

python3 scripts/lottery_engine.py analyze  --game pb --csv pb.csv
python3 scripts/lottery_engine.py generate --game mm --csv mm.csv --tickets 3 --budget 15 --seed 2026
python3 scripts/lottery_engine.py evaluate --game pb --csv pb.csv --ticket "7 19 33 48 66 | 12"
python3 scripts/lottery_engine.py check    --game pb --ticket "7 19 33 48 66 | 12" --draw "7 19 40 48 66 | 12"
```

## Exemplos de prompts
- "Análise completa das duas loterias e 3 combinações para cada, orçamento US$ 20."
- *(foto da cartela)* "Quais números devo marcar?"
- "Compare estas apostas: 5 12 33 48 61 | 7 e 1 2 3 4 5 | 6."
- "Confira meu bilhete do sorteio de ontem." *(foto)*

## ⚠️ Aviso
Loterias são aleatórias. Toda combinação válida tem a mesma probabilidade (MM 1 em 290.472.336; PB 1 em
292.201.338). A Skill organiza escolhas e evita padrões populares (menor risco de dividir o prêmio); não prevê
resultados. Jogue com responsabilidade — 1-800-GAMBLER.

#!/usr/bin/env python3
"""
LOTTERY INTELLIGENCE AI — motor estatístico (somente biblioteca padrão).

Por que este script existe
--------------------------
Um modelo de linguagem NÃO deve "estimar de cabeça" frequências, atrasos ou somas:
isso gera números inventados. Este motor recebe o histórico oficial (CSV) e calcula
tudo de forma determinística e auditável. A Skill só apresenta o que sai daqui.

Subcomandos
-----------
  analyze   Relatório estatístico completo (frequência, janelas 10/30/50, atrasos,
            paridade, baixos/altos, faixas, soma, pares, trincas, bola especial,
            teste qui-quadrado de uniformidade).
  generate  Gera combinações (estatística, equilibrada, diversificada) validadas
            pelas regras oficiais vigentes.
  evaluate  Avalia combinações informadas pelo usuário (ou lidas de uma cartela).
  check     Confere um bilhete contra um resultado (faixa de acerto).
  rules     Mostra as regras/matriz vigentes usadas pelo motor.

Formatos de CSV aceitos (detecção automática)
---------------------------------------------
  1) NY Open Data — Powerball:      "Draw Date,Winning Numbers,Multiplier"
     (Winning Numbers = 6 números; o último é a Powerball)
  2) NY Open Data — Mega Millions:  "Draw Date,Winning Numbers,Mega Ball,Multiplier"
  3) Normalizado: date,n1,n2,n3,n4,n5,special
     (também aceita colunas "mega_ball"/"powerball" no lugar de "special")

Exemplos
--------
  python3 lottery_engine.py analyze  --game mm --csv mm.csv --format md
  python3 lottery_engine.py generate --game pb --csv pb.csv --seed 42
  python3 lottery_engine.py evaluate --game mm --csv mm.csv --ticket "5 12 33 48 61 | 7"
  python3 lottery_engine.py check    --game pb --ticket "1 2 3 4 5 | 6" --draw "1 9 3 22 50 | 6"

Aviso: todas as combinações válidas têm exatamente a mesma probabilidade em um
sorteio justo. O motor organiza dados históricos; ele NÃO prevê resultados.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
import statistics
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime
from itertools import combinations
from typing import Iterable

# ---------------------------------------------------------------------------
# 1. REGRAS OFICIAIS VIGENTES (matriz) + "eras" históricas
# ---------------------------------------------------------------------------
# Misturar sorteios de matrizes antigas distorce frequências (ex.: a Mega Ball
# 25 deixou de existir em 08/04/2025). Por isso cada jogo define a data a partir
# da qual a matriz atual vale — separadamente para bolas principais e especial.
GAMES = {
    "mm": {
        "name": "Mega Millions",
        "main_max": 70,            # 5 números de 1 a 70
        "special_max": 24,         # Mega Ball de 1 a 24
        "special_name": "Mega Ball",
        "main_since": date(2017, 10, 31),     # início da matriz 5/70
        "special_since": date(2025, 4, 8),    # Mega Ball 1–24 (antes 1–25)
        "price_usd": 5.00,
        "draw_days": "Terça e sexta, 23h00 (horário do Leste dos EUA)",
        "notes": "Desde 08/04/2025: bilhete de US$ 5, multiplicador 2x–10x embutido "
                 "em prêmios que não são o jackpot; Megaplier extinto.",
    },
    "pb": {
        "name": "Powerball",
        "main_max": 69,            # 5 números de 1 a 69
        "special_max": 26,         # Powerball de 1 a 26
        "special_name": "Powerball",
        "main_since": date(2015, 10, 7),      # início da matriz 5/69 + 1/26
        "special_since": date(2015, 10, 7),
        "price_usd": 2.00,
        "draw_days": "Segunda, quarta e sábado, 22h59 (horário do Leste dos EUA)",
        "notes": "Power Play opcional (+US$ 1). Double Play disponível em alguns estados.",
    },
}

PICK = 5  # quantidade de números principais em ambos os jogos


@dataclass(frozen=True)
class Draw:
    """Um sorteio: data, 5 números principais ordenados e a bola especial."""
    when: date
    main: tuple[int, ...]
    special: int


# ---------------------------------------------------------------------------
# 2. LEITURA E VALIDAÇÃO DE DADOS
# ---------------------------------------------------------------------------
DATE_FORMATS = ("%m/%d/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f",
                "%d/%m/%Y")


def parse_date(text: str) -> date:
    text = text.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Data não reconhecida: {text!r}")


def ints_in(text: str) -> list[int]:
    """Extrai todos os inteiros de um texto ("05 12 33" -> [5, 12, 33])."""
    return [int(x) for x in re.findall(r"\d+", text or "")]


def load_draws(paths: list[str], game: str) -> tuple[list[Draw], list[str]]:
    """Lê um ou mais CSVs (ex.: histórico oficial + sorteios recentes digitados),
    detecta o formato de cada um, valida as linhas e devolve (sorteios, avisos)."""
    draws: list[Draw] = []
    warnings: list[str] = []
    for path in paths:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            # normaliza cabeçalhos: minúsculas, sem espaços extras
            reader.fieldnames = [(h or "").strip().lower() for h in (reader.fieldnames or [])]
            for lineno, row in enumerate(reader, start=2):
                try:
                    draws.append(_row_to_draw(row))
                except (ValueError, KeyError) as exc:
                    warnings.append(f"{path} linha {lineno}: ignorada ({exc})")
    draws.sort(key=lambda d: d.when)
    # remove datas duplicadas (alguns exports repetem linhas)
    unique: dict[date, Draw] = {}
    for d in draws:
        if d.when in unique and unique[d.when] != d:
            warnings.append(f"{d.when}: data duplicada com números diferentes — mantida a 1ª")
            continue
        unique.setdefault(d.when, d)
    draws = list(unique.values())
    if not draws:
        raise SystemExit("Nenhum sorteio válido encontrado no(s) CSV(s).")
    return draws, warnings


def _row_to_draw(row: dict) -> Draw:
    date_key = next((k for k in row if k in ("draw date", "date", "draw_date", "data")), None)
    if not date_key:
        raise KeyError("coluna de data ausente")
    when = parse_date(row[date_key])

    if "winning numbers" in row:
        nums = ints_in(row["winning numbers"])
        special_col = next((k for k in ("mega ball", "powerball", "special") if row.get(k)), None)
        if len(nums) == 6 and not special_col:      # formato Powerball NY
            main, special = nums[:5], nums[5]
        elif len(nums) == 5 and special_col:        # formato Mega Millions NY
            main, special = nums, ints_in(row[special_col])[0]
        else:
            raise ValueError("formato de 'Winning Numbers' inesperado")
    else:                                            # formato normalizado
        main = [int(row[f"n{i}"]) for i in range(1, 6)]
        special_col = next(k for k in ("special", "mega_ball", "powerball", "mega ball") if k in row)
        special = int(row[special_col])

    if len(set(main)) != 5:
        raise ValueError("números principais repetidos")
    return Draw(when, tuple(sorted(main)), special)


def filter_era(draws: list[Draw], game: str, since: date | None, special_since: date | None):
    """Separa os sorteios válidos para a matriz atual (principais e especial)."""
    g = GAMES[game]
    ms = since or g["main_since"]
    ss = special_since or g["special_since"]
    main_draws = [d for d in draws if d.when >= ms and all(1 <= n <= g["main_max"] for n in d.main)]
    spec_draws = [d for d in draws if d.when >= ss and 1 <= d.special <= g["special_max"]]
    return main_draws, spec_draws, ms, ss


# ---------------------------------------------------------------------------
# 3. FUNÇÕES MATEMÁTICAS AUXILIARES
# ---------------------------------------------------------------------------
def norm_sf(z: float) -> float:
    """Cauda superior da normal padrão: P(Z > z)."""
    return 0.5 * math.erfc(z / math.sqrt(2))


def chi2_pvalue(x: float, k: int) -> float:
    """p-valor aproximado do qui-quadrado (aproximação de Wilson–Hilferty).
    Precisão suficiente para k >= 20, que é o nosso caso (k = 23..69)."""
    if k <= 0:
        return float("nan")
    z = ((x / k) ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k))
    return norm_sf(z)


def chi_square_uniform(counts: dict[int, int], universe: int) -> dict:
    """Testa se as frequências observadas são compatíveis com um sorteio uniforme."""
    total = sum(counts.get(n, 0) for n in range(1, universe + 1))
    expected = total / universe
    x2 = sum((counts.get(n, 0) - expected) ** 2 / expected for n in range(1, universe + 1))
    p = chi2_pvalue(x2, universe - 1)
    return {
        "chi2": round(x2, 2), "df": universe - 1, "p_value": round(p, 4),
        "interpretation": ("Sem evidência de desvio da aleatoriedade (p >= 0,05)."
                           if p >= 0.05 else
                           "Desvio estatisticamente detectável (p < 0,05) — investigar "
                           "mudança de regra/dados antes de concluir qualquer coisa."),
    }


def hypergeom_pmf(k: int, pop: int, successes: int, draws: int) -> float:
    """P(exatamente k 'sucessos') ao sortear `draws` de `pop` contendo `successes`."""
    return math.comb(successes, k) * math.comb(pop - successes, draws - k) / math.comb(pop, draws)


def percentile(sorted_vals: list[float], q: float) -> float:
    """Percentil com interpolação linear (q entre 0 e 100)."""
    if not sorted_vals:
        return float("nan")
    pos = (len(sorted_vals) - 1) * q / 100
    lo, hi = math.floor(pos), math.ceil(pos)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (pos - lo)


def jackpot_odds(game: str) -> int:
    g = GAMES[game]
    return math.comb(g["main_max"], PICK) * g["special_max"]


# ---------------------------------------------------------------------------
# 4. ANÁLISE ESTATÍSTICA
# ---------------------------------------------------------------------------
def frequency(draws: Iterable[Draw], universe: int, special: bool = False) -> Counter:
    c: Counter = Counter({n: 0 for n in range(1, universe + 1)})
    for d in draws:
        if special:
            c[d.special] += 1
        else:
            c.update(d.main)
    return c


def gaps(draws: list[Draw], universe: int, special: bool = False) -> dict[int, dict]:
    """Atraso atual (sorteios desde a última aparição), maior atraso e atraso médio."""
    last_seen: dict[int, int] = {}
    max_gap = {n: 0 for n in range(1, universe + 1)}
    gap_lists: dict[int, list[int]] = {n: [] for n in range(1, universe + 1)}
    for idx, d in enumerate(draws):
        hits = (d.special,) if special else d.main
        for n in hits:
            prev = last_seen.get(n, -1)
            g = idx - prev - 1 if prev >= 0 else idx
            if prev >= 0:
                gap_lists[n].append(g)
            max_gap[n] = max(max_gap[n], g)
            last_seen[n] = idx
    total = len(draws)
    out = {}
    for n in range(1, universe + 1):
        current = total - 1 - last_seen[n] if n in last_seen else total
        out[n] = {
            "current_gap": current,
            "max_gap": max(max_gap[n], current),
            "mean_gap": round(statistics.mean(gap_lists[n]), 1) if gap_lists[n] else None,
            "last_date": draws[last_seen[n]].when.isoformat() if n in last_seen else None,
        }
    return out


def analyze(draws_all: list[Draw], game: str, since=None, special_since=None, top: int = 10) -> dict:
    g = GAMES[game]
    N, S = g["main_max"], g["special_max"]
    main_draws, spec_draws, ms, ss = filter_era(draws_all, game, since, special_since)
    if not main_draws:
        raise SystemExit("Nenhum sorteio na era da matriz atual — verifique o CSV/datas.")
    n = len(main_draws)

    # --- A. Frequência histórica -------------------------------------------
    freq = frequency(main_draws, N)
    expected = n * PICK / N
    ranked = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    freq_table = [{"number": k, "count": v, "pct_draws": round(100 * v / n, 2),
                   "vs_expected_pct": round(100 * (v - expected) / expected, 1)} for k, v in ranked]

    # --- B. Janelas recentes -------------------------------------------------
    windows = {}
    for w in (10, 30, 50):
        sub = main_draws[-w:]
        fw = frequency(sub, N)
        hot = sorted(((k, v) for k, v in fw.items() if v > 0), key=lambda kv: (-kv[1], kv[0]))
        repeated = [k for k, v in hot if v >= 2]
        windows[str(w)] = {
            "draws": len(sub),
            "top": [{"number": k, "count": v} for k, v in hot[:top]],
            "repeated_numbers": repeated,
            "absent_numbers": sorted(k for k, v in fw.items() if v == 0),
            "expected_per_number": round(len(sub) * PICK / N, 2),
        }

    # --- C. Distribuição -----------------------------------------------------
    evens_universe = N // 2
    parity_obs = Counter(sum(1 for x in d.main if x % 2 == 0) for d in main_draws)
    parity = [{"evens": k, "odds": PICK - k, "observed": parity_obs.get(k, 0),
               "observed_pct": round(100 * parity_obs.get(k, 0) / n, 1),
               "theoretical_pct": round(100 * hypergeom_pmf(k, N, evens_universe, PICK), 1)}
              for k in range(PICK + 1)]

    low_max = N // 2   # MM: baixos 1–35 | PB: baixos 1–34
    low_obs = Counter(sum(1 for x in d.main if x <= low_max) for d in main_draws)
    lowhigh = [{"low": k, "high": PICK - k, "observed": low_obs.get(k, 0),
                "observed_pct": round(100 * low_obs.get(k, 0) / n, 1),
                "theoretical_pct": round(100 * hypergeom_pmf(k, N, low_max, PICK), 1)}
               for k in range(PICK + 1)]

    bands = [(lo, min(lo + 9, N)) for lo in range(1, N + 1, 10)]
    band_counts = Counter()
    for d in main_draws:
        for x in d.main:
            band_counts[(x - 1) // 10] += 1
    band_table = [{"band": f"{lo:02d}-{hi:02d}", "count": band_counts[i],
                   "pct": round(100 * band_counts[i] / (n * PICK), 1),
                   "theoretical_pct": round(100 * (hi - lo + 1) / N, 1)}
                  for i, (lo, hi) in enumerate(bands)]

    sums = sorted(sum(d.main) for d in main_draws)
    spreads = sorted(d.main[-1] - d.main[0] for d in main_draws)
    consec = sum(1 for d in main_draws if any(b - a == 1 for a, b in zip(d.main, d.main[1:])))
    repeats_prev = [len(set(a.main) & set(b.main)) for a, b in zip(main_draws, main_draws[1:])]
    sum_stats = {
        "mean": round(statistics.mean(sums), 1), "stdev": round(statistics.pstdev(sums), 1),
        "min": sums[0], "max": sums[-1],
        "p10": round(percentile(sums, 10)), "p25": round(percentile(sums, 25)),
        "median": round(percentile(sums, 50)), "p75": round(percentile(sums, 75)),
        "p90": round(percentile(sums, 90)),
        "theoretical_mean": PICK * (N + 1) / 2,
    }
    spacing = {
        "mean_spread": round(statistics.mean(spreads), 1),
        "median_spread": round(percentile(spreads, 50)),
        "pct_draws_with_consecutive": round(100 * consec / n, 1),
        "avg_repeats_from_previous_draw": round(statistics.mean(repeats_prev), 2) if repeats_prev else None,
        "theoretical_repeats_from_previous": round(PICK * PICK / N, 2),
    }

    # --- D. Combinações (pares/trincas/repetições exatas) ---------------------
    pairs, trios = Counter(), Counter()
    for d in main_draws:
        pairs.update(combinations(d.main, 2))
        trios.update(combinations(d.main, 3))
    exp_pair = n * (PICK * (PICK - 1)) / (N * (N - 1))
    exp_trio = n * math.comb(PICK, 3) / math.comb(N, 3)
    exact_dupes = [list(k) for k, v in Counter(d.main for d in main_draws).items() if v > 1]

    # --- E. Ausência ----------------------------------------------------------
    gap_main = gaps(main_draws, N)
    overdue = sorted(gap_main.items(), key=lambda kv: (-kv[1]["current_gap"], kv[0]))

    # --- Bola especial -------------------------------------------------------
    special_block = None
    if spec_draws:
        sf = frequency(spec_draws, S, special=True)
        sg = gaps(spec_draws, S, special=True)
        sranked = sorted(sf.items(), key=lambda kv: (-kv[1], kv[0]))
        special_block = {
            "name": g["special_name"], "era_start": ss.isoformat(), "draws": len(spec_draws),
            "expected_per_number": round(len(spec_draws) / S, 2),
            "most_frequent": [{"number": k, "count": v} for k, v in sranked[:top]],
            "least_frequent": [{"number": k, "count": v} for k, v in sranked[::-1][:top]],
            "last_30": [{"number": k, "count": v} for k, v in sorted(
                frequency(spec_draws[-30:], S, special=True).items(),
                key=lambda kv: (-kv[1], kv[0]))[:top] if v > 0],
            "overdue": [{"number": k, **v} for k, v in sorted(
                sg.items(), key=lambda kv: (-kv[1]["current_gap"], kv[0]))[:top]],
            "uniformity_test": chi_square_uniform(sf, S),
            "small_sample_warning": len(spec_draws) < 10 * S,
        }

    last = main_draws[-1]
    return {
        "game": g["name"],
        "rules": {"main": f"5 de 1–{N}", "special": f"1 de 1–{S} ({g['special_name']})",
                  "jackpot_odds": f"1 em {jackpot_odds(game):,}".replace(",", "."),
                  "price_usd": g["price_usd"], "draw_days": g["draw_days"], "notes": g["notes"]},
        "data": {"main_era_start": ms.isoformat(), "draws_analyzed": n,
                 "first_draw": main_draws[0].when.isoformat(),
                 "last_draw": last.when.isoformat(),
                 "last_result": {"main": list(last.main), "special": last.special},
                 "total_rows_in_file": len(draws_all)},
        "frequency": {"expected_per_number": round(expected, 2),
                      "most_frequent": freq_table[:top],
                      "least_frequent": freq_table[::-1][:top],
                      "uniformity_test": chi_square_uniform(freq, N)},
        "recent_windows": windows,
        "distribution": {"parity": parity, "low_high": lowhigh, "low_range": f"1–{low_max}",
                         "bands": band_table, "sum": sum_stats, "spacing": spacing},
        "combinations": {
            "expected_count_per_pair": round(exp_pair, 2),
            "top_pairs": [{"pair": list(k), "count": v} for k, v in pairs.most_common(top)],
            "expected_count_per_trio": round(exp_trio, 3),
            "top_trios": [{"trio": list(k), "count": v} for k, v in trios.most_common(5) if v >= 2],
            "exact_repeated_combinations": exact_dupes,
        },
        "absence": {"theoretical_mean_gap": round(N / PICK - 1, 1),
                    "most_overdue": [{"number": k, **v} for k, v in overdue[:top]]},
        "special": special_block,
        "disclaimer": "Frequências passadas não alteram probabilidades futuras. "
                      f"Qualquer combinação tem chance de {('1 em ' + format(jackpot_odds(game), ',')).replace(',', '.')} "
                      "de acertar o jackpot.",
    }


# ---------------------------------------------------------------------------
# 5. AVALIAÇÃO DE COMBINAÇÕES
# ---------------------------------------------------------------------------
def parse_ticket(text: str, game: str) -> tuple[tuple[int, ...], int]:
    """Aceita "5 12 33 48 61 | 7", "05-12-33-48-61 MB 07", "5,12,33,48,61,7"."""
    g = GAMES[game]
    nums = ints_in(text)
    if len(nums) != 6:
        raise SystemExit(f"Bilhete inválido ({text!r}): informe 5 números + 1 {g['special_name']}.")
    main, special = nums[:5], nums[5]
    errors = validate(main, special, game)
    if errors:
        raise SystemExit(f"Bilhete inválido ({text!r}): " + "; ".join(errors))
    return tuple(sorted(main)), special


def validate(main: list[int] | tuple[int, ...], special: int, game: str) -> list[str]:
    """Valida contra as regras oficiais vigentes. Lista vazia = válido."""
    g = GAMES[game]
    errs = []
    if len(main) != PICK:
        errs.append(f"são necessários exatamente {PICK} números principais")
    if len(set(main)) != len(main):
        dup = sorted(n for n, c in Counter(main).items() if c > 1)
        errs.append(f"números duplicados: {dup}")
    out = [n for n in main if not 1 <= n <= g["main_max"]]
    if out:
        errs.append(f"fora da faixa 1–{g['main_max']}: {out}")
    if not 1 <= special <= g["special_max"]:
        errs.append(f"{g['special_name']} fora da faixa 1–{g['special_max']}: {special}")
    return errs


def popularity_flags(main: tuple[int, ...]) -> list[str]:
    """Heurística de 'números populares'. NÃO muda a chance de ganhar; reduz o risco
    de DIVIDIR o jackpot com muitas pessoas (impacta o valor esperado do prêmio)."""
    flags = []
    if all(n <= 31 for n in main):
        flags.append("todos ≤ 31 (padrão 'datas de aniversário' — muito jogado)")
    diffs = {b - a for a, b in zip(main, main[1:])}
    if len(diffs) == 1:
        flags.append("progressão aritmética (padrão visual muito jogado)")
    run = max_run(main)
    if run >= 3:
        flags.append(f"{run} números consecutivos")
    if all(n % 7 == 0 for n in main) or all(n % 5 == 0 for n in main):
        flags.append("todos múltiplos de 5 ou 7")
    if len({(n - 1) // 10 for n in main}) == 1:
        flags.append("todos na mesma dezena")
    return flags


def max_run(main: tuple[int, ...]) -> int:
    best = cur = 1
    for a, b in zip(main, main[1:]):
        cur = cur + 1 if b - a == 1 else 1
        best = max(best, cur)
    return best


def evaluate_ticket(main, special, game, main_draws: list[Draw] | None, stats: dict | None) -> dict:
    g = GAMES[game]
    N = g["main_max"]
    s = sum(main)
    res = {
        "ticket": {"main": list(main), "special": special},
        "evens_odds": f"{sum(1 for x in main if x % 2 == 0)}/{sum(1 for x in main if x % 2)}",
        "low_high": f"{sum(1 for x in main if x <= N // 2)}/{sum(1 for x in main if x > N // 2)}",
        "sum": s,
        "spread": main[-1] - main[0],
        "bands_used": len({(n - 1) // 10 for n in main}),
        "max_consecutive_run": max_run(main),
        "popularity_flags": popularity_flags(main),
        "jackpot_probability": f"1 em {jackpot_odds(game):,}".replace(",", "."),
    }
    if main_draws:
        sums = sorted(sum(d.main) for d in main_draws)
        below = sum(1 for x in sums if x <= s)
        res["sum_percentile"] = round(100 * below / len(sums), 1)
        best = max(main_draws, key=lambda d: len(set(d.main) & set(main)))
        res["best_historical_match"] = {
            "hits": len(set(best.main) & set(main)), "date": best.when.isoformat(),
            "draw": list(best.main)}
        res["exact_combination_drawn_before"] = any(d.main == tuple(main) for d in main_draws)
        last = main_draws[-1]
        res["overlap_with_last_draw"] = sorted(set(last.main) & set(main))
    if stats:
        hot30 = {x["number"] for x in stats["recent_windows"]["30"]["top"]}
        top_all = {x["number"] for x in stats["frequency"]["most_frequent"]}
        res["in_top_frequency_all_time"] = sorted(set(main) & top_all)
        res["in_top_last_30"] = sorted(set(main) & hot30)
    return res


# ---------------------------------------------------------------------------
# 6. GERADOR DE COMBINAÇÕES
# ---------------------------------------------------------------------------
def balanced_ok(main: tuple[int, ...], game: str, sum_lo: float, sum_hi: float) -> bool:
    """Filtro 'equilibrado': paridade 2/3 ou 3/2, baixos/altos 2/3 ou 3/2, soma no
    intervalo interquartil histórico, ≥4 faixas de dezena, sem trinca consecutiva."""
    N = GAMES[game]["main_max"]
    ev = sum(1 for x in main if x % 2 == 0)
    lo = sum(1 for x in main if x <= N // 2)
    return (ev in (2, 3) and lo in (2, 3) and sum_lo <= sum(main) <= sum_hi
            and len({(n - 1) // 10 for n in main}) >= 4 and max_run(main) <= 2)


def weighted_sample(rng: random.Random, weights: dict[int, float], k: int,
                    exclude: set[int]) -> list[int]:
    """Amostragem ponderada SEM reposição."""
    pool = {n: w for n, w in weights.items() if n not in exclude and w > 0}
    chosen = []
    for _ in range(k):
        total = sum(pool.values())
        r = rng.uniform(0, total)
        acc = 0.0
        for n, w in pool.items():
            acc += w
            if acc >= r:
                chosen.append(n)
                del pool[n]
                break
    return chosen


def generate(game: str, main_draws: list[Draw], spec_draws: list[Draw], seed: int | None,
             tickets: int, exclude: set[int], avoid_popular: bool) -> dict:
    g = GAMES[game]
    N, S = g["main_max"], g["special_max"]
    rng = random.Random(seed)
    used_main: set[int] = set()
    used_special: set[int] = set()

    if main_draws:
        freq = frequency(main_draws, N)
        sums = sorted(sum(d.main) for d in main_draws)
        sum_lo, sum_hi = percentile(sums, 25), percentile(sums, 75)
    else:   # sem histórico: pesos iguais e soma teórica ± 1 desvio aproximado
        freq = Counter({n: 1 for n in range(1, N + 1)})
        mu = PICK * (N + 1) / 2
        sum_lo, sum_hi = mu - 0.67 * 45, mu + 0.67 * 45
    sfreq = frequency(spec_draws, S, special=True) if spec_draws else Counter({n: 1 for n in range(1, S + 1)})

    def pick_special(weights: Counter, prefer_new: bool = True) -> int:
        cands = [n for n in range(1, S + 1) if not (prefer_new and n in used_special)] or list(range(1, S + 1))
        w = {n: max(weights.get(n, 0), 0.5) for n in cands}
        return weighted_sample(rng, w, 1, set())[0]

    def accept(main: tuple[int, ...]) -> bool:
        return not (avoid_popular and popularity_flags(main))

    results = []

    # 1) ESTATÍSTICA — peso proporcional à frequência histórica (na era atual),
    #    com piso de equilíbrio mínimo para não gerar combinações degeneradas.
    for _ in range(5000):
        weights = {n: (freq[n] + 1) ** 2 for n in range(1, N + 1)}   # realça os mais frequentes
        main = tuple(sorted(weighted_sample(rng, weights, PICK, exclude)))
        if max_run(main) <= 2 and accept(main):
            break
    sp = pick_special(Counter({n: (c + 1) ** 2 for n, c in sfreq.items()}))
    results.append(("Estatística", main, sp,
                    "Sorteio ponderado pela frequência histórica (peso = (freq+1)²) na matriz atual; "
                    "Bola especial ponderada pela própria frequência."))
    used_main |= set(main)
    used_special.add(sp)

    # 2) EQUILIBRADA — uniforme, filtrada por paridade, baixos/altos, soma IQR e faixas.
    for _ in range(20000):
        main = tuple(sorted(rng.sample([n for n in range(1, N + 1) if n not in exclude], PICK)))
        if balanced_ok(main, game, sum_lo, sum_hi) and accept(main) and len(set(main) & used_main) <= 1:
            break
    sp = pick_special(Counter({n: 1 for n in range(1, S + 1)}))
    results.append(("Equilibrada", main, sp,
                    f"Paridade 2/3 ou 3/2, baixos/altos 2/3 ou 3/2, soma entre P25 e P75 "
                    f"históricos ({sum_lo:.0f}–{sum_hi:.0f}), ≥4 faixas de dezena, sem trinca consecutiva."))
    used_main |= set(main)
    used_special.add(sp)

    # 3+) DIVERSIFICADA — cobertura: prioriza números ainda NÃO usados nas apostas
    #     anteriores (sobreposição mínima), mantendo o filtro de equilíbrio e,
    #     por padrão, evitando números 'populares' para reduzir risco de rateio.
    for i in range(max(1, tickets - 2)):
        best, best_overlap = None, 99
        for _ in range(20000):
            fresh = [n for n in range(1, N + 1) if n not in used_main and n not in exclude]
            pool = fresh if len(fresh) >= PICK else [n for n in range(1, N + 1) if n not in exclude]
            main = tuple(sorted(rng.sample(pool, PICK)))
            ov = len(set(main) & used_main)
            if balanced_ok(main, game, sum_lo, sum_hi) and not popularity_flags(main) and ov <= best_overlap:
                best, best_overlap = main, ov
                if ov == 0:
                    break
        main = best or main
        sp = pick_special(Counter({n: 1 for n in range(1, S + 1)}))
        results.append((f"Diversificada{'' if tickets <= 3 else f' #{i + 1}'}", main, sp,
                        "Minimiza repetição de números entre as apostas (cobertura), mantém o equilíbrio "
                        "e evita padrões populares (reduz chance de dividir o prêmio)."))
        used_main |= set(main)
        used_special.add(sp)

    out = []
    for label, main, sp, why in results:
        errs = validate(main, sp, game)
        assert not errs, errs   # nunca entregar combinação inválida
        out.append({"strategy": label, "main": list(main), "special": sp, "criteria": why,
                    "profile": evaluate_ticket(main, sp, game, main_draws, None)})
    total_cost = round(len(out) * g["price_usd"], 2)
    return {"game": g["name"], "special_name": g["special_name"], "seed": seed,
            "combinations": out, "cost_usd": total_cost,
            "unique_main_numbers_covered": len({n for c in out for n in c["main"]}),
            "disclaimer": "Todas as combinações têm a mesma probabilidade de acerto. "
                          "As estratégias organizam escolhas; não aumentam a chance."}


# ---------------------------------------------------------------------------
# 7. CONFERÊNCIA DE BILHETE
# ---------------------------------------------------------------------------
TIERS = [  # (acertos principais, acertou especial?) -> faixa
    ((5, True), "JACKPOT"), ((5, False), "2º prêmio (5 números)"),
    ((4, True), "4 + bola especial"), ((4, False), "4 números"),
    ((3, True), "3 + bola especial"), ((3, False), "3 números"),
    ((2, True), "2 + bola especial"), ((1, True), "1 + bola especial"),
    ((0, True), "Somente a bola especial"),
]


def check_ticket(ticket, draw) -> dict:
    hits = sorted(set(ticket[0]) & set(draw[0]))
    sp_hit = ticket[1] == draw[1]
    tier = dict(TIERS).get((len(hits), sp_hit))
    return {"matched_main": hits, "special_hit": sp_hit,
            "tier": tier or "Sem prêmio",
            "note": "Valores variam (multiplicador, estado, jackpot/rateio). Confirme no site "
                    "oficial ou em um revendedor autorizado antes de descartar o bilhete."}


# ---------------------------------------------------------------------------
# 8. SAÍDA EM MARKDOWN (relatório pronto para o usuário)
# ---------------------------------------------------------------------------
def f2(n: int) -> str:
    return f"{n:02d}"


def md_analysis(r: dict) -> str:
    L = []
    d, fr, rw, ds = r["data"], r["frequency"], r["recent_windows"], r["distribution"]
    L.append(f"## {r['game'].upper()} — Relatório Estatístico\n")
    L.append(f"- **Regras vigentes:** {r['rules']['main']} + {r['rules']['special']}")
    L.append(f"- **Chance do jackpot:** {r['rules']['jackpot_odds']} · **Preço:** US$ {r['rules']['price_usd']:.2f}")
    L.append(f"- **Sorteios:** {r['rules']['draw_days']}")
    L.append(f"- **Base:** {d['draws_analyzed']} sorteios de {d['first_draw']} a {d['last_draw']} "
             f"(matriz atual desde {d['main_era_start']})")
    lr = d["last_result"]
    L.append(f"- **Último resultado no arquivo:** {' - '.join(map(f2, lr['main']))} | "
             f"{r['special']['name'] if r['special'] else 'Especial'}: {f2(lr['special'])}\n")

    L.append(f"### Frequência histórica (esperado por número: {fr['expected_per_number']})\n")
    L.append("| # | Mais sorteados | Vezes | vs esperado | Menos sorteados | Vezes | vs esperado |")
    L.append("|---|---|---|---|---|---|---|")
    for i, (a, b) in enumerate(zip(fr["most_frequent"], fr["least_frequent"]), 1):
        L.append(f"| {i} | **{f2(a['number'])}** | {a['count']} | {a['vs_expected_pct']:+.1f}% | "
                 f"**{f2(b['number'])}** | {b['count']} | {b['vs_expected_pct']:+.1f}% |")
    ut = fr["uniformity_test"]
    L.append(f"\n> Teste qui-quadrado: χ²={ut['chi2']} (gl={ut['df']}), p={ut['p_value']} → {ut['interpretation']}\n")

    L.append("### Concursos recentes\n")
    L.append("| Janela | Mais presentes | Repetidos (≥2x) | Ausentes |")
    L.append("|---|---|---|---|")
    for w, blk in rw.items():
        top = ", ".join(f"{f2(x['number'])}({x['count']})" for x in blk["top"][:8])
        rep = ", ".join(map(f2, blk["repeated_numbers"][:12])) or "—"
        L.append(f"| Últimos {w} | {top} | {rep} | {len(blk['absent_numbers'])} números |")

    L.append("\n### Números há mais tempo sem aparecer\n")
    L.append(f"Atraso médio teórico: {r['absence']['theoretical_mean_gap']} sorteios.\n")
    L.append("| Número | Atraso atual | Maior atraso | Atraso médio | Última vez |")
    L.append("|---|---|---|---|---|")
    for x in r["absence"]["most_overdue"]:
        L.append(f"| **{f2(x['number'])}** | {x['current_gap']} | {x['max_gap']} | {x['mean_gap']} | {x['last_date']} |")
    L.append("\n> Atraso NÃO aumenta a chance do número sair (sorteios são independentes).\n")

    L.append("### Distribuição\n")
    L.append("| Pares/Ímpares | Observado | Teórico |   | Baixos/Altos (" + ds["low_range"] + ") | Observado | Teórico |")
    L.append("|---|---|---|---|---|---|---|")
    for p, q in zip(ds["parity"], ds["low_high"]):
        L.append(f"| {p['evens']}/{p['odds']} | {p['observed_pct']}% | {p['theoretical_pct']}% | | "
                 f"{q['low']}/{q['high']} | {q['observed_pct']}% | {q['theoretical_pct']}% |")
    sm, sp = ds["sum"], ds["spacing"]
    L.append(f"\n- **Soma das dezenas:** média {sm['mean']} (teórica {sm['theoretical_mean']}), "
             f"faixa central P25–P75 = {sm['p25']}–{sm['p75']}, P10–P90 = {sm['p10']}–{sm['p90']}")
    L.append(f"- **Amplitude (maior − menor):** média {sp['mean_spread']}")
    L.append(f"- **Sorteios com ao menos 1 par consecutivo:** {sp['pct_draws_with_consecutive']}%")
    L.append(f"- **Repetições do sorteio anterior:** média {sp['avg_repeats_from_previous_draw']} "
             f"(teórica {sp['theoretical_repeats_from_previous']})")
    L.append("- **Faixas:** " + " · ".join(f"{b['band']}: {b['pct']}% (teórico {b['theoretical_pct']}%)" for b in ds["bands"]))

    cb = r["combinations"]
    L.append(f"\n### Pares e trincas (esperado por par: {cb['expected_count_per_pair']})\n")
    L.append("- **Pares mais recorrentes:** " + ", ".join(
        f"{f2(p['pair'][0])}-{f2(p['pair'][1])} ({p['count']}x)" for p in cb["top_pairs"]))
    if cb["top_trios"]:
        L.append("- **Trincas recorrentes:** " + ", ".join(
            "-".join(map(f2, t["trio"])) + f" ({t['count']}x)" for t in cb["top_trios"]))
    L.append(f"- **Combinações de 5 repetidas na história:** {len(cb['exact_repeated_combinations'])}")

    s = r["special"]
    if s:
        L.append(f"\n### {s['name']} (desde {s['era_start']}, {s['draws']} sorteios; esperado {s['expected_per_number']}/número)\n")
        L.append("- **Mais frequentes:** " + ", ".join(f"{f2(x['number'])}({x['count']})" for x in s["most_frequent"]))
        L.append("- **Menos frequentes:** " + ", ".join(f"{f2(x['number'])}({x['count']})" for x in s["least_frequent"]))
        L.append("- **Últimos 30:** " + (", ".join(f"{f2(x['number'])}({x['count']})" for x in s["last_30"]) or "—"))
        L.append("- **Mais atrasadas:** " + ", ".join(f"{f2(x['number'])}({x['current_gap']})" for x in s["overdue"]))
        if s["small_sample_warning"]:
            L.append(f"\n> ⚠️ Amostra pequena para a {s['name']} na matriz atual — frequências muito instáveis.")
    L.append(f"\n---\n*{r['disclaimer']}*")
    return "\n".join(L)


def md_generate(r: dict) -> str:
    L = [f"## {r['game'].upper()} — Combinações sugeridas\n"]
    for c in r["combinations"]:
        p = c["profile"]
        L.append(f"**Combinação — {c['strategy']}**\n")
        L.append("```")
        L.append(f"Números principais: {' - '.join(map(f2, c['main']))}")
        L.append(f"{r['special_name']}: {f2(c['special'])}")
        L.append("```")
        L.append(f"- Critério: {c['criteria']}")
        L.append(f"- Perfil: pares/ímpares {p['evens_odds']} · baixos/altos {p['low_high']} · "
                 f"soma {p['sum']}" + (f" (percentil {p['sum_percentile']})" if 'sum_percentile' in p else "")
                 + f" · {p['bands_used']} faixas\n")
    L.append(f"**Custo total:** US$ {r['cost_usd']:.2f} · **Números distintos cobertos:** "
             f"{r['unique_main_numbers_covered']} · seed={r['seed']}")
    L.append(f"\n*{r['disclaimer']}*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# 9. CLI
# ---------------------------------------------------------------------------
def emit(obj, fmt: str, md_fn=None):
    if fmt == "md" and md_fn:
        print(md_fn(obj))
    else:
        print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def main(argv=None):
    ap = argparse.ArgumentParser(description="LOTTERY INTELLIGENCE AI — motor estatístico")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, need_csv=True):
        p.add_argument("--game", choices=["mm", "pb"], required=True, help="mm=Mega Millions, pb=Powerball")
        p.add_argument("--csv", nargs="+", required=need_csv,
                       help="um ou mais CSVs (oficial + extras); datas duplicadas são unificadas")
        p.add_argument("--since", help="início da era p/ números principais (AAAA-MM-DD)")
        p.add_argument("--special-since", help="início da era p/ bola especial (AAAA-MM-DD)")
        p.add_argument("--format", choices=["json", "md"], default="md")

    p = sub.add_parser("analyze"); common(p)
    p.add_argument("--top", type=int, default=10)

    p = sub.add_parser("generate"); common(p, need_csv=False)
    p.add_argument("--seed", type=int, default=None, help="semente p/ reprodutibilidade")
    p.add_argument("--tickets", type=int, default=3, help="nº de apostas (≥3)")
    p.add_argument("--exclude", default="", help="números a evitar (ex.: '7 13 22')")
    p.add_argument("--allow-popular", action="store_true",
                   help="não filtra padrões populares nas estratégias 1 e 2")
    p.add_argument("--budget", type=float, default=None, help="orçamento em US$ (limita nº de apostas)")

    p = sub.add_parser("evaluate"); common(p, need_csv=False)
    p.add_argument("--ticket", action="append", required=True, help='"5 12 33 48 61 | 7" (repetível)')

    p = sub.add_parser("check")
    p.add_argument("--game", choices=["mm", "pb"], required=True)
    p.add_argument("--ticket", action="append", required=True)
    p.add_argument("--draw", required=True, help='resultado oficial "n1 n2 n3 n4 n5 | especial"')

    p = sub.add_parser("rules")
    p.add_argument("--game", choices=["mm", "pb"], required=True)

    a = ap.parse_args(argv)
    since = parse_date(a.since) if getattr(a, "since", None) else None
    ssince = parse_date(a.special_since) if getattr(a, "special_since", None) else None

    if a.cmd == "rules":
        g = dict(GAMES[a.game]); g["jackpot_odds"] = jackpot_odds(a.game)
        print(json.dumps(g, ensure_ascii=False, indent=2, default=str)); return

    if a.cmd == "check":
        draw = parse_ticket(a.draw, a.game)
        print(json.dumps([{"ticket": t, **check_ticket(parse_ticket(t, a.game), draw)} for t in a.ticket],
                         ensure_ascii=False, indent=2)); return

    draws, warns = (load_draws(a.csv, a.game) if a.csv else ([], []))
    for w in warns[:20]:
        print(f"[aviso] {w}", file=sys.stderr)
    main_draws, spec_draws = (filter_era(draws, a.game, since, ssince)[:2] if draws else ([], []))

    if a.cmd == "analyze":
        emit(analyze(draws, a.game, since, ssince, a.top), a.format, md_analysis)
    elif a.cmd == "generate":
        n = max(3, a.tickets)
        if a.budget is not None:
            afford = int(a.budget // GAMES[a.game]["price_usd"])
            if afford < 1:
                raise SystemExit(f"Orçamento de US$ {a.budget:.2f} não cobre 1 aposta "
                                 f"(US$ {GAMES[a.game]['price_usd']:.2f}).")
            n = min(n, afford) if afford >= 3 else afford
        if not draws:
            print("[aviso] sem CSV: gerando sem base histórica (pesos iguais).", file=sys.stderr)
        res = generate(a.game, main_draws, spec_draws, a.seed, n, set(ints_in(a.exclude)),
                       avoid_popular=not a.allow_popular)
        res["combinations"] = res["combinations"][:n]
        res["cost_usd"] = round(len(res["combinations"]) * GAMES[a.game]["price_usd"], 2)
        emit(res, a.format, md_generate)
    elif a.cmd == "evaluate":
        stats = analyze(draws, a.game, since, ssince) if draws else None
        out = [evaluate_ticket(*parse_ticket(t, a.game), a.game, main_draws or None, stats) for t in a.ticket]
        print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

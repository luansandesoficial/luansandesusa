# Fontes de dados e protocolo de atualização

## Fontes (da melhor para a pior)

| # | Fonte | Conteúdo | Formato | Observação |
|---|---|---|---|---|
| 1 | **NY Open Data** (NYS Gaming Commission) | Histórico completo | CSV/JSON (API Socrata) | Oficial, gratuito, sem chave. Melhor custo-benefício |
| 2 | **megamillions.com / powerball.com** | Último resultado, próximo sorteio, jackpot, regras | HTML | Fonte de verdade para conferência |
| 3 | Sites de loterias estaduais (ex.: Texas, Califórnia) | Históricos alternativos | CSV/HTML | Bom backup |
| 4 | Arquivo enviado pelo usuário | Qualquer | CSV/XLSX | Confirmar origem com o usuário |
| ✗ | Blogs/sites de "previsão" | — | — | **Nunca** usar como fonte de resultados |

## URLs

```text
Powerball (CSV):     https://data.ny.gov/api/views/d6yy-54nr/rows.csv?accessType=DOWNLOAD
Mega Millions (CSV): https://data.ny.gov/api/views/5xaw-6ayf/rows.csv?accessType=DOWNLOAD
Powerball (JSON):    https://data.ny.gov/resource/d6yy-54nr.json?$order=draw_date%20DESC&$limit=60
Mega Millions (JSON):https://data.ny.gov/resource/5xaw-6ayf.json?$order=draw_date%20DESC&$limit=60
Oficial MM:          https://www.megamillions.com/Winning-Numbers.aspx
Oficial PB:          https://www.powerball.com/previous-results
```

## Protocolo

1. Baixar os CSVs (`curl -L -o pb.csv "<url>"`). Se o ambiente não tiver rede para esses hosts, tentar a
   ferramenta de busca/leitura web; se nada funcionar, **declarar a limitação**.
2. Rodar `analyze` e ler `data.last_draw`.
3. Comparar com o último sorteio do site oficial (considerar o calendário: um sorteio de hoje à noite ainda
   não consta).
4. Se faltar sorteio, criar `extra.csv` normalizado e concatenar:
   ```csv
   date,n1,n2,n3,n4,n5,special
   2026-11-18,4,15,27,39,61,9
   ```
   e rode com os dois arquivos: `analyze --game pb --csv pb.csv extra.csv` (o motor mescla, ordena e
   alerta se a mesma data tiver números diferentes).
5. Citar no relatório: **fonte**, **data/hora da consulta** e **último sorteio incluído**.

## Formatos aceitos pelo motor
- NY Powerball: `Draw Date,Winning Numbers,Multiplier` (6 números; último = Powerball)
- NY Mega Millions: `Draw Date,Winning Numbers,Mega Ball,Multiplier`
- Normalizado: `date,n1,n2,n3,n4,n5,special` (aceita `mega_ball`/`powerball` no lugar de `special`)
- Datas: `MM/DD/AAAA`, `AAAA-MM-DD`, ISO com hora, `DD/MM/AAAA`.

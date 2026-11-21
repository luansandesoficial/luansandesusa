# REVIEW — Lumi, a baleia que acende as estrelas do mar

## Escolhas criativas
- Usei a história do pedido sem desenvolver outros roteiros (o pedido já trazia a história e pedia o arquivo).
- Livro ilustrado em vetor: contorno #283272, água índigo→petróleo, lua e areia. Os únicos brilhos são as estrelas acesas e as bolhas de luz.
- As cenas trocam com um "piscar" (escurece 60% e reabre), como olhos de sono. O final escurece só 30%.
- Legenda palavra por palavra em Nunito 900 72 px. A palavra ativa fica dourada e as palavras-chave (Lumi, luz, estrela-do-mar, brilhou) continuam douradas.

## Medido
- `check`: 0 erros. O aviso `timeline_track_too_dense` foi mantido de propósito, porque todas as legendas ficam num só host para virarem uma faixa única no Studio.
- Legenda dentro da área segura de 9:16 (borda inferior em y ≤ 1248, x 120–780). Contraste aprovado em 22/22 amostras.
- Áudio do MP4: 8 efeitos com picos em 0.35, 8.62, 11.07, 15.62, 16.62, 17.61, 20.43 e 25.73 s, ou seja, 1 frame depois de cada ação.
- Loudness −21.9 LUFS, pico −7.9 dBTP, sem clipping. Está mais baixo que o padrão de redes (−14 a −16) de propósito, para ser um som de ninar. Os sons foram medidos, não ouvidos.
- MP4 em 1080×1920, 30 fps, 30 s.

## Não verificado
- Ninguém ouviu o resultado.
- Não tem música: sem login na HeyGen não há acesso ao catálogo, e o Openverse estava bloqueado pela rede. Os efeitos são da biblioteca embutida (licença Pixabay).

## Cena mais fraca
- S1, frame 0: a baleia ainda está entrando e a legenda só aparece em 0.2 s. Com mais tempo, deixaria uma estrela já acesa como gancho da thumbnail.
- Uma narração em PT-BR combinaria com a legenda palavra por palavra.

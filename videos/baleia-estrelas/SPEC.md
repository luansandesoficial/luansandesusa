# SPEC — "Lumi, a baleia que acende as estrelas do mar"

GOAL:    a criança termina calma e sonolenta; a última imagem é a baleia dormindo num mar de estrelas acesas.
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps (Reels / TikTok / Shorts)
TIME:    30 s x 30 fps = 900 frames. Sem música (sem login HeyGen); efeitos suaves por cena.

LOOK:    livro ilustrado à noite, vetor com contorno.
         água: degradê #2a3577 (topo) → #163e66 → #0f3347 (fundo); areia #2c4a5e com dunas #365a6e.
         lua #fff3c4 com halo 0.35; raios de luar #fff3c4 a 7–10% de opacidade.
         baleia "Lumi": corpo #7d9be0, barriga #d3ddf7, contorno #283272 a 6 px, bochecha #f4a6b8 a 70%.
         estrela-do-mar apagada #3e5672; acesa #ffd36e com miolo #fff1c2 e halo radial #ffd36e (o brilho é a história, não decoração).
         grão de papel 5% sobre tudo.
         legenda: Nunito 900, 72 px, creme #fff6e0; palavra ativa #ffd36e; sombra 0 4px 18px rgba(8,12,40,.85).
OBJECTS: baleia com olho (aberto/fechado), sorriso, bochecha, nadadeira, cauda com barbatana e respiradouro;
         estrela-do-mar de 5 pontas arredondadas; bolhas de luz (círculo com brilho e reflexo); algas; lua.
MOTION:  chegada expo.out / power3.out; câmera power2.inOut; saída power3.in.
         cauda e nadadeira: atuação (rotação 6–12°, períodos diferentes, nunca em uníssono).
         palavra da legenda: blur 6→0 + opacidade + 12 px de subida em 0.3 s, 0.42 s entre palavras.
         transição entre cenas: "piscar" — escurece 60% em 0.3 s e reabre em 0.45 s (os olhos da criança).
SHOTS:
  S1 0–5    plano aberto, Lumi entra pela direita sob o luar; câmera desce 120 px. "Era uma vez, no fundo do mar escuro…"   som: whoosh suave 0.3 s
  S2 5–10   close: Lumi pisca, sorri, a bochecha cora, uma bolhinha sobe e estoura.  "Lá vivia Lumi, uma baleia muito gentil."  som: pop na bolha
  S3 10–15  Lumi se encolhe (antecipação) e sopra 7 bolhas de luz pelo respiradouro. "Toda noite, ela soprava bolhas de luz."  som: sparkle no sopro
  S4 15–20  fundo do mar: três bolhas descem e cada uma acende uma estrela-do-mar.  "Cada bolha acendia uma estrela-do-mar."  som: chime, pop, click suave (um por estrela)
  S5 20–25  plano aberto: 14 estrelas acendem em onda da esquerda p/ direita, a água esquenta. "E o mar inteiro brilhou, bem quentinho." som: sparkle na onda
  S6 25–30  Lumi dorme na areia, "z" em bolhas, estrelas acesas em volta, lua no alto. "Boa noite, Lumi. Durma bem." (segura ≥ 2.5 s) som: chime
BANNED:  vazio escuro com elementos pequenos no meio; partículas decorativas; neon/bloom genérico; tudo entrando com fade+slide;
         texto se movendo enquanto é lido; logo no canto; cortes secos entre mundos.
QA:      t=0 (thumbnail já mostra a baleia), 6.4 (piscada), 11.3 (sopro), 16.7 (2ª estrela acesa), 22.0 (onda), 28.5 (final).

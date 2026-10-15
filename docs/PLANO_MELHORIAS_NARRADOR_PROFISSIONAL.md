# Plano de melhorias — Narrador de Futebol IA

## Diagnóstico direto

O projeto já tem uma boa fundação: overlay para OBS, acompanhamento por ESPN/API-Football, fila de áudio com prioridade para gols, narração local com Piper/Kokoro, escalações, fotos, contexto de clubes e uma IA local que reorganiza fatos sem permitir que o modelo invente números. Isso aparece no `README.md`, em `backend/narration_channel.py`, `backend/local_brain.py` e `backend/local_voice.py`.

A principal diferença entre o estado atual e um narrador profissional é que hoje o sistema recebe **eventos publicados pela fonte**. Ele não interpreta diretamente o vídeo da partida. Portanto, consegue narrar gol, cartão, substituição, placar e panoramas, mas não consegue garantir uma narração lance a lance de cada passe, drible, pressão ou defesa apenas com o feed atual.

## O que deve ser melhorado primeiro

### 1. Criar uma camada de eventos ao vivo com prioridade

O programa já possui uma fila e dá prioridade a gols em `local_voice.py`. O próximo passo é transformar isso em um sistema de prioridade explícito:

- **P0 — imediato:** gol, pênalti, expulsão, VAR, fim de jogo e lesão grave.
- **P1 — curto:** defesa difícil, chance clara, substituição e cartão amarelo.
- **P2 — normal:** escanteio, falta perigosa, impedimento e ataque promissor.
- **P3 — panorama:** posse, estatísticas, escalação e comentário periódico.
- **P4 — interação:** mensagens do chat, agradecimentos e chamadas de inscrição.

Quando chegar um gol, a fila deve interromper ou adiar um panorama. Também deve remover eventos repetidos pelo identificador do evento, minuto, jogador e texto normalizado. Isso evita a repetição que costuma deixar a voz artificial.

Cada evento deveria carregar algo parecido com:

```json
{
  "id": "espn-123-67-goal",
  "kind": "goal",
  "priority": 0,
  "minute": "67+2",
  "team": "Flamengo",
  "player": "Pedro",
  "facts": ["Gol do Flamengo aos 67 minutos e 2 segundos"],
  "created_at": "...",
  "expires_at": "..."
}
```

### 2. Separar fato, roteiro e voz

A separação já começou em `local_brain.py`, que seleciona fatos e rejeita texto inventado. Ela deve ser mantida e ampliada:

1. **Fonte:** fornece os dados brutos.
2. **Normalizador:** converte os dados para português e identifica o tipo do lance.
3. **Roteirista:** escolhe a estrutura da frase e o tom, sem criar números ou jogadores.
4. **Pronúncia:** troca nomes difíceis por uma forma fonética apenas para o TTS.
5. **Síntese:** gera o áudio.
6. **Player:** toca o áudio no OBS e informa o estado da fila.

Nunca deixe o modelo de linguagem receber autorização para inventar estatísticas. O texto pode ficar mais emocionante, mas o placar, minuto, nome, time e tipo do lance devem vir exclusivamente dos dados confirmados.

### 3. Melhorar os textos de narração

Hoje o projeto usa aberturas curtas e comentários factuais. Para soar profissional, use modelos diferentes por situação, com frases curtas e informação progressiva.

**Gol:**

> “Olha o gol! O Flamengo recupera a bola no ataque, Pedro recebe na área e bate cruzado. A bola morre no canto! Flamengo 1, Fluminense 0, aos 67 minutos!”

**Chance clara sem gol:**

> “Boa chegada do Palmeiras! Raphael Veiga encontra espaço pelo meio e finaliza de fora da área. A bola passa muito perto da trave!”

**Cartão:**

> “Cartão amarelo para João Silva. Chegada atrasada no meio-campo, e a arbitragem não hesita.”

**Panorama:**

> “O placar continua 0 a 0, mas o mandante controla mais a bola: 58% de posse contra 42%. O visitante tenta acelerar pelos lados.”

**Substituição:**

> “Mudança no time visitante: sai Lucas e entra Marcos. O treinador busca mais velocidade no ataque.”

As explicações táticas só devem ser usadas quando houver base nos dados, na formação ou em uma anotação configurada pelo usuário. Não afirmar que um jogador está cansado, lesionado ou mal se isso não veio da fonte.

### 4. Criar entonação real por tipo de lance

O controle atual de `rate`, pausas de frase e `delivery` é um bom início, mas velocidade sozinha não produz narração profissional. Criar um perfil de voz por evento:

- **Gol:** início rápido, pausa curta antes do nome do autor, final forte e volume maior.
- **Chance:** energia média, subida no nome do jogador e queda no final se não houver gol.
- **Cartão:** tom firme e mais lento.
- **VAR:** suspense com frases curtas e silêncio controlado.
- **Panorama:** voz estável, ritmo conversacional.
- **Intervalo/fim:** tom de fechamento e resumo.

No áudio, isso pode ser feito com frases segmentadas, marcadores de pausa e parâmetros por trecho. Se for adicionado um provedor de TTS remoto, ele deve ser opcional; a voz local atual precisa continuar como fallback para evitar que a live pare sem internet.

A documentação de TTS da OpenAI descreve controles por instruções para sotaque, emoção, entonação, velocidade e tom, além de streaming de áudio. Porém, as vozes são indicadas como otimizadas para inglês; por isso, deve haver teste específico em português antes de torná-las a voz padrão. Também é necessário informar ao público quando uma voz de IA estiver sendo usada. [1]

### 5. Dicionário de pronúncia mais inteligente

O campo `pronunciations` já existe. Melhorar para aceitar:

- nome exibido;
- pronúncia em português;
- apelido;
- clube associado;
- validade por campeonato;
- exemplo de áudio;
- prioridade da regra.

Exemplo:

```json
{
  "display": "Endrick",
  "spoken": "Êndriqui",
  "aliases": ["Endrick Felipe"],
  "team": "Real Madrid"
}
```

Aplicar a substituição somente no texto enviado ao TTS. O overlay deve continuar mostrando o nome oficial. Também normalizar abreviações, nomes com hífen, acentos e jogadores homônimos.

### 6. Adicionar “Enviar lance” no painel

A API atual já possui `POST /api/event`, mas o usuário precisa de um formulário claro no painel. Criar um cartão **Enviar lance manualmente** com:

- tipo do lance;
- minuto;
- time;
- jogador;
- texto factual;
- ícone;
- botão **Mostrar no overlay**;
- botão **Narrar agora**;
- opção **Adicionar à fila**.

O botão **Narrar agora** deve gerar um evento P0/P1 e inserir o áudio na fila. O botão **Mostrar no overlay** deve atualizar o gráfico sem necessariamente interromper a fala atual. Também incluir atalhos de teclado para gol, cartão, escanteio e chance clara.

Esse recurso é importante porque a fonte pode atrasar. O operador da transmissão pode enviar o lance assim que o enxergar e corrigir o texto depois, sem editar o placar manualmente.

### 7. Integrar o chat da live do YouTube com segurança

A API oficial do YouTube fornece `liveChatMessages.list` e também `streamList` para receber mensagens com menor latência. As mensagens podem conter texto, Super Chat, membros, enquetes e dados do autor. O `liveChatId` vem do recurso da transmissão ao vivo. [2] [3]

Implementar em um módulo separado, por exemplo `backend/youtube_live.py`:

1. Login OAuth 2.0 somente para a conta do canal.
2. Localizar a transmissão ativa e obter o `liveChatId`.
3. Receber mensagens via `streamList`; usar `list` com `nextPageToken` como fallback.
4. Guardar o último ID processado e descartar duplicatas.
5. Limitar frequência por usuário, por exemplo uma interação a cada 30–60 segundos.
6. Aceitar somente comandos configurados, como:
   - `!narrar nome`
   - `!placar`
   - `!jogador Pedro`
   - `!pergunta ...`
7. Colocar mensagens em uma fila separada da fila dos lances.
8. Nunca deixar o chat ultrapassar um gol, VAR ou cartão vermelho.
9. Sanitizar texto, remover links, comandos perigosos e conteúdo ofensivo.
10. Mostrar no painel quem foi atendido, qual mensagem foi ignorada e por quê.

Exemplo de interação:

> Chat: `@ana fala do Pedro`
>
> Narrador: “A Ana pediu um comentário sobre Pedro. Ele aparece como referência na área e participa das principais ações ofensivas registradas até aqui.”

Esse texto só deve mencionar estatísticas se elas estiverem disponíveis. Se não houver informação confiável, responder: “Ainda não tenho estatística individual suficiente para comentar esse jogador nesta partida.”

Não recomendar que o programa leia todo o chat em voz alta. O correto é ter comandos, aprovação automática por regras e limites para não transformar a transmissão em spam.

### 8. Responder a nomes de jogadores sem confundir homônimos

Criar um índice com os titulares, reservas e jogadores que apareceram nos eventos. Quando o chat mencionar um nome:

- comparar sem acento e sem diferença entre maiúsculas/minúsculas;
- aceitar nome completo e sobrenome;
- conferir o time quando houver ambiguidade;
- pedir esclarecimento se dois jogadores tiverem o mesmo sobrenome;
- impedir que um nome escrito no chat seja tratado como fato sobre o jogo.

O comentário deve usar primeiro fatos da partida, depois o perfil pré-carregado, e por último uma resposta neutra. Não inventar biografia, nota ou desempenho.

### 9. Melhorar o “cérebro” local

O Qwen local deve continuar como planejador de baixo risco. Para soar melhor:

- expandir os tipos de evento para `var`, `chance`, `corner`, `free_kick`, `substitution`, `chat_reply`, `halftime` e `fulltime`;
- usar esquemas JSON separados por tipo;
- incluir limite de duração estimada do áudio;
- impedir duas frases de abertura iguais seguidas;
- registrar a decisão usada, sem registrar mensagens sensíveis além do necessário;
- usar um cache de frases para respostas frequentes do chat;
- adicionar testes de não-invenção para nomes, números, cartões e autores de gol.

A geração de texto não deve ficar no caminho crítico de gols. Se a IA demorar mais que um limite curto, usar um roteiro determinístico pronto e narrar o fato.

### 10. Corrigir a arquitetura do servidor antes de publicar

O código foi desenhado para uso local, o que é adequado para OBS. Se houver exposição externa, adicionar autenticação nos endpoints que alteram placar, eventos, aparência, narração e comandos. Uma live pública não deve permitir que qualquer pessoa que descubra a porta envie gol falso para o overlay.

Também recomendo:

- logs estruturados com nível configurável;
- health check de fonte, voz e YouTube;
- reconexão com backoff;
- indicador de atraso da fonte;
- botão de pânico **silenciar tudo**;
- teste de áudio antes de entrar ao vivo;
- gravação local opcional das últimas falas para revisão;
- métricas de latência: evento recebido, texto pronto, áudio pronto e áudio iniciado.

## Ordem recomendada de implementação

### Fase 1 — melhora imediata, sem depender de APIs novas

1. Formulário **Enviar lance**.
2. Fila com IDs, prioridade, deduplicação e interrupção controlada.
3. Templates melhores para gol, cartão, chance, escanteio, substituição e VAR.
4. Perfis de entonação por tipo de evento.
5. Dicionário de pronúncia com teste de voz.
6. Botão de silenciar e indicador de atraso.

### Fase 2 — chat do YouTube

1. OAuth 2.0 e armazenamento seguro do token.
2. Descoberta da live e do `liveChatId`.
3. Recepção por `streamList` com fallback para `list`.
4. Comandos `!placar`, `!narrar`, `!jogador` e `!pergunta`.
5. Moderação, limite por usuário e fila separada.
6. Painel de mensagens recebidas e respostas narradas.

### Fase 3 — narração realmente lance a lance

1. Integrar uma fonte de eventos mais detalhada, com ações e timestamps.
2. Implementar alinhamento entre horário da fonte, atraso do vídeo e áudio.
3. Permitir operador enviar eventos manuais em tempo real.
4. Só depois testar visão computacional sobre a imagem da partida. Isso exige acesso legítimo ao vídeo, bastante processamento e uma estratégia para reduzir falsos positivos. Não deve ser a primeira etapa.

## Critérios de aceitação

O programa pode ser considerado profissional quando:

- um gol é narrado uma única vez, com nome, time, placar e minuto corretos;
- um comentário atrasado nunca passa na frente de gol ou VAR;
- uma falha da IA não interrompe a transmissão;
- uma mensagem do chat não consegue alterar o placar;
- o nome de um jogador é pronunciado de forma configurável;
- o operador consegue enviar e corrigir um lance sem reiniciar o servidor;
- o áudio chega ao OBS com atraso visível e controlável;
- o sistema informa quando está usando voz de IA;
- cada resposta sobre jogador é baseada em fatos disponíveis ou admite que não há dados.

## Referências

[1]: https://developers.openai.com/api/docs/guides/text-to-speech "OpenAI — Text to speech"
[2]: https://developers.google.com/youtube/v3/live/docs/liveChatMessages "Google for Developers — Live Chat Messages"
[3]: https://developers.google.com/youtube/v3/live/docs "Google for Developers — YouTube Live Streaming API"

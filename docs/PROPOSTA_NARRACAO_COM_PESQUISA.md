# Proposta: narração com pesquisa e roteiro dinâmico

**Data:** 15/10/2026  
**Status:** proposta para revisão; a coleta ampliada de notícias ainda não foi implementada.

## Objetivo

Preparar comentários em português que combinem os dados ao vivo da partida com contexto recente e verificável sobre os clubes e o jogo. A IA deve redigir um roteiro curto; o narrador atual lê cada parte da fila, interrompendo contexto e panorama quando chega um lance prioritário.

## O que o programa já faz

- A ESPN é a fonte principal configurável para placar, relógio, estatísticas, escalações e eventos. O projeto identifica essa consulta como experimental e sujeita à cobertura e ao atraso da fonte.
- Há integração opcional do GE para encontrar a partida e consultar lances, escalações e técnicos na página pública vinculada. A consulta ocorre a cada 30 segundos; o canal direto já testado retornou 403. O código mantém placar e relógio sob controle da fonte principal.
- A fila do navegador prioriza gols, correções, revisões e outros eventos. Comentários menos urgentes podem ser removidos da fila se ficarem velhos.
- A IA atual não pesquisa a internet. Ela recebe texto/fatos que o programa já possui e escolhe informações permitidas para organizar um comentário. Se falhar, a narração factual original continua.
- Existem informações complementares limitadas de perfis, classificação, forma recente e alguns conteúdos de clubes. Elas não equivalem a uma pesquisa geral de notícias.

## Desenho recomendado

1. **Separar fatos da partida e contexto editorial.** ESPN/GE ou outro fornecedor autorizado fornece placar e eventos; notícias nunca alteram o placar, o relógio ou confirmam um gol.
2. **Pesquisar somente fontes configuradas e permitidas.** Priorizar API licenciada, feed RSS cujo uso permita essa finalidade, comunicados oficiais de clubes/ligas e fontes que o usuário habilitou. Não raspar páginas de notícias automaticamente, contornar bloqueios, paywalls ou endpoints privados.
3. **Validar cada item antes de enviá-lo à IA.** Registrar partida/equipe relacionada, título, resumo curto permitido, URL, editor, horário de publicação e horário de consulta. Descartar notícia ambígua, velha, duplicada ou sobre outro jogo.
4. **Montar um pacote de evidências pequeno.** Reunir os fatos recentes mais relevantes e dados atuais da partida. Cada fato conserva a fonte e a idade; a IA não recebe permissão para inventar informações externas.
5. **Gerar roteiro estruturado.** A resposta da IA lista blocos curtos (abertura, contexto, leitura do jogo e transição), cada um ligado aos IDs dos fatos usados. Validar esses IDs e números no servidor. A IA pode resumir/parafrasear, sem reproduzir parágrafos das matérias.
6. **Entregar o roteiro à fila existente.** Eventos novos interrompem ou passam à frente do contexto. Antes da fala, descartar blocos vencidos e já lidos; evitar repetição. A fila não deve atrasar anúncio de gol para esperar pesquisa ou IA.
7. **Expor controles no painel.** Ativar/desativar pesquisa, escolher fontes, solicitar atualização, configurar intervalo, mostrar título/fonte/horário dos itens e permitir ignorar ou reler o roteiro. Exibir quando a IA ou alguma fonte estiver indisponível.
8. **Manter fallback.** Se pesquisa, IA ou internet falhar, usar estatísticas, eventos e os panoramas atuais. Pesquisa deve ser assíncrona, com timeout, cache e limites por fonte.

## Fontes e limites

- **ESPN:** manter como fonte estruturada atual do projeto. Sua cobertura já fornece o núcleo de dados esportivos, mas a disponibilidade de campos e a autorização comercial precisam ser avaliadas conforme o uso final.
- **GE:** manter a integração pública existente para a partida selecionada enquanto acessível. A página informa eventos e contexto editorial; não se deve assumir autorização para automatizar coleta ou retransmitir seus textos sem verificar os termos aplicáveis.
- **UOL:** não habilitar raspagem nem uso automático de matérias sem autorização. O aviso oficial restringe mineração/coleta automatizada, cópia/armazenamento e uso do conteúdo no desenvolvimento de software/IA sem autorização escrita.
- **Outros veículos:** ESPN, UOL e demais sites podem ser exibidos como links/fontes em integrações autorizadas. Para ingestão automática, cada conector precisa de API/licença/feed que permita o uso pretendido. A página pública, por si só, não prova essa permissão.
- **Dados pagos:** uma API esportiva licenciada pode melhorar cobertura de eventos ao vivo, mas exige chave, custo e verificação de competições cobertas. Notícias e placares são produtos/fontes diferentes.

## Fases sugeridas

**Fase 1 — roteiro melhor com dados existentes:** ampliar o planejador para produzir blocos fundamentados nos dados já disponíveis (ESPN, GE vinculado, tabela, forma e escalações), integrando-os à fila com prioridades e validade.

**Fase 2 — pesquisa editorial autorizada:** implementar conectores para fontes com API/feed e permissão confirmada, primeiro como contexto pré-jogo e intervalo. Guardar atribuição, URL, idade e histórico de uso.

**Fase 3 — ajuste operacional:** controles de fonte e cadência no painel, observabilidade dos dados utilizados, limite de chamadas, teste com partidas completas e ajuste das regras de frescor e repetição.

## Critérios de aceite propostos

- Cada afirmação contextual do roteiro aponta para um fato recebido e uma fonte identificável.
- Placar, minuto, autor de gol e estado da partida continuam vindo da fonte esportiva configurada, nunca de uma notícia ou da memória do modelo.
- Gols, cartões, revisões e correções mantêm prioridade sobre roteiro e panorama.
- Nenhum roteiro atrasado, repetido ou referente a outra partida é lido.
- Uma falha de fonte/API/modelo não para a narração factual.
- A tela mostra a fonte e o horário de publicação/consulta para contexto editorial.

## Remoção do runtime Llama

O código do planejador já não chama `llama-b10410-bin-win-cpu-x64`; a função foi substituída pela conexão OpenAI-compatible configurada no painel. A pasta executável ainda existe fisicamente na cópia local. Uma tentativa automática anterior de removê-la foi bloqueada; por isso, este relatório não afirma que os arquivos foram apagados. O GGUF Qwen é um arquivo separado e deve ser preservado se for usado pelo LM Studio.

O estado atual de `brain.json` aponta para `http://localhost:1235/v1` e `qwen/qwen3.5-9b`, mas o teste recente de conexão retornou HTTP 502. É necessário estabilizar essa conexão para aceitar a fase de geração por LLM; os fallbacks factuais continuam disponíveis.

## Referências consultadas

- Código existente: `backend/free_feed.py`, `backend/ge_feed.py`, `backend/match_context.py`, `backend/local_brain.py`, `static/narration.js` e `static/brain-output.js`.
- Relatórios existentes: `docs/VIABILIDADE.md`, `docs/VIABILIDADE_GE.md` e `docs/REFERENCIAS_APIS_CONTEXTO.md`.
- UOL, aviso oficial de direitos autorais: https://noticias.uol.com.br/regras/aviso-de-direitos-autorais/ — descreve limites para reprodução, armazenamento, coleta automatizada e uso em software/IA sem permissão escrita.
- UOL, termos oficiais: https://noticias.uol.com.br/regras/termos-de-uso/ — restringe mineração/coleta automatizada e exploração de conteúdo sem autorização.
- Globo, termo oficial de uso consultado: https://ajuda.globo/cartola/termos-e-politicas/faq/termo-de-uso.ghtml — contém restrições de acesso automatizado, data mining e reprodução para aquele serviço; deve-se verificar os termos próprios do produto antes de habilitar qualquer conector GE.
- API-Football, guia oficial: https://www.api-football.com/news/post/how-to-get-started-with-api-football-the-complete-beginners-guide — descreve acesso estruturado a resultados/eventos ao vivo e suas condições de cobertura.

## Decisão solicitada

Revisar e aprovar ou ajustar o escopo acima antes de iniciar a ampliação para coleta autorizada de notícias e roteiros. A remoção física da pasta Llama fica registrada como pendência separada porque a ação automática de exclusão foi bloqueada.

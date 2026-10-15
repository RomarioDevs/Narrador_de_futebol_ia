# Proposta: narração com pesquisa e roteiro dinâmico

**Data:** 15/10/2026  
**Status:** escopo aprovado e implementado em 15/10/2026. A integração com o LM Studio ainda precisa ser testada pelo usuário após reiniciar o servidor.

## Objetivo

Preparar comentários em português que combinem os dados ao vivo da partida com contexto recente e verificável sobre os clubes e o jogo. A IA deve redigir um roteiro curto; o narrador atual lê cada parte da fila, interrompendo contexto e panorama quando chega um lance prioritário.

## O que o programa já faz

- A ESPN é a fonte principal configurável para placar, relógio, estatísticas, escalações e eventos. O projeto identifica essa consulta como experimental e sujeita à cobertura e ao atraso da fonte.
- Há integração opcional do GE para encontrar a partida e consultar lances, escalações e técnicos na página pública vinculada. A consulta ocorre a cada 30 segundos; o canal direto já testado retornou 403. O código mantém placar e relógio sob controle da fonte principal.
- A fila do navegador prioriza gols, correções, revisões e outros eventos. Comentários menos urgentes podem ser removidos da fila se ficarem velhos.
- A IA atual não pesquisa a internet. Ela recebe texto/fatos que o programa já possui e escolhe informações permitidas para organizar um comentário. Se falhar, a narração factual original continua.
- Existem informações complementares limitadas de perfis, classificação, forma recente e alguns conteúdos de clubes. Elas não equivalem a uma pesquisa geral de notícias.

## O que foi implementado após a aprovação

- O planejador recebe fatos do comentário estatístico atual, placar/tempo como contexto e pode escolher até três fatos complementares. O servidor mantém o texto factual validado; a IA não escreve nomes, placares ou lances novos.
- A narração periódica agora trata corretamente a escolha do comentarista como um objeto de fato, fonte e texto. Isso corrige a seleção de estatísticas/contexto que podia ser marcada como lida sem chegar à fila.
- O panorama pré-jogo e o roteiro de etapa incluem a forma recente que a fonte já fornece, com resultados e adversários disponíveis.
- A aba **07 · Notícias** usa a busca RSS gratuita do Google Notícias, sem chave ou assinatura. Consulta os nomes dos dois times, a competição/temporada e até dez jogadores das escalações, filtrando os domínios selecionados. Só aceita itens com data de publicação dos últimos três dias; a busca automática roda a cada 30 minutos.
- As preferências ficam em `news_context.json` (ignorado pelo Git). Títulos chegam à fila de voz somente com a opção correspondente ativada; ela começa desligada. O painel exibe títulos, link, veículo e data.
- O cliente de IA tenta novamente sem `response_format` se o servidor compatível rejeitar JSON mode e passa a mostrar a resposta HTTP de erro do servidor local para ajudar a diagnosticar o 502.

## Limites atuais da pesquisa gratuita

- O Google Notícias oferece RSS de busca sem chave, mas a disponibilidade, cobertura, frescor e formato dos feeds podem mudar; essa busca não tem SLA. O painel recebe títulos e links e não abre nem copia o texto das matérias.
- A página oficial do UOL Esporte explica o serviço RSS gratuito; o GE também mantém uma página de RSS por time e editoria, embora a página pública consultada seja antiga. A implementação usa busca agregada para cobrir times e jogadores em diversos veículos, porque nem todo site oferece um feed atualizado. [UOL Esporte RSS](https://www.uol.com.br/esporte/ultimas/receba.jhtm), [página RSS do GE](https://redeglobo.globo.com/Esportes/0,,GEH946-9645,00.html), [formato de RSS de busca do Google Notícias](https://support.google.com/googlenews/thread/740233/how-do-i-obtain-an-rss-feed-of-google-news-custom-search).
- Acesso gratuito ao título/link não concede automaticamente direitos para retransmitir manchetes em voz. O UOL restringe coleta automatizada e reprodução/uso do conteúdo em software/IA sem autorização escrita. Mantenha a opção de voz desligada sem permissão. [Aviso oficial do UOL](https://noticias.uol.com.br/regras/aviso-de-direitos-autorais/).
- Enquanto o servidor do LM Studio continuar retornando 502, a fila usa o texto factual. O novo erro detalhado pode identificar a causa depois da reinicialização; não foi possível acessar o LM Studio do agente nesta sessão.

## Como ativar no programa

1. Reinicie o servidor com `start.bat` e atualize o painel com **Ctrl+F5**.
2. Na aba **07 · Notícias**, marque as fontes e salve. Não precisa de chave nem cadastro. Clique em **Pesquisar notícias recentes (até 3 dias)**.
3. Para atualizar enquanto o jogo está carregado, marque a opção de atualização automática. Ela consulta no máximo a cada 30 minutos.
4. Mantenha **Incluir títulos na voz** desligado até confirmar que seu plano e as permissões dos veículos cobrem essa retransmissão. O contexto da partida e os comentários estatísticos continuam funcionando sem isso.
5. Na seção da IA, use **Buscar modelos disponíveis**, escolha o modelo servido pelo LM Studio e teste a conexão. Uma falha deixa a narração factual ativa.

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

## Próximas melhorias possíveis

**Roteiro:** ampliar o planejador para produzir blocos fundamentados nos dados disponíveis (ESPN, GE vinculado, tabela, forma, escalações e manchetes RSS), integrando-os à fila com prioridades e validade.

**Mais fontes:** ampliar a lista de veículos conforme feeds públicos e permissões de uso disponíveis. Guardar atribuição, URL, data e histórico de itens usados.

**Ajuste operacional:** observar os feeds em partidas reais e ajustar relevância, frescor, repetição e cadência; o Google Notícias pode alterar cobertura ou formato sem aviso.

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

## Runtime Llama

O programa não usa mais o executável `llama-b10410-bin-win-cpu-x64`; o planejador chama somente o servidor configurado pelo usuário. A pasta binária ainda está fisicamente no disco porque a solicitação automática de exclusão foi bloqueada pelo ambiente. Não se deve confundir esse runtime com o arquivo GGUF Qwen, que é separado e pode continuar sendo usado pelo LM Studio.

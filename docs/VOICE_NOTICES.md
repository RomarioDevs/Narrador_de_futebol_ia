# Componentes da voz local

## Planejamento dos comentários

O planejador pode ser desligado, conectado a um servidor local compatível com OpenAI Chat Completions, ou a uma API online HTTPS. O usuário escolhe o serviço, modelo e URL no painel. Quando configurado, o serviço recebe as informações usadas no comentário; podem se aplicar termos, cobrança e condições de privacidade do provedor. A resposta só pode escolher uma abertura permitida e índices de fatos enviados pelo programa; nomes, números e fatos originais são montados e validados localmente. Sem resposta válida, o programa mantém o texto factual original.

## Kokoro

As vozes **Alex** (`pm_alex`), **Santa** (`pm_santa`) e **Dora** (`pf_dora`) usam o modelo **Kokoro-82M v1.0**, em português brasileiro, a 24.000 Hz. O projeto informa licença Apache-2.0 para o modelo; o adaptador `kokoro-onnx` 0.6.1 usa MIT. O adaptador também utiliza `phonemizer` e eSpeak NG, com suas próprias licenças GPL. As vozes são fornecidas pelo modelo; o programa não faz clonagem de vozes.

- Modelo e atribuições dos dados: https://huggingface.co/hexgrad/Kokoro-82M
- Catálogo das vozes: https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
- Código e licença do adaptador: https://github.com/thewh1teagle/kokoro-onnx
- Distribuição: https://pypi.org/project/kokoro-onnx/0.6.1/
- Exportação ONNX usada: https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1
- SHA-256 do modelo: `beb0d1848dee9a49da392cc3df26958d46cfa35d321edf434f52949153f0df3a`.
- SHA-256 do conjunto de vozes: `bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d`.
- eSpeak NG: https://github.com/espeak-ng/espeak-ng
- Phonemizer: https://github.com/bootphon/phonemizer

## Piper

O modo de IA usa **Piper TTS 1.8.0**, da Open Home Foundation, instalado separadamente por `requirements-voice.txt`.

- Código e licença GPL-3.0-or-later: https://github.com/OHF-Voice/piper1-gpl/tree/v1.8.0
- Licença do motor: https://github.com/OHF-Voice/piper1-gpl/blob/v1.8.0/COPYING
- Distribuição: https://pypi.org/project/piper-tts/1.8.0/
- Voz: `pt_BR-faber-medium`, português brasileiro, 22.050 Hz, um falante.
- Origem fixada: https://huggingface.co/rhasspy/piper-voices/tree/1162a9173d0ce503555aed757976b7a9912eae4c/pt/pt_BR/faber/medium
- O cartão dessa voz declara CC0 para o conjunto de treinamento. O repositório de vozes informa MIT em seus metadados. As declarações originais ficam em `models/piper/MODEL_CARD` e `models/piper/REPOSITORY_README.md` após instalar.
- SHA-256 do modelo ONNX: `858555e3a064209c57088fe6bd70c4c3dc54d03eaa00c45d5ecaf43a33f95aa7`.

A geração de voz acontece localmente. Textos de narração seguem do navegador para o servidor local do programa; não são enviados à API de planejamento de texto. A primeira instalação baixa o motor de voz, suas dependências e o modelo. As consultas de dados do futebol continuam usando a internet.

O planejador configurado pode selecionar e ordenar informações dos comentários. A saída é um plano restrito aos fatos fornecidos; o texto factual permanece inalterado. A síntese da voz é feita por Kokoro ou Piper. As licenças desses componentes não concedem direitos sobre transmissões, dados esportivos ou escudos de terceiros. Ao redistribuir o software, mantenha e observe as licenças dos componentes incluídos.

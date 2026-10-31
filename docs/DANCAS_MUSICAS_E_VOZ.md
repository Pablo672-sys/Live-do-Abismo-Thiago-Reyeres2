# Como adicionar músicas, danças e configurar a voz do Boneco

Este guia é para o avatar selecionado no sistema. Os nomes das pastas são sensíveis à grafia: mantenha-os exatamente como abaixo.

## 1. Coloque as músicas do sistema

Dentro da pasta de assets do avatar selecionado, crie ou use:

`Musicas/`

Coloque ali os arquivos de áudio. Formatos reconhecidos: `.mp3`, `.wav`, `.ogg`, `.flac` e `.m4a`.

Exemplo:

```text
<PASTA_DE_ASSETS>/<AVATAR_SELECIONADO>/
└── Musicas/
    ├── funk.mp3
    ├── rock.ogg
    └── samba.mp3
```

## 2. Crie uma dança silenciosa para cada música

Na mesma pasta do avatar, use:

`Dancando/`

Coloque um vídeo por dança. Formatos reconhecidos: `.mp4`, `.webm`, `.mov` e `.mkv`.

**Regra de associação:** o nome do vídeo deve ser igual ao nome da música, sem considerar a extensão.

```text
<PASTA_DE_ASSETS>/<AVATAR_SELECIONADO>/
├── Musicas/
│   ├── funk.mp3
│   ├── rock.ogg
│   └── samba.mp3
└── Dancando/
    ├── funk.mp4
    ├── rock.webm
    └── samba.mp4
```

Assim, `funk.mp3` toca com `funk.mp4`, `rock.ogg` com `rock.webm` e `samba.mp3` com `samba.mp4`.

- Exporte os vídeos sem áudio (ou com a faixa de áudio removida). A música vem da pasta `Musicas`.
- Use nomes simples, sem colocar informações extras no nome do vídeo.
- Se não existir um vídeo com o mesmo nome, o sistema usa uma dança disponível como alternativa.
- Quando a música começa, o Boneco entra na dança correspondente. Quando a música termina e outra começa, a dança acompanha a nova faixa.

## 3. Voz original do Boneco

O sintetizador configurado é o **Coqui XTTS v2**, em português (`pt`), usando a gravação original:

`<PASTA_DE_ASSETS>/BONECO_MAPA_2D/voz/VOZ_RAPIDA_MASCULINA.wav`

Não apague, renomeie ou substitua esse WAV se quiser manter a identidade vocal atual. O sistema não deve trocar silenciosamente para uma voz genérica do Windows: se o arquivo ou o XTTS falhar, o erro é registrado no log de TTS.

A fala usa a fila de mensagens do renderer. Quando há uma fala:
1. O vídeo/estado de dança é interrompido para mostrar a animação de fala.
2. A música continua em volume reduzido.
3. Ao terminar a fala, a música volta ao volume normal e a dança da faixa atual é retomada.

Volumes definidos no renderer:
- Música durante a dança: 16%.
- Música durante a fala: 5,5%.

## 4. Se ele não falar

Confira estes pontos:
1. O arquivo `VOZ_RAPIDA_MASCULINA.wav` existe no caminho indicado.
2. O ambiente Python do projeto tem o pacote Coqui TTS e as dependências do XTTS v2 instaladas.
3. O serviço/worker de TTS está iniciado e não há erro de síntese.
4. A fila de fala está recebendo mensagens e o renderer está aberto na página `/renderer`.
5. Consulte o log de TTS do projeto. Erros de voz original ausente ou falha do XTTS são registrados; não são corrigidos trocando por uma voz genérica.

## 5. Depois de adicionar arquivos

Reinicie/atualize o sistema para ele reler os arquivos de mídia. O renderer consulta a lista de músicas e vídeos do avatar selecionado automaticamente.

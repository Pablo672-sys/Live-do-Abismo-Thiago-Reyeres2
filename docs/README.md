# Boneco do Abismo — site para iPhone

Este site é publicado automaticamente em GitHub Pages pelo workflow `.github/workflows/deploy-pages.yml`.

## Endereço esperado
`https://pablo672-sys.github.io/Live-do-Abismo-Thiago-Reyeres2/`

## Instalar no iPhone
1. Abra o endereço no Safari.
2. Toque em Compartilhar.
3. Escolha **Adicionar à Tela de Início**.
4. Toque em **Adicionar**.

## Como criar o servidor
Leia o [tutorial de criação do servidor](COMO-CRIAR-O-SERVIDOR.md). Ele explica a diferença entre testar no Windows e usar uma VPS na nuvem, que é o caminho para manter o servidor ligado com o seu PC desligado.

## Limite importante
GitHub Pages hospeda apenas os arquivos estáticos deste site. O painel de live, o Ollama, a voz XTTS e o motor de transmissão precisam estar num servidor separado com HTTPS. A página permite informar o endereço HTTPS real desse servidor; ela não inventa nem cria um servidor de IA automaticamente.

## Publicação
O workflow de publicação é executado a cada alteração em `docs/` ou no próprio workflow. Consulte a aba Actions do repositório para ver o resultado mais recente.

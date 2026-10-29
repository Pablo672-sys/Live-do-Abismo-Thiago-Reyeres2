# Atualizações do Boneco do Abismo

## Como publicar uma versão

1. Faça e teste as alterações na branch `main`.
2. Crie uma tag de versão no formato `v0.1.1` (aumente o número conforme a mudança).
3. Envie a tag para o GitHub.
4. Confira a aba **Actions** e aguarde o fluxo de validação terminar.

O GitHub disponibiliza um ZIP do código de cada tag automaticamente. O fluxo de validação deste repositório verifica sintaxe Python, arquivos essenciais e o script Linux; ele não substitui testes reais no Windows, Linux, áudio ou transmissão.

## Limitações importantes do atualizador

- A atualização pelo painel existente usa `git pull --ff-only` e só funciona em cópias clonadas com Git.
- Instalações feitas extraindo ZIP ainda não são atualizadas pelo atualizador atual.
- A atualização não deve substituir `assets/`, `private/`, `runs/`, `.env` ou o ambiente `.venv/`, pois podem conter a voz original, configurações e dados locais.
- Não considere uma versão pronta apenas porque o fluxo de validação passou. Teste em uma cópia de instalação Windows e Linux antes de anunciar a versão.

## Estado da atualização automática

O fluxo de CI aqui valida alterações e tags. Ele não publica uma versão por conta própria nem habilita instalação silenciosa em todas as máquinas. Isso exige um atualizador multiplataforma com backup, validação do pacote, rollback e reinício coordenado; não execute uma atualização destrutiva enquanto a live estiver ativa.

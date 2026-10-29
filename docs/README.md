# Boneco do Abismo — Windows e Linux

Página de entrada do projeto para computador. Não oferecemos aqui instalação para iPhone ou Android.

## Site
https://pablo672-sys.github.io/Live-do-Abismo-Thiago-Reyeres2/

## Baixar o projeto
[Baixar o código-fonte em ZIP](https://github.com/Pablo672-sys/Live-do-Abismo-Thiago-Reyeres2/archive/refs/heads/main.zip)

O ZIP contém o código-fonte; não é um instalador .exe nem AppImage pronto.

## Windows
1. Extraia o ZIP.
2. Instale Python 3.12.
3. Abra PowerShell na pasta do projeto e execute:
   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\start_boneco_windows.ps1
   ```

## Linux
Com Python 3.12 e o módulo venv instalados, na pasta do projeto:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
BONECO_GAME_DIR="$PWD" BONECO_GAME_ASSETS_DIR="$PWD/assets" BONECO_GAME_HOST=127.0.0.1 BONECO_GAME_PORT=9292 python -m uvicorn boneco_game.main:app --host 127.0.0.1 --port 9292
```
Abra http://127.0.0.1:9292 no navegador do computador.

## Voz do Boneco
O serviço de voz define como referência `assets/BONECO_MAPA_2D/voz/VOZ_RAPIDA_MASCULINA.wav` e usa Coqui XTTS para síntese. O XTTS e seus modelos precisam estar instalados/configurados para a geração de voz funcionar; o arquivo de referência por si só não é um aplicativo de voz independente.

## Limitações
O GitHub Pages hospeda apenas arquivos estáticos. O servidor, IA, modelos, credenciais de live, áudio e transmissão são executados/configurados separadamente. Nunca coloque credenciais privadas no GitHub.

# Boneco do Abismo — instalação no Windows e Linux

Este guia é apenas para computadores Windows e Linux. Não é um tutorial de iPhone ou Android.

## Windows 10/11
1. Baixe o projeto em **Code → Download ZIP** e extraia a pasta.
2. Instale Python 3.12 e marque a opção para adicionar Python ao PATH.
3. Abra PowerShell na pasta extraída e execute:
   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\start_boneco_windows.ps1
   ```
4. Na primeira execução, o script cria o ambiente virtual e instala as dependências básicas.
5. Abra http://127.0.0.1:9292 no navegador do PC e mantenha o terminal aberto.

## Linux
1. Instale Python 3.12, pip e venv usando o gerenciador de pacotes da sua distribuição.
2. Abra um terminal na pasta extraída e execute:
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python -m pip install -e . --no-deps
   BONECO_GAME_DIR="$PWD" BONECO_GAME_ASSETS_DIR="$PWD/assets" BONECO_GAME_HOST=127.0.0.1 BONECO_GAME_PORT=9292 python -m uvicorn boneco_game.main:app --host 127.0.0.1 --port 9292
   ```
3. Abra http://127.0.0.1:9292 no navegador do mesmo computador.

## Voz original do Boneco
O serviço de síntese aponta para `assets/BONECO_MAPA_2D/voz/VOZ_RAPIDA_MASCULINA.wav` como referência vocal do Coqui XTTS. Para gerar falas, instale e configure as dependências e o modelo XTTS necessários. Não confunda o arquivo de referência com um modelo completo de síntese de voz.

## Importante
- O ZIP é o código-fonte e o iniciador, não um instalador Windows .exe ou Linux AppImage.
- Os recursos completos de live podem precisar de modelos de IA, credenciais privadas, Tor, áudio e software de transmissão configurados separadamente.
- Não exponha o servidor diretamente à internet nem publique tokens ou senhas.

#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo
echo "============================================"
echo "       BONECO DO ABISMO - LINUX"
echo "============================================"
echo
echo "Este instalador foi pensado para Ubuntu/Debian."
echo "A primeira instalacao precisa de internet."
echo

if ! command -v apt-get >/dev/null 2>&1; then
  echo "ERRO: este instalador automatico precisa de Ubuntu/Debian (apt)."
  echo "Em outras distribuicoes, instale os pacotes equivalentes manualmente."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python nao encontrado. Os pacotes serao instalados pelo apt."
fi

echo "[1/4] Instalando dependencias do sistema..."
sudo apt-get update
sudo apt-get install -y \
  python3 python3-venv python3-pip python3-dev build-essential \
  git curl xdg-utils nodejs npm tor torsocks \
  pulseaudio-utils pavucontrol xserver-xephyr x11-utils \
  gstreamer1.0-tools gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly gstreamer1.0-libav \
  gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0

echo
echo "[2/4] Criando ambiente Python..."
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip setuptools wheel

echo
echo "[3/4] Instalando dependencias do projeto..."
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -e . --no-deps

echo
echo "[4/4] Preparando monitor TikTok..."
if [ -f external/tiktok-live-monitoring-server/package.json ]; then
  (cd external/tiktok-live-monitoring-server && npm install)
fi

mkdir -p private runs/logs

echo
echo "Instalacao do painel concluida."
echo "O XTTS e a transmissao ao vivo podem exigir configuracao extra de Torch/CUDA,"
echo "Tor, navegador, audio, videos e credenciais. Nada disso sera inventado pelo instalador."
echo "A gravacao de referencia da voz original precisa estar nos assets do projeto."
echo
read -r -p "Deseja iniciar o painel agora? [S/n] " answer
if [[ "${answer:-S}" =~ ^[Ss]$ ]]; then
  export BONECO_GAME_DIR="$PROJECT_DIR"
  exec .venv/bin/python -m uvicorn boneco_game.main:app --app-dir src --host 127.0.0.1 --port 9292
fi

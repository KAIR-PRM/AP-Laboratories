#!/bin/bash

# Skrypt do pobrania tylko podkatalogu CARLA/lab0 oraz wybranych plików z CARLA
# Używa Git sparse-checkout (wymaga Git >= 2.25)

set -e  # Zakończ skrypt przy błędzie

REPO_URL="https://github.com/KAIR-PRM/AP-Laboratories.git"
REPO_NAME="AP-Laboratories"

echo "======================================================="
echo "Klonowanie CARLA/lab0 i plików konfiguracyjnych"
echo "======================================================="

# Sprawdzenie wersji Git
GIT_VERSION=$(git --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
echo "Wykryta wersja Git: $GIT_VERSION"

# Klonowanie z filtrowaniem i sparse checkout
echo "Klonowanie repozytorium..."
git clone --filter=blob:none --sparse "$REPO_URL"

# Przejście do katalogu repozytorium
cd "$REPO_NAME"

# Konfiguracja sparse-checkout na wybrane pliki i katalogi
# Używamy --no-cone aby móc wskazać pojedyncze pliki
# Przedrostek '/' dla pojedynczych plików (non-cone mode)
echo "Konfigurowanie sparse-checkout..."
echo "  - CARLA/lab0"
echo "  - CARLA/docker-compose.yml"
echo "  - CARLA/requirements.txt"
git sparse-checkout init --no-cone
git sparse-checkout set CARLA/lab0 /CARLA/docker-compose.yml /CARLA/requirements.txt

echo ""
echo "✓ Pomyślnie sklonowano wybrane pliki i katalogi"
echo "✓
echo "Struktura sklonowanych plików:"
tree CARLA -L 2 2>/dev/null || find CARLA -maxdepth 2 -type f -o -type d

echo ""
echo "======================================================="
echo "Sklonowanie zakończone!"
echo "======================================================="
echo ""
echo "Aby uruchomić CARLA:"
echo "  cd $REPO_NAME/CARLA"
echo "  docker compose up
echo "================================================"

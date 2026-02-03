#!/bin/bash
set -e

# --- Configuration ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'
HUB_USER="blueman2903"
IMAGE_NAME="lola-backend"

# --- 1. Generate Date-Based Tag ---
# Format: YYYY-MM-DD-HHMM (Year-Month-Day-HourMinute)
# Example: 2026-02-03-2115
TAG=$(date +%Y-%m-%d-%H%M)
FULL_IMAGE_NAME="$HUB_USER/$IMAGE_NAME:$TAG"

# --- Find Project Root ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$( cd -- "$SCRIPT_DIR/.." &> /dev/null && pwd )

echo -e "${GREEN}--- Building Image: $FULL_IMAGE_NAME ---${NC}"
docker build -t "$FULL_IMAGE_NAME" -f "$PROJECT_ROOT/Docker/Dockerfile" "$PROJECT_ROOT"

echo -e "\n${GREEN}--- Pushing to Docker Hub ---${NC}"
docker push "$FULL_IMAGE_NAME"

echo -e "\n${GREEN}--- SUCCESS! ---${NC}"
echo -e "Copy this tag for your server:"
echo -e "${CYAN}$TAG${NC}"
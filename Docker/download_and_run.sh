#!/bin/bash
set -e

# --- Configuration ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

# --- Find Project Root ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$( cd -- "$SCRIPT_DIR/.." &> /dev/null && pwd )
COMPOSE_FILE="${PROJECT_ROOT}/Docker/docker-compose.yml"
ENV_FILE="${PROJECT_ROOT}/.env"

# --- 1. Ask User for Tag ---
echo -e "${CYAN}Which tag do you want to deploy?${NC}"
echo -e "(Copy the date-tag from your build script, e.g., 2026-02-03-2115)"
read -r INPUT_TAG

if [ -z "$INPUT_TAG" ]; then
    echo "Error: Tag cannot be empty."
    exit 1
fi

# Export the variable so docker-compose can see it
export TAG=$INPUT_TAG

echo -e "\n${GREEN}--- Step 2: Downloading image: $TAG ... ---${NC}"
# Pass the env var explicitly to the command
TAG=$TAG docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull

echo -e "\n${GREEN}--- Step 3: Restarting stack... ---${NC}"
TAG=$TAG docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down --remove-orphans
TAG=$TAG docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

echo -e "\n${GREEN}--- Deployment Complete! ---${NC}"
echo -e "Running version: ${CYAN}$TAG${NC}"
#!/bin/bash
set -e

# --- Configuration ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# --- Find Project Root ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$( cd -- "$SCRIPT_DIR/.." &> /dev/null && pwd )

echo -e "${GREEN}--- Project root identified at: ${PROJECT_ROOT} ---${NC}"

# Define paths
COMPOSE_FILE="${PROJECT_ROOT}/Docker/docker-compose.yml"
ENV_FILE="${PROJECT_ROOT}/.env"

if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}Error: docker-compose.yml not found at $COMPOSE_FILE${NC}"
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Error: .env file not found at $ENV_FILE${NC}"
    exit 1
fi

echo -e "\n${GREEN}--- Step 1: Stopping and removing old containers... ---${NC}"
# CHANGED: 'docker-compose' -> 'docker compose'
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down --remove-orphans || true

echo -e "\n${GREEN}--- Step 2: Rebuilding and starting the stack... ---${NC}"
# CHANGED: 'docker-compose' -> 'docker compose'
if docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up --build -d; then
    echo -e "\n${GREEN}--- Process complete! Stack is running. ---${NC}"
    echo -e "${CYAN}Backend and Ngrok are now active.${NC}"
    # CHANGED: Updated the help text to suggest the new command
    echo "To view logs: docker compose -f Docker/docker-compose.yml logs -f"
else
    echo -e "${RED}ERROR: Failed to start the stack.${NC}"
    exit 1
fi
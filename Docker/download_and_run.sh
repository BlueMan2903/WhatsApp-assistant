#!/bin/bash
set -e

# --- Configuration ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

# --- 1. Smart Path Resolution ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Find .env (Check same folder, then parent folder)
if [ -f "$SCRIPT_DIR/.env" ]; then
    ENV_FILE="$SCRIPT_DIR/.env"
elif [ -f "$SCRIPT_DIR/../.env" ]; then
    ENV_FILE="$SCRIPT_DIR/../.env"
else
    echo -e "${CYAN}Error: .env file not found in $SCRIPT_DIR or its parent.${NC}"
    exit 1
fi

# Find docker-compose.yml (Check same folder, then standard Docker/ path)
if [ -f "$SCRIPT_DIR/docker-compose.yml" ]; then
    COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"
elif [ -f "$SCRIPT_DIR/../Docker/docker-compose.yml" ]; then
    COMPOSE_FILE="$SCRIPT_DIR/../Docker/docker-compose.yml"
else
    echo -e "${CYAN}Error: docker-compose.yml not found.${NC}"
    exit 1
fi

echo -e "${GREEN}Using Env: $ENV_FILE${NC}"
echo -e "${GREEN}Using Compose: $COMPOSE_FILE${NC}"

# --- 2. Ask User for Tag ---
echo -e "\n${CYAN}Which tag do you want to deploy?${NC}"
read -r INPUT_TAG

if [ -z "$INPUT_TAG" ]; then
    echo "Error: Tag cannot be empty."
    exit 1
fi

export TAG=$INPUT_TAG
# NEW: Export the absolute path to the .env file for Docker Compose
export ENV_FILE_PATH=$ENV_FILE

echo -e "\n${GREEN}--- Step 2: Downloading image: $TAG ... ---${NC}"

# --- 3. Pull and Run ---
echo -e "\n${GREEN}--- Step 2: Downloading image: $TAG ... ---${NC}"
TAG=$TAG docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull

echo -e "\n${GREEN}--- Step 3: Restarting stack... ---${NC}"
TAG=$TAG docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down --remove-orphans
TAG=$TAG docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

echo -e "\n${GREEN}--- Deployment Complete! ---${NC}"
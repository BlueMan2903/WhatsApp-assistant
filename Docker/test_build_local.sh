#!/bin/bash
set -e

# --- Configuration ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'
HUB_USER="blueman2903"
IMAGE_NAME="lola-backend"
CONTAINER_NAME="lola-local-test"

# --- 1. Generate Local Tag ---
# Use a consistent, descriptive tag for local testing
TAG="local-test"
FULL_IMAGE_NAME="$HUB_USER/$IMAGE_NAME:$TAG"

# --- Find Project Root ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$( cd -- "$SCRIPT_DIR/.." &> /dev/null && pwd )

echo -e "${GREEN}--- Step 1: Building Local Test Image: $FULL_IMAGE_NAME ---${NC}"
docker build -t "$FULL_IMAGE_NAME" -f "$PROJECT_ROOT/Docker/Dockerfile" "$PROJECT_ROOT"

echo -e "\n${GREEN}--- Step 2: Stopping and removing any old test containers ---${NC}"
# Use '|| true' to prevent script from exiting if container doesn't exist
docker stop "$CONTAINER_NAME" || true
docker rm "$CONTAINER_NAME" || true

echo -e "\n${GREEN}--- Step 3: Running the new image locally ---${NC}"
# Note: Assumes your .env file is in the project root.
docker run -d \
  --name "$CONTAINER_NAME" \
  -p 5000:5000 \
  --env-file "$PROJECT_ROOT/.env" \
  "$FULL_IMAGE_NAME"

echo -e "\n${GREEN}--- LOCAL BUILD AND RUN SUCCESS! ---${NC}"
echo -e "Container started as '${CYAN}$CONTAINER_NAME${NC}' and is accessible on ${CYAN}http://localhost:5000${NC}"
echo -e "To view logs, run: ${CYAN}docker logs -f $CONTAINER_NAME${NC}"
echo -e "To stop the container, run: ${CYAN}docker stop $CONTAINER_NAME${NC}"
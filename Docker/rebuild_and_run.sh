#!/bin/bash

# rebuild_and_run.sh
# This script prompts for a version tag, then stops, removes, rebuilds,
# and starts the Docker container.

# --- Configuration ---
CONTAINER_NAME="test-container"
IMAGE_BASE_NAME="whatsapp-assistant"

# --- Add color for readability ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- NEW: Robustly find the project root directory ---
# This finds the directory the script itself is in, then goes one level up.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$( cd -- "$SCRIPT_DIR/.." &> /dev/null && pwd )

echo -e "${GREEN}--- Project root identified at: ${PROJECT_ROOT} ---${NC}"
# --- End of new section ---

# --- Prompt user for a version tag ---
echo -e "\n${CYAN}Please provide a version tag for the Docker image.${NC}"
read -p "Enter tag (e.g., v1.1) or press Enter for 'latest': " TAG

if [ -z "$TAG" ]; then
  TAG="latest"
fi

IMAGE_NAME="${IMAGE_BASE_NAME}:${TAG}"
echo -e "${GREEN}Will use image tag: ${IMAGE_NAME}${NC}"

# --- Execute Docker commands from the project root ---
echo -e "\n${GREEN}--- Step 1: Stopping the existing container... ---${NC}"
docker stop $CONTAINER_NAME || true

echo -e "\n${GREEN}--- Step 2: Removing the old container... ---${NC}"
docker rm $CONTAINER_NAME || true

echo -e "\n${GREEN}--- Step 3: Building the new image from project root... ---${NC}"
# The build context is the project root, and we point to the Dockerfile with -f
docker build --no-cache -t $IMAGE_NAME -f "${PROJECT_ROOT}/Docker/Dockerfile" "$PROJECT_ROOT"

echo -e "\n${GREEN}--- Step 4: Starting the new container... ---${NC}"
docker run -d -p 5000:5000 --env-file "${PROJECT_ROOT}/.env" --name $CONTAINER_NAME $IMAGE_NAME

echo -e "\n${GREEN}--- Process complete! ---${NC}"
echo "Container '$CONTAINER_NAME' is running with image '$IMAGE_NAME'."
echo "You can view logs with: docker logs -f $CONTAINER_NAME"
#!/bin/bash

# ---
# WARNING: This script is destructive and will permanently delete
# ALL Docker containers, images, networks, and build cache.
# Use with extreme caution.
# ---

# 1. Stop and remove all containers
echo "Stopping and removing all Docker containers..."
if [ -n "$(docker ps -a -q)" ]; then
    docker rm -f $(docker ps -a -q)
else
    echo "No containers to remove."
fi

# 2. Delete all Docker images
echo "Deleting all Docker images..."
if [ -n "$(docker images -q)" ]; then
    docker rmi -f $(docker images -q)
else
    echo "No images to delete."
fi

# 3. [NEW] Delete unused networks
# Docker Compose creates networks that must be manually removed if you don't use 'down'
echo "Pruning unused networks..."
docker network prune -f

# 4. [NEW] Delete Build Cache
# Critical for AWS Lightsail to reclaim space from the 'build-essential' compilation steps
echo "Pruning build cache..."
docker builder prune -f

echo "Docker cleanup complete. System is clean."
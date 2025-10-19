#!/bin/bash

# ---
# WARNING: This script is destructive and will permanently delete
# all Docker containers and images on your system.
# Use with extreme caution.
# ---

# 1. Stop and remove all containers
# The 'docker ps -a -q' command lists the IDs of all containers.
# The 'docker rm -f' command forcefully removes them. The -f (force) flag
# will stop them if they are running before removing them.
echo "Stopping and removing all Docker containers..."
if [ -n "$(docker ps -a -q)" ]; then
    docker rm -f $(docker ps -a -q)
else
    echo "No containers to remove."
fi

# 2. Delete all Docker images
# The 'docker images -q' command lists the IDs of all images.
# The 'docker rmi -f' command forcefully removes them.
echo "Deleting all Docker images..."
if [ -n "$(docker images -q)" ]; then
    docker rmi -f $(docker images -q)
else
    echo "No images to delete."
fi

echo "Docker cleanup complete."
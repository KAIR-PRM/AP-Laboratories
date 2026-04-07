#!/bin/bash

# Set required environment variables
export UID=$(id -u)
export USER=$(whoami)

# Remove existing containers if they exist
echo "Usuwanie istniejących kontenerów..."
docker rm -f carla_sim carla_viz 2>/dev/null || true

# Start containers using docker-compose
echo "Uruchamianie kontenerów CARLA..."
docker-compose up


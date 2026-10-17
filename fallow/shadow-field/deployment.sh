# Build and run all services
docker-compose up -d

# Scale model instances
docker-compose up -d --scale shadow-field=5
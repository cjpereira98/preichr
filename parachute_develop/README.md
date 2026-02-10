# Building both images using docker=compose
docker-compose build --no-cache
docker-compose up

# Building docker images seperately
$ docker buildx build -t parachute-frontend:latest .
$ docker buildx build -t parachute-backend:latest .

# List running containers and their port mapping
$ docker ps

# Check active containers and their IP addresses
$ docker network inspect bridge
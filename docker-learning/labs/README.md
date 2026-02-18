cat > docker-learning/labs/python-fastapi-dockerfile/README.md <<'EOF'
# Python FastAPI Dockerfile Lab

## Build
docker build -t py-api:3 .

## Run
docker run -d --name pyapi -p 8080:8000 py-api:3

## Test
curl http://localhost:8080/

## Check health
docker ps --filter name=pyapi
docker inspect --format='{{.State.Health.Status}}' pyapi
EOF

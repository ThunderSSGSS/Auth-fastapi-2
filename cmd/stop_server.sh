#Stop and delete containers
cd ../devops/docker-compose && \
docker-compose down

#Delete auth-server image
docker rmi auth-fastapi-2_auth-server
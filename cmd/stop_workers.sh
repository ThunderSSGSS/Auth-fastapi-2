#Stop and delete containers
cd ../devops/docker-compose && \
docker-compose down

#Delete email-worker and db-worker images
docker rmi auth-fastapi-2_email-worker auth-fastapi-2_db-worker
#Stop and delete containers
cd ../devops/docker-compose && \
docker-compose down

#Delete custom images
docker rmi auth-fastapi-2_broker
#workers
docker rmi auth-fastapi-2_email-worker auth-fastapi-2_db-worker 
#auth-server
docker rmi auth-fastapi-2_auth-server auth-fastapi-2_test-app
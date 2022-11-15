#Start db and broker
cd ../devops/docker-compose && \
#SET TEST_MODE to YES
sleep 6s && export TEST_MODE=YES && \
#start auth-server
docker-compose up -d auth-server

#Run TEST
docker exec -it auth-fastapi-2_auth-server_1 pytest tests

#Stop and delete container
docker-compose down

#auth-server
docker rmi auth-fastapi-2_auth-server auth-fastapi-2_test-app
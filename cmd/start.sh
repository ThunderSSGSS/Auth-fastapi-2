#Start all services
cd ../devops/docker-compose && \
docker-compose up -d db-server broker && \
sleep 6s && \
docker-compose up -d test-app email-worker db-worker auth-server nginx
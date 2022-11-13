#Start auth-server
cd ../devops/docker-compose && \
docker-compose up -d --scale auth-server=2 nginx
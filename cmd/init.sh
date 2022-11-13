#build base images

#build celery_run:v1
cd ./base_Dockerfiles/celery_run && \
docker build . -t celery_run:v1 && \

#build celery_sql_run:v1
cd ../celery_sql_run && \
docker build . -t celery_sql_run:v1 && \

#build fastapi_run:v1
cd ../fastapi_run && \
docker build . -t fastapi_run:v1
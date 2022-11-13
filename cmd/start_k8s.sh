#Build docker images
cd ../src/auth-server && \
docker build . -t auth-fastapi-2_auth-server && \
cd ../db-worker && \
docker build . -t auth-fastapi-2_db-worker && \
cd ../email-worker && \
docker build . -t auth-fastapi-2_email-worker && \

#LOAD IMAGES
#This commands is only for may case (I use minikube)
#Push image to minikube
minikube image load auth-fastapi-2_auth-server && \
minikube image load auth-fastapi-2_email-worker && \
minikube image load auth-fastapi-2_db-worker && \

#Create kubernetes components
cd ../../devops/kubernetes && \
kubectl create namespace auth-namespace && \
helm install -n auth-namespace db-worker base-app --values values_db-worker.yaml && \
helm install -n auth-namespace email-worker base-app --values values_email-worker.yaml && \
helm install -n auth-namespace auth-server base-app --values values_auth-server.yaml
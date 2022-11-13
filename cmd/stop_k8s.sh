#Stop and delete kubernetes all components
cd ../devops/kubernetes && \
kubectl delete namespace auth-namespace

#This commands is only for my case (I use minikube)
#Remove images from minikube
minikube ssh docker rmi auth-fastapi-2_auth-server
minikube ssh docker rmi auth-fastapi-2_email-worker
minikube ssh docker rmi auth-fastapi-2_db-worker

#Delete custom images
#workers
docker rmi auth-fastapi-2_email-worker auth-fastapi-2_db-worker 
#auth-server
docker rmi auth-fastapi-2_auth-server
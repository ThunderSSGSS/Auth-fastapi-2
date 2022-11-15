# Auth-fastapi-2 DEVELOPER DOCUMENTATION
This documentation is not finished.

## Requeriments
To understand this documentation you need to known:
- [Clean Arquitecture](https://betterprogramming.pub/the-clean-architecture-beginners-guide-e4b7058c1165);
- [Event driven Arquitecture](https://en.wikipedia.org/wiki/Event-driven_architecture).

## Diagrams:
- [Arquitecture](./Arquitecture.drawio), have the project arquitecture and packages;
- [Flows](./Flows.drawio), have the services flows.


## Running the project using the source code

#### Necessary
- [Docker](https://www.docker.com/) and Docker-Compose, to run containers;
- user with docker permission;

#### Optional
If you want run the project on kubernetes cluster, you need:
- [kubectl](https://kubernetes.io/docs/reference/kubectl/);
- [helm](https://helm.sh/).

## How to run
The project have 3 modes:
- **DevMode**, run all containers on docker, use port 8080 to receive http connections;
- **TestMode**, run containers on docker and make automatic test;
- **ProductionMode**, not finished, you need to change the service email-worker.

#### How to run (DevMode):
- Go to path [cmd](../../cmd/); 
- If is the first time that you running the project, run [init.sh](./cmd/init.sh).
- Run [start.sh](../../cmd/start.sh), to start all containers, use http port 8080;
- Run [stop.sh](../../cmd/stop.sh), stop all containers.

This mode creates automaticaly a admin user with email defined on [.env](../../devops/docker-compose/.env), variable: **ADMIN_USER_EMAIL**. Use the forget password flow to get the password.


### Comands
On path [cmd](../../cmd), I create some scripts to run the project.
- [dc.sh](../../cmd/dc.sh), shotcut of docker-compose comand;
- [init.sh](../../cmd/init.sh), used to init the project, will build the base docker images;
- [run_tests.sh](../../cmd/run_tests.sh), used to make automatic test (TestMode);
- [start_k8s.sh](../../cmd/start_k8s.sh), used to start the project on kubernetes cluster (DevMode);
- [stop_k8s.sh](../../cmd/stop_k8s.sh), used to stop the project on kubernetes cluster (DevMode);
- [start.sh](../../cmd/start.sh), used to start the project on docker (DevMode);
- [stop.sh](../../cmd/stop.sh), used to stop the project on docker (DevMode).


## DevInfos:
- Name: James Artur (Thunder);
- A DevOps and infrastructure enthusiastics.
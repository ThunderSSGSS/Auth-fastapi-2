# Auth-fastapi-2
This project is an Authentication provider.

## Used Tecnologies:
- [FastAPI](https://fastapi.tiangolo.com/);
- [PostgreSQL](https://www.postgresql.org/);
- [Docker](https://www.docker.com/) and Docker-Compose;
- [kubernetes](https://kubernetes.io/);
- [Rabbitmq](https://www.rabbitmq.com/);
- [Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html);
- [Redis](https://redis.io/).


## Requirements

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
- Go to path [cmd](./cmd); 
- If is the first time that you running the project, run [init.sh](./cmd/init.sh).
- Run [start.sh](./cmd/start.sh), to start all containers, use http port 8080;
- Run [stop.sh](./cmd/stop.sh), stop all containers.

This mode creates automaticaly a admin user with email defined on [.env](./devops/docker-compose/.env), variable: **ADMIN_USER_EMAIL**. Use the forget password flow to get the password.


### Comands
On path [cmd](./cmd), I create some scripts to run the project.
- [dc.sh](./cmd/dc.sh), shotcut of docker-compose comand;
- [init.sh](./cmd/init.sh), used to init the project;
- [run_tests.sh](./cmd/run_tests.sh), used to make automatic test (TestMode);
- [start_k8s.sh](./cmd/start_k8s.sh), used to start the project on kubernetes cluster (DevMode);
- [stop_k8s.sh](./cmd/stop_k8s.sh), used to stop the project on kubernetes cluster (DevMode);
- [start_server.sh](./cmd/start_server.sh), used to start auth-server containers (ProductionMode);
- [stop_server.sh](./cmd/stop_server.sh), used to stop auth-server containers (ProductionMode);
- [start_workers.sh](./cmd/start_workers.sh), used to start email-worker and db-worker containers (ProductionMode);
- [stop_workers.sh](./cmd/stop_workers.sh), used to stop email-worker and db-worker containers (ProductionMode);
- [start.sh](./cmd/start.sh), used to start the project on docker (DevMode);
- [stop.sh](./cmd/stop.sh), used to stop the project on docker (DevMode).


## Documentation
For more documentation: 
- Go to dir [user](./docs/user/), to get user documentation (how to use);
- Go to dir [dev](./docs/dev/), to get developer documentation.


## DevInfos:
- Name: James Artur (Thunder);
- A DevOps and infraestructure enthusiastics.
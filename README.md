# Auth-fastapi-2
This project is an Authentication and Authorization server for microservices.

### Used Tecnologies:
- [FastAPI](https://fastapi.tiangolo.com/);
- [PostgreSQL](https://www.postgresql.org/);
- [Docker](https://www.docker.com/) and Docker-Compose;
- [kubernetes](https://kubernetes.io/);
- [Rabbitmq](https://www.rabbitmq.com/);
- [Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html).

## How Run

### Using Docker-Compose:

Create the file .env:
```
COMPOSE_PROJECT_NAME=auth-fastapi-2

DB_SERVER=db-server
DB_NAME=auth
DB_USER=example
DB_PASSWORD=example
DB_PORT=5432

RABBITMQ_SERVER=broker
RABBITMQ_USER=example
RABBITMQ_PASSWORD=example
RABBITMQ_VHOST=default

SENDER_EMAIL=example_sender@outlook.com
SENDER_EMAIL_PASSWORD=example

ADMIN_USER_EMAIL=admin@admin.com

#HS256 Secret Key, string of 64 chars, you can gen using: openssl rand -hex 32
PRIVATE_KEY=17559258d3ac145d717dcafea3277fe82a3cb5d5bad01296925bdd9a2e0c3370

#AES-CBC Secret Key, string of 32 chars, you can gen using: openssl rand -hex 16
SECRET_KEY=a86a57ed41d9720bd481594917da2bca
```

And now, create the file docker-compose.yml:
```yaml
version: "3"
services:

  db-server:
    image: postgres:14.2-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}

  broker:
    image: rabbitmq:3.9.13-alpine
    environment:
      RABBITMQ_DEFAULT_USER: ${RABBITMQ_USER}
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
      RABBITMQ_DEFAULT_VHOST: ${RABBITMQ_VHOST}

  email-worker:
    image: thunderssgss/email-worker:v0.3.0
    environment:
      RABBITMQ_URI: amqp://${RABBITMQ_USER}:${RABBITMQ_PASSWORD}@${RABBITMQ_SERVER}/${RABBITMQ_VHOST}
      SENDER_EMAIL: ${SENDER_EMAIL}
      SENDER_EMAIL_PASSWORD: ${SENDER_EMAIL_PASSWORD}

  db-worker:
    image: thunderssgss/db-worker:v0.3.0
    environment:
      ADMIN_USER_EMAIL: ${ADMIN_USER_EMAIL}
      RABBITMQ_URI: amqp://${RABBITMQ_USER}:${RABBITMQ_PASSWORD}@${RABBITMQ_SERVER}/${RABBITMQ_VHOST}
      DATABASE_URI: ${DB_USER}:${DB_PASSWORD}@${DB_SERVER}/${DB_NAME}

  auth-server:
    image: thunderssgss/auth-server:v0.3.0
    environment:
      DATABASE_URI: ${DB_USER}:${DB_PASSWORD}@${DB_SERVER}/${DB_NAME}
      PRIVATE_KEY: ${PRIVATE_KEY}
      SECRET_KEY: ${SECRET_KEY}
      RABBITMQ_URI: amqp://${RABBITMQ_USER}:${RABBITMQ_PASSWORD}@${RABBITMQ_SERVER}/${RABBITMQ_VHOST}
    ports:
      - 8080:80
```

### Using Kubernets (Healm Chart):
**NOTE**: THE healm chart is not read

## How Work
This project uses [Event driven Arquitecture](https://en.wikipedia.org/wiki/Event-driven_architecture) with [Rabbitmq](https://www.rabbitmq.com/) as a message broker and 3 microservices:
- **auth-server** => the http server, runs the REST API;
- **db-worker** => the database worker, execute all transactions;
- **email-worker** => the email worker, send emails to users.

## Environment Variables
For simple tests, you can set only the required enviroment variables, but on production mode you must set more environment variables depends of your requirements.
<br>

### Auth-server ENVS

| Name | Default | Description | Required | 
|------|---------|-------------|:--------:|
| TEST_MODE | NO | Test mode; **please, don't set** | no |
| DATABASE_URI | null | Database uri. The format is: *username:password@hostname/db_name* | yes |
| RABBITMQ_URI | null | Rabbitmq uri. The format is: *amqp://username:password@hostname/vhost_name* | yes |
| EMAILS_QUEUE | auth_emails | The email-worker **WORKER_DEFAULT_QUEUE** | no |
| DB_TRANSACTIONS_QUEUE | auth_db_transactions | The db-worker **WORKER_DEFAULT_QUEUE** | no |
| JWT_ALGORITHM | HS256 | JWT signiture algorithm. You can change to **RS256**, but you need to set **PRIVATE_KEY** and **PUBLIC_KEY** ENVS | no |
| PRIVATE_KEY | null | JWT signiture algorithm private key | yes |
| PUBLIC_KEY | null | JWT signiture algorithm public key. You must set if the algorithm is **RS256** | no |
| SECRET_KEY | null | AES CBC secret key. Must be a string with 32 chars. Used to encrypt the JWT token | yes |
| ACCESS_TOKEN_EXP | 20 | Access token expiration minutes | no |
| REFRESH_TOKEN_EXP | 50 | Refresh token expiration minutes | no |
| RANDOM_EXP | 10 | Random number (sended to email) expiration minutes | no |
<br>

### Email-worker ENVS
| Name | Default | Description | Required | 
|------|---------|-------------|:--------:|
| RABBITMQ_URI | null | Rabbitmq uri. The format is: *amqp://username:password@hostname/vhost_name* | yes |
| WORKER_DEFAULT_QUEUE | auth_emails | The worker default queue name | no | 
| SENDER_EMAIL | null | The server email | yes |
| SENDER_EMAIL_PASSWORD | null | The server email password | yes |
<br>

### Db-worker ENVS
| Name | Default | Description | Required | 
|------|---------|-------------|:--------:|
| RABBITMQ_URI | null | Rabbitmq uri. The format is: *amqp://username:password@hostname/vhost_name* | yes |
| WORKER_DEFAULT_QUEUE | auth_db_transactions | The worker default queue name | no |
| ADMIN_USER_EMAIL | null | The ADMIN user email. If the server don't have admin user, it will create a admin user using this email | no |
| DATABASE_URI | null |Database uri. The format is: *username:password@hostname/db_name* | yes |
<br>


## More Documentation
For more documentation:
- Go to dir [dev](./docs/dev/), to get developer documentation.


## DevInfos:
- Name: James Artur (Thunder);
- A DevOps and infrastructure enthusiastics.
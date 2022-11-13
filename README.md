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
ss

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
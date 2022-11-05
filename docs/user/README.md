# Auth-fastapi-2 USER DOCUMENTATION

## Auth-Server ENVS
The auth-server can have many ENVS that can make the server works on differents modes:

- **TEST_MODE** => (default value: NO), indicate the test mode, please don't set this;
- **DATABASE_URI** => indicate the database uri: *username:password@hostname/db_name* ;
- **RABBITMQ_URI** => indicate the rabbitmq uri: *amqp://username:password@hostname/vhost_name* ;
- **EMAILS_QUEUE** => (default value: auth_emails) indicate the emails queue name;
- **DB_TRANSACTIONS_QUEUE** => (default value: auth_db_transactions) indicate the database transactions queue;
- **JWT_ALGORITHM** => (default value: HS256), indicate the jwt signiture algorithm. you change to RS256, but you need to set **PRIVATE_KEY** and **PUBLIC_KEY** ENVS;
- **PRIVATE_KEY** => indicate the **JWT_ALGORITHM** key;
- **PUBLIC_KEY** => (default value: none), indicate the public key if the algorithm was RS256;
- **SECRET_KEY** => indicate the AES CBC secret key, must be a string with 32 chars;
- **PASSWORD_SALT** => (default value: 1234567@), indicate the salt of hash password algorithm;
- **ACCESS_TOKEN_EXP** => (default value: 20), indicate the access token expiration minutes;
- **REFRESH_TOKEN_EXP** => (default value: 50), indicate the refresh token expiration;
- **RANDOM_EXP** => (default value: 10), indicate the random expiration time.


## Email-Worker ENVS
- **RABBITMQ_URI** => indicate the rabbitmq uri: *amqp://username:password@hostname/vhost_name* ;
- **WORKER_DEFAULT_QUEUE** => (default value: auth_emails) indicate the email-worker queue;
- **SENDER_EMAIL** => indicate the email;
- **SENDER_EMAIL_PASSWORD** => indicate the email password.


## Db-Worker ENVS
- **RABBITMQ_URI** => indicate the rabbitmq uri: *amqp://username:password@hostname/vhost_name* ;
- **WORKER_DEFAULT_QUEUE** => (default value: auth_db_transactions) indicate the db-worker queue;
- **ADMIN_USER_EMAIL** => (default value: none), if setted and don't have admin user, will create a admin user with the email;
- **DATABASE_URI** => indicate the database uri: *username:password@hostname/db_name* .


## ENVS THAT MUST BE SETTED ON PRODUCTION MODE

### Auth-Server
You can set many others envs, but these must be setted: 
- DATABASE_URI;
- RABBITMQ_URI;
- PRIVATE_KEY;
- SECRET_KEY;
- PASSWORD_SALT;
- ACCESS_TOKEN_EXP, (OPTIONAL) depends of your business rules;
- REFRESH_TOKEN_EXP, (OPTIONAL) depends of your busines rules;
- RANDOM_EXP, (OPTIONAL) depends of your business rules.

### Email-Worker
- RABBITMQ_URI;
- SENDER_EMAIL;
- SENDER_EMAIL_PASSWORD.

### DB-Worker
- RABBITMQ_URI;
- ADMIN_USER_EMAIL, must be a real and valid admin email;
- DATABASE_URI.



## DevInfos:
- Name: James Artur (Thunder);
- A DevOps and infraestructure enthusiastics.
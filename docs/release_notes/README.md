# Auth-fastapi-2 RELEASES

## RELEASES

| NAME | FEATURE |
|:----:|---------|
|  v0.4.0 | jwt token encryption and password salt improvements |
| v0.3.0 | Add randoms password salt |

### Release v0.4.0
This version add token encryption improvements.<br>
**NOTE**: If you are using the version v0.3.0, update the to v0.4.0 will only make the old access and refresh tokens invalid. All users needs to authenticate again.<br>
**NOTE2**: No changes were made on email-worker. The new db-worker will try to connect to database until start consuming the queue, if the connecting fail, will trying again (100 times with 6 seconds interval).


## DevInfos:
- Name: James Artur (Thunder);
- A DevOps and infrastructure enthusiastics.
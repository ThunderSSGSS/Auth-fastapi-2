#import uuid
from fastapi import APIRouter, Depends
from app import schemas
from app.dependencies import get_check_authorization_service
from app.internal.application.interfaces import IntraServiceInterface

router = APIRouter(tags=['Intra: authorization and status'])

@router.post("/authorization", response_model=schemas.CheckAuthorizationResponseSchema)
def check_authorization(data: schemas.CheckAuthorizationSchema,
	service: IntraServiceInterface = Depends(get_check_authorization_service)):
	"""
		## Check Authorization
		This route will check if the access token have the permissions and groups, if yes will return the token user_id and session_id, if not will return unauthorized error. 
		<p><b>Note</b>: The permissions and groups are optional if you set, the server will check if the access_token have the permissions and groups. If you don't set, the server will only return user_id and session_id.</p>
		<p><b>Note2</b>: This route is used for your microservices to check the token authorization.</p>
		<p><b>Note3</b>: On production, you must limit access to this route, only your services can access.</p>
	"""
	return service.start_service(data.dict())

@router.get("/status")
def get_status():
	"""
		## Get Status
		This route is used to check if the auth-server is working. Load balancers can use to check the server healthy.
	"""
	return {'status':'running'}
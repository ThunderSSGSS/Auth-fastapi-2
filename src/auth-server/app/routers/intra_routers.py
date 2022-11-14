#import uuid
from fastapi import APIRouter, Depends
from app import schemas
from app.dependencies import get_check_authorization_service
from app.internal.application.interfaces import IntraServiceInterface

router = APIRouter(tags=['Intra: authorization and status'])

@router.post("/authorization", response_model=schemas.CheckAuthorizationResponseSchema)
def check_authorization(data: schemas.CheckAuthorizationSchema,
	service: IntraServiceInterface = Depends(get_check_authorization_service)):
	return service.start_service(data.dict())

@router.get("/status")
def get_status():
	return {'status':'running'}
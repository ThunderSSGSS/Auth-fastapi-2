from fastapi import FastAPI, Depends
from .dependencies import check_admin_permission, check_normal_group
from .schemas import ResponseSchema

app = FastAPI()


@app.get("/admin_resource", response_model=ResponseSchema)
async def for_admin_users(user_info = Depends(check_admin_permission)):
    return user_info

@app.get("/normal_resource", response_model=ResponseSchema)
async def for_normal_group_users(user_info = Depends(check_normal_group)):
    return user_info
from fastapi import FastAPI, Depends
from .dependencies import check_admin_permission, check_normal_group
from .schemas import ResponseSchema

app = FastAPI()


@app.get("/admin_resource", response_model=ResponseSchema)
async def for_admin_users(user_info = Depends(check_admin_permission)):
    """
        ## For Admin Users
        This route will:
        * Check if the access token have the 'admin' permission;<br>
        * If yes, will return the user_id and session_id.<br>
        <p><b>Note</b>: This route make a http call to the 'Check Authorization' route of auth-server.</p>
    """
    return user_info

@app.get("/normal_resource", response_model=ResponseSchema)
async def for_normal_group_users(user_info = Depends(check_normal_group)):
    """
        ## For Normal Group Users
        This route will:
        * Check if the access token have the 'normal' group;<br>
        * If yes, will return the user_id and session_id.<br>
        <p><b>Note</b>: This route make a http call to the 'Check Authorization' route of auth-server.</p>
    """
    return user_info
from fastapi import FastAPI, Depends
from .dependencies import check_admin_permission


app = FastAPI()


@app.get("/resource")
async def test(user_info = Depends(check_admin_permission)):
    return user_info
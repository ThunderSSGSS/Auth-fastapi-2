from fastapi import FastAPI
#Routers
from .routers import auth_routers, admin_routers, intra_routers


async def async_main():
	async with engine.begin() as session:
		await session.run_sync(Base.metadata.create_all)


app = FastAPI()
# Auth routers
app.include_router(auth_routers.router_signup, prefix='/auth')
app.include_router(auth_routers.router_authenticate, prefix='/auth')
app.include_router(auth_routers.router_forget_password, prefix='/auth')
app.include_router(auth_routers.router_set_email, prefix='/auth')
app.include_router(auth_routers.router_others, prefix='/auth')

# Admin routers
app.include_router(admin_routers.router_user_crud, prefix='/admin')
app.include_router(admin_routers.router_permission_crud, prefix='/admin')
app.include_router(admin_routers.router_group_crud, prefix='/admin')
app.include_router(admin_routers.router_grant_permission, prefix='/admin')
app.include_router(admin_routers.router_grant_group, prefix='/admin')
app.include_router(admin_routers.router_session_mng, prefix='/admin')

# Intra routers
app.include_router(intra_routers.router, prefix='/intra')

"""
@app.on_event("startup")
async def startup():
	await async_main()

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()"""
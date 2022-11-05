from fastapi import FastAPI
#Routers
from .routers import auth_routers, admin_routers, intra_routers

async def async_main():
	async with engine.begin() as session:
		await session.run_sync(Base.metadata.create_all)


app = FastAPI()
app.include_router(auth_routers.router, prefix='/auth', tags=['Auth Services'])
app.include_router(admin_routers.router, prefix='/admin', tags=['Admin Services'])
app.include_router(intra_routers.router, prefix='/intra', tags=['Intra Services'])

"""
@app.on_event("startup")
async def startup():
	await async_main()

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()"""
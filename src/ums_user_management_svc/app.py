from fastapi import FastAPI
from src.ums_user_management_svc.routers.signup import router as signup_router
from src.ums_user_management_svc.routers.verification import router as verification_router

app = FastAPI()

app.include_router(signup_router, prefix='/signup')
app.include_router(verification_router, prefix='/verify')

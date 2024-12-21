from fastapi import FastAPI
from src.ums_user_management_svc.routers.signup import router as signup_router

app = FastAPI(debug=True)

# Include routers
app.include_router(signup_router)
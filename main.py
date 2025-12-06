from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from views.pages import router as pages_router
from api.user_authentication import router as auth_router
from config.general_config import GeneralConfig

# Create a FastAPI application instance
app = FastAPI()

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=GeneralConfig().SECRET_KEY,
    max_age=3600,  # Session expires in 1 hour
)

app.include_router(pages_router)
app.include_router(auth_router)


# Define a root endpoint
@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}


# Define a root endpoint

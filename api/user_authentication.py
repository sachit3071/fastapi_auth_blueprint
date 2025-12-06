from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from DAO.user_dao import UserDAO
import hashlib
from config.database import get_db_session
from api.auth_utils import AuthUtils
import secrets
from config.general_config import GeneralConfig
from config.logging_config import logger

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = GeneralConfig().SECRET_KEY
ALGORITHM = GeneralConfig().ALGORITHM


@router.post("/signup", response_class=RedirectResponse)
async def signup(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    form = await request.form()
    first_name = form.get("firstName")
    last_name = form.get("lastName")
    email = form.get("email")
    username = form.get("username")
    password = form.get("password")

    if not all([first_name, last_name, email, username, password]):
        response = RedirectResponse(
            url="/signup", status_code=status.HTTP_303_SEE_OTHER
        )
        response.session["error"] = "All fields are required"
        return response

    user_dao = UserDAO(session)
    user = await user_dao.get_user_by_filters(filters={"email": email})

    if user:
        response = RedirectResponse(
            url="/signup", status_code=status.HTTP_303_SEE_OTHER
        )
        response.session["error"] = "User with this email already exists"
        return response

    refresh_token = secrets.token_urlsafe(32)
    access_token = secrets.token_urlsafe(32)

    await user_dao.create_user(
        {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": username,
            "password": hashlib.sha256(password.encode()).hexdigest(),
            "refresh_token": refresh_token,
            "access_token": access_token,
        }
    )

    # Set success message
    request.session["success"] = "Account created successfully! Please sign in."

    auth_utils = AuthUtils(session)
    response = await auth_utils.redirect_with_new_tokens(request, email)
    return response


@router.post("/signin", response_class=RedirectResponse)
async def signin(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")

    if not all([email, password]):
        request.session["error"] = "Email and password are required"
        logger.info("Email and password are required")
        return RedirectResponse(url="/signin", status_code=status.HTTP_303_SEE_OTHER)

    auth_utils = AuthUtils(session)
    is_valid = await auth_utils.verify_password(
        email, hashlib.sha256(password.encode()).hexdigest()
    )

    if not is_valid:
        request.session["error"] = "Invalid email or password"
        logger.info("Invalid email or password")
        return RedirectResponse(url="/signin", status_code=status.HTTP_303_SEE_OTHER)

    response = await auth_utils.redirect_with_new_tokens(request, email)
    logger.info(f"Siginin Successful. Redirecting {email} to dashboard")
    return response


@router.get("/signout", response_class=RedirectResponse)
def signout(
    request: Request,
):
    response = RedirectResponse(url="/signin", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("email")
    return response


@router.get("/verify-username")
async def verify_username(
    username: str, session: AsyncSession = Depends(get_db_session)
):
    user_dao = UserDAO(session)
    user = await user_dao.get_user_by_filters(filters={"username": username})
    exists = user is not None
    return {"exists": exists}

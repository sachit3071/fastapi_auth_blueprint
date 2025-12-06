from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from DAO.user_dao import UserDAO
from fastapi.responses import RedirectResponse
from fastapi import status
import secrets
from config.general_config import GeneralConfig
from config.logging_config import log_function_call

SECRET_KEY = GeneralConfig().SECRET_KEY
ALGORITHM = GeneralConfig().ALGORITHM


class AuthUtils:
    @log_function_call
    def __init__(self, session: AsyncSession):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.session = session
        self.user_dao = UserDAO(session)

    @log_function_call
    async def redirect_with_new_tokens(self, request: Request, email: str):
        user = await self.user_dao.get_user_by_filters(filters={"email": email})

        if not user:
            request.session["error"] = "User not found"
            return RedirectResponse(
                url="/signin", status_code=status.HTTP_303_SEE_OTHER
            )

        refresh_token = secrets.token_urlsafe(32)
        access_token = secrets.token_urlsafe(32)

        await self.user_dao.update_user(
            filters={"email": email},
            user_data={"refresh_token": refresh_token, "access_token": access_token},
        )

        response = RedirectResponse(
            url=request.query_params.get("next", "/dashboard"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

        self.set_cookies(response, email, access_token, refresh_token)

        return response

    @log_function_call
    async def verify_password(self, email: str, password: str) -> bool:
        user = await self.user_dao.get_user_by_filters(filters={"email": email})
        if user is None:
            return False

        return password == user.password

    @log_function_call
    def set_cookies(
        self,
        response: RedirectResponse,
        email: str,
        access_token: str,
        refresh_token: str,
    ):
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=3600,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400 * 7,  # 7 days
        )
        response.set_cookie(
            key="email",
            value=email,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=86400 * 7,
        )

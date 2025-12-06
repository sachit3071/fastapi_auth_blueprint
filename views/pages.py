from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return get_template(request, "signup.html")


@router.get("/signin", response_class=HTMLResponse)
async def signin_page(request: Request):
    return get_template(request, "signin.html")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    # Get and clear flash messages
    if not authenticate_user(request):
        return RedirectResponse(url="/signin", status_code=status.HTTP_303_SEE_OTHER)
    return get_template(request, "dashboard.html")


def authenticate_user(request: Request):
    email = request.cookies.get("email")
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    if not all([email, access_token, refresh_token]):
        return False
    return True


def get_template(request: Request, template_name: str):
    email = request.cookies.get("email")
    error = request.session.pop("error", None)
    success = request.session.pop("success", None)

    return templates.TemplateResponse(
        template_name,
        {"request": request, "email": email, "error": error, "success": success},
    )

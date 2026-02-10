import src.utils.syspath

from datetime import date
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.utils.helper import list_files

from modules.overwatch.OverwatchController import OverwatchController

# Initialize Jinja2Templates globally
templates = Jinja2Templates(f"{src.utils.syspath.VIEW_DIR}/templates")

# Define the router
router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def get_staffing_plan(request: Request):
    overwatch_controller = OverwatchController()
    overwatch = overwatch_controller.get()

    css_files = list_files(src.utils.syspath.CSS_DIR, ".css")
    js_files = list_files(src.utils.syspath.JS_DIR, ".js")

    header = templates.TemplateResponse("layouts/header.html", {"request": request, "page_title": "Overwatch","css_files": css_files, "js_files": js_files}).body.decode("utf-8")
    content = templates.TemplateResponse("overwatch.html", {"request": request, "overwatch": overwatch}).body.decode("utf-8")
    footer = templates.TemplateResponse("layouts/footer.html", {"request": request}).body.decode("utf-8")

    # Render the main layout with header, content, and footer
    return templates.TemplateResponse("layouts/scaffolding.html", {
        "request": request,
        "header": header,
        "content": content,
        "footer": footer
    })
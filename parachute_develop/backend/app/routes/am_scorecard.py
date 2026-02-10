import src.utils.syspath
# import asyncio
import datetime
import json
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from src.utils.helper import list_files, annual_weeks
from modules.am_scorecard.AmScorecardController import AmScorecardController

# Initialize Jinja2Templates globally
templates = Jinja2Templates(f"{src.utils.syspath.VIEW_DIR}/templates")

# Define the router
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def get_am_scorecard(request: Request):
    weeks = json.loads(annual_weeks(2024).to_json(orient="records"))
    current_week = datetime.datetime.now().isocalendar()[1] - 1
    
    am_scorecard_controller = AmScorecardController()
    data = await am_scorecard_controller.get_am_scorecards() #returns data in a DataFrame
    columns = am_scorecard_controller.df_columns(data)
    data = am_scorecard_controller.df2xarray(data) #converting 2D dataframe into 3D xarray to hold cell style data
    data = am_scorecard_controller.apply_escape_class(data, columns, ["Huddle Completion %"]) #remove cell colors for all these columns

    css_files = list_files(src.utils.syspath.CSS_DIR, ".css")
    js_files = list_files(src.utils.syspath.JS_DIR, ".js")

    header = templates.TemplateResponse(
                "layouts/header.html",
                {
                    "request": request,
                    "page_title": f"AM Scorecard",
                    "css_files": css_files,
                    "js_files": js_files,
                },
            ).body.decode("utf-8")

    content = templates.TemplateResponse(
                "am_scorecard.html",
                {
                    "request": request,
                    "page_title": f"Area Manager Scorecard",
                    "weeks": weeks,
                    "current_week": current_week,
                    "columns": columns,
                    "data": data
                },
            ).body.decode("utf-8")

    footer = templates.TemplateResponse(
                "layouts/footer.html", {"request": request}
            ).body.decode("utf-8")

    # Render the main layout with header, content, and footer
    return templates.TemplateResponse(
        "layouts/scaffolding.html",
        {"request": request, "header": header, "content": content, "footer": footer},
    )

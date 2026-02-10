import sys
import os

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import src.utils.syspath
from pathlib import Path

# Now proceed with the imports
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from src.utils.helper import generate_header_routes

from routes.example import router as example_router
from routes.staffing_plan import router as staffing_plan_router
from routes.overwatch import router as overwatch_router
from routes.am_scorecard import router as am_scorecard_router

# Initialize the FastAPI app
app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost",  # Add your frontend URL here
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow all origins or specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to your templates directory
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).parent / "static")),
    name="static",
)


# Loops IMG(.ico only), CSS & JS directories and generates the routes dynamically
generate_header_routes(
    app,
    {
        "/images": (src.utils.syspath.IMG_DIR, ".ico"),
        "/css": (src.utils.syspath.CSS_DIR, ".css"),
        "/js": (src.utils.syspath.JS_DIR, ".js"),
    },
)


# Redirect main route
@app.get("/", response_class=RedirectResponse)
async def index():
    return RedirectResponse("/staffing_plan")


# Include sub package routes
app.include_router(example_router, prefix="/example", tags=["example"])
app.include_router(staffing_plan_router, prefix="/staffing_plan", tags=["staffing_plan"])
app.include_router(overwatch_router, prefix="/overwatch", tags=["overwatch"])
app.include_router(am_scorecard_router, prefix="/am_scorecard", tags=["am_scorecard"])

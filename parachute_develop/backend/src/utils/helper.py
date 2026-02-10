import pandas as pd

import os
from datetime import datetime, timedelta
from fastapi.responses import FileResponse


def get_dataframe_from_csv(file_path):
    return pd.read_csv(file_path)


def get_dataframe_from_excel(file_path):
    return pd.read_excel(file_path)


# Function to create routes dynamically for specified directories and file extensions
def generate_header_routes(app, file_settings):
    """
    Generates routes for specified directories and file types.

    Args:
        file_settings (dict): A dictionary where the key is the route prefix (e.g., "/css")
                              and the value is a tuple of (directory, file extension).
                              Example: {"/css": ("app/static/css", ".css")}
    """
    for route_prefix, (directory, extension) in file_settings.items():
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory '{directory}' not found!")

        # Loop through all files in the directory with the specified extension
        for file_name in os.listdir(directory):
            if file_name.endswith(extension):
                route_path = f"{route_prefix}/{file_name}"
                file_path = os.path.join(directory, file_name)

                # Create a route for each file
                @app.get(route_path, response_class=FileResponse)
                async def serve_file(file_path=file_path):
                    return FileResponse(file_path)


def list_files(directory, extension):
    """
    Lists all files with the given extension in the specified directory.

    Args:
        directory (str): The directory to search.
        extension (str): The file extension to filter by.

    Returns:
        list: A list of file paths relative to the static directory.
    """
    if not os.path.exists(directory):
        return []
    return [
        f"{directory.split('static/')[1]}/{file_name}"
        for file_name in os.listdir(directory)
        if file_name.endswith(extension)
    ]


def annual_weeks(year):
    start_time = datetime(year, 1, 1)
    start_time += timedelta(days=(6 - start_time.weekday()) % 7)
    start_time = start_time.replace(hour=6, minute=0, second=0)
    weeks = [{"name": (i+1), "start": start_time + timedelta(days=7*i), 
              "end": start_time + timedelta(days=7*(i+1)) - timedelta(seconds=1)}
             for i in range(53) if (start_time + timedelta(days=7*i)).year == year]
    return pd.DataFrame(weeks)
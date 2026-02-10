# # src/models/department.py
# import pandas as pd
# from typing import List
# from .area import Area

# class Department:
#     def __init__(self, name: str):
#         self.name = name
#         self.is_active = True
#         self.area_data = None
#         self.process_data = None
#         self.area_file_path = None
#         self.process_file_path = None
#         self.areas: List[Area] = []

#     def set_name(self, name):
#         self.name = name

#     def get_name(self):
#         return self.name

#     def set_is_active(self, is_active):
#         self.is_active = is_active

#     def get_is_active(self):
#         return self.is_active
    
#     def set_area_file_path(self, area_file_path):
#         """Sets the area file path and loads the data from the CSV file."""
#         self.area_file_path = area_file_path
#         self.area_data = pd.read_csv(area_file_path)

#     def get_area_file_path(self):
#         """Returns the current area file path."""
#         return self.area_file_path

#     def set_process_file_path(self, process_file_path):
#         """Sets the process file path and loads the data from the CSV file."""
#         self.process_file_path = process_file_path
#         self.process_data = pd.read_csv(process_file_path)

#     def get_process_file_path(self):
#         """Returns the current process file path."""
#         return self.process_file_path

#     def get_all_areas(self):
#         """Returns a DataFrame of all areas from the area CSV file."""
#         if self.area_data is not None:
#             return self.area_data
#         else:
#             raise ValueError("Area file path not set. Use set_area_file_path() to set the file path.")

#     def get_all_departments(self):
#         """Returns a DataFrame of all departments from the process code CSV file."""
#         if self.process_data is not None:
#             return self.process_data
#         else:
#             raise ValueError("Process file path not set. Use set_process_file_path() to set the file path.")

#     def add_area(self, area: Area):
#         """Adds multiple areas to the department."""
#         self.areas.extend([area])

#     def add_areas(self, areas: List[Area]):
#         """Adds multiple areas to the department."""
#         self.areas.extend(areas)

#     def delete_area_by_name(self, area_name):
#         """Deletes an area from the department by area name."""
#         self.areas = [area for area in self.areas if area.get_name() != area_name]

#     def clear_all_areas(self):
#         """Removes all areas from the department."""
#         self.areas.clear()

#     def __repr__(self):
#         return f"Department(name={self.name}, is_active={self.is_active}, area_data={self.area_data}, process_data={self.process_data}, area_file_path={self.area_file_path}, process_file_path={self.process_file_path})"
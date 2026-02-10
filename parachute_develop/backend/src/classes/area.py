# # src/models/area.py
# import pandas as pd
# from typing import List
# from .employee import Employee

# class Area:
#     def __init__(self, name):
#         self.name = name
#         self.is_active = None
#         self.data = None
#         self.file_path = None
#         self.employees: List[Employee] = []

#     def set_name(self, name):
#         self.name = name

#     def get_name(self):
#         return self.name

#     def set_is_active(self, is_active):
#         self.is_active = is_active

#     def get_is_active(self):
#         return self.is_active

#     def set_file_path(self, file_path):
#         """Sets the file path and loads the data from the CSV file."""
#         self.file_path = file_path
#         self.data = pd.read_csv(file_path)
    
#     def get_file_path(self):
#         return self.file_path
    
#     def get_all_areas(self):
#         """Returns a DataFrame of all areas from the CSV file."""
#         if self.data is not None:
#             return self.data
#         else:
#             raise ValueError("File path not set. Use set_file_path() to set the file path.")

#     def get_areas_by_department(self, department):
#         """Returns a list of areas for a given department."""
#         if self.data is not None:
#             return self.data[self.data['Department'] == department]['Area'].unique().tolist()
#         else:
#             raise ValueError("File path not set. Use set_file_path() to set the file path.")

#     def get_department_by_area(self, area):
#         """Returns the department(s) associated with a given area."""
#         if self.data is not None:
#             return self.data[self.data['Area'] == area]['Department'].unique().tolist()
#         else:
#             raise ValueError("File path not set. Use set_file_path() to set the file path.")

#     def add_employee(self, employee: Employee):
#         """Adds a single employee to the area."""
#         self.employees.append(employee)

#     def add_employees(self, employees: List[Employee]):
#         """Adds multiple employees to the area."""
#         self.employees.extend(employees)

#     def delete_employee_by_badge_id(self, badge_id):
#         """Deletes an employee from the area by badge ID."""
#         self.employees = [emp for emp in self.employees if emp.badge_id != badge_id]

#     def delete_employee_by_login(self, login):
#         """Deletes an employee from the area by login."""
#         self.employees = [emp for emp in self.employees if emp.login != login]

#     def get_employees_in_area(self):
#         """Returns a list of all employees in the area."""
#         return self.employees
    
#     def clear_all_employees(self):
#         """Removes all employees from the area."""
#         self.employees.clear()

#     def __repr__(self):
#         return f"Area(name={self.name}, is_active={self.is_active}, data={self.data}, file_path={self.file_path})"


# # # Example usage
# # area_obj = Area()
# # area_obj.set_name("Main Warehouse")
# # area_obj.set_is_active(True)

# # # Set up employees
# # emp1 = Employee(badge_id="12345", login="emp1_login", name="Employee One")
# # emp2 = Employee(badge_id="67890", login="emp2_login", name="Employee Two")

# # # Add employees to area
# # area_obj.add_employee(emp1)
# # area_obj.add_employees([emp2])

# # # Delete employee by badge ID
# # area_obj.delete_employee_by_badge_id("12345")

# # # Retrieve all employees in area
# # employees_in_area = area_obj.get_employees_in_area()
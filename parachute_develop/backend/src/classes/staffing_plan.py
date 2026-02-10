# # src/models/staffing_plan.py
# from typing import List
# from .department import Department

# class StaffingPlan:
#     def __init__(self, name: str, is_active: bool, date: str, shift: str):
#         self.name = name
#         self.is_active = is_active
#         self.date = date
#         self.shift = shift
#         self.departments: List[Department] = []

#     def add_department(self, department):
#         self.departments.append(department)

#     def __repr__(self):
#         return f"StaffingPlan(name={self.name}, is_active={self.is_active}, date={self.date}, shift={self.shift})"

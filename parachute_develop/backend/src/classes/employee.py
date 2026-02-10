# # src/models/employee.py
# from typing import List
# from .permission import Permission
# from .attendance import Attendance

# class Employee:
#     def __init__(self, name: str, is_active: bool, badge_id: str, login: str, title: str, homepath: str, shift: str):
#         self.name = name
#         self.is_active = is_active
#         self.badge_id = badge_id
#         self.login = login
#         self.title = title
#         self.homepath = homepath
#         self.shift = shift
#         self.permissions: List[Permission] = []
#         self.attendances: List[Attendance] = []

#     def add_permission(self, permission):
#         self.permissions.append(permission)

#     def add_attendance(self, attendance):
#         self.attendances.append(attendance)

#     def __repr__(self):
#         return f"Employee(name={self.name}, is_active={self.is_active}, title={self.title})"

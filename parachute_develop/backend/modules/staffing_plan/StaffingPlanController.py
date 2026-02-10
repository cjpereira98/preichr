import src.utils.syspath
import pandas as pd
import random
from pydantic import BaseModel
from typing import List, Optional
from faker import Faker
from datetime import date

# Import necessary modules from the project
from src.utils.helper import get_dataframe_from_csv

# Initialize Faker for generating random data
fake = Faker()

# Models for Area, Employee, Department, and StaffingPlan
class Area(BaseModel):
    name: str
    fhd_hc: int
    fhn_hc: int
    bhd_hc: int
    bhn_hc: int

class Employee(BaseModel):
    initials: str
    name: str
    employee_id: str
    status: str
    area: Area
    next_shift_area: Area

class Department(BaseModel):
    name: str
    employees: List[Employee]

class StaffingPlan(BaseModel):
    name: str
    date: str
    weekday: str
    departments: List[Department]
    filename: str

# Controller to manage the staffing plan logic
class StaffingPlanController:
    name: str

    def get_staffing_plan(self, input_date: Optional[date] = None):
        staffing_date = input_date.strftime("%Y/%m/%d") if input_date else date.today().strftime("%Y/%m/%d")
        weekday = input_date.strftime("%a") if input_date else date.today().strftime("%a")

        department_and_area = self.get_department_and_area()
        # employee_perms = self.get_employee_perms()
        employee_perms = self.filter_employees(self.get_employee_perms(), weekday, False)
        departments = []

        for department_name, group in department_and_area.groupby('Department'):
            department = Department(name=department_name, employees=[])

            # Create a dictionary to store areas for easy lookup
            areas_dict = {}
            for _, row in group.iterrows():
                area_name = row['Area']
                fhd_hc = row['FHD HC']
                fhn_hc = row['FHN HC']
                bhd_hc = row['BHD HC']
                bhn_hc = row['BHN HC']

                # Create an Area object for each area, and store it in the dictionary
                area = Area(
                    name=area_name,
                    fhd_hc=fhd_hc,
                    fhn_hc=fhn_hc,
                    bhd_hc=bhd_hc,
                    bhn_hc=bhn_hc
                )
                areas_dict[area_name] = area

            # Loop through each area and assign people to them
            for area_name, area in areas_dict.items():
                fhd_hc = area.fhd_hc  # Get the headcount for the FHD shift

                # Assign employees to this area based on the FHD headcount
                for _ in range(fhd_hc):
                    this_employee = self.get_employee(employee_perms)
                    employee_name = ' '.join(str(this_employee['User ID']).split(',')[::-1]).title()
                    employee = Employee(
                        name=employee_name,
                        initials=self.get_initials(employee_name),
                        employee_id=this_employee['Employee ID'],
                        status=area_name,
                        area=area,
                        next_shift_area=area,
                    )
                    department.employees.append(employee)

            # Sort employees within department by area name
            department.employees.sort(key=lambda employee: employee.area.name)

            departments.append(department)

        # Create StaffingPlan instance
        staffing_plan = StaffingPlan(
            name=staffing_date,
            date=staffing_date,
            weekday=weekday,
            departments=departments,
            filename=f"staffing_plan_{staffing_date}.csv"
        )

        return staffing_plan

    def get_employee(self, df):
        while True:
            sample_index = df.sample().index[0]
            sample_name = df.loc[sample_index, 'User ID']
            if pd.notna(sample_name) and sample_name != '':  # Check if it's not NaN and not empty
                return df.loc[sample_index]
    
    def get_initials(self, name):
        return name.split()[0][0].upper() + name.split()[-1][0].upper()

    def generate_hc(self):
        return random.randint(1, 5)

    def get_department_and_area(self):
        return get_dataframe_from_csv("src/models/department_area.csv")

    def get_employee_perms(self):
        return get_dataframe_from_csv("src/models/employee_perms.csv")

    def filter_employees(self, employees, weekday, is_met=False):
        filtered_employees = employees[(employees[weekday] == weekday) | (is_met & (employees[weekday] == '50'))]

        return filtered_employees
import src.utils.syspath
import pandas as pd
import random
from pydantic import BaseModel
from typing import List
from faker import Faker

# Import necessary modules from the project
from src.utils.helper import get_dataframe_from_csv
# from src.models.area import Area
# from src.models.department import Department

# Initialize Faker for generating random data
fake = Faker()

# Models for Area, Employee, and Department
class Area(BaseModel):
    name: str
    fhd_hc: int
    fhn_hc: int
    bhd_hc: int
    bhn_hc: int

class Employee(BaseModel):
    initials: str
    name: str
    status: str
    area: Area
    next_shift_area: Area

class Department(BaseModel):
    name: str
    persons: List[Employee]

# Controller to manage the staffing plan logic
class OverwatchController:
    name: str

    def get_staffing_plan(self):
        department_and_area = self.get_department_and_area()
        employee_perms = self.get_employee_perms()
        departments = []

        for department_name, group in department_and_area.groupby('Department'):
            department = Department(name=department_name, persons=[])
            
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
                areas_dict[area_name] = area  # Store by area name

            # Loop through each area and assign people to them
            for area_name, area in areas_dict.items():
                fhd_hc = area.fhd_hc  # Get the headcount for the FHD shift

                # Assign persons to this area based on the FHD headcount
                for _ in range(fhd_hc):
                    person_name = ' '.join(str(self.get_aa(employee_perms)).split(',')[::-1])
                    person = Employee(
                        name=person_name,
                        initials=self.get_initials(person_name),
                        status=area_name,  # Using FHD as the shift type here
                        area=area,  # Assign the area to the person
                        next_shift_area=area,  # Assuming the next shift is the same area
                    )
                    department.persons.append(person)

            # Sort persons within department by area name
            department.persons.sort(key=lambda person: person.area.name)
            departments.append(department)
        
        return departments
    
    def get_initials(self, name):
        return name.split()[0][0].upper() + name.split()[-1][0].upper()

    def get_aa(self, df):
        while True:
            sample = df.loc[df.sample().index[0], 'User ID']
            if pd.notna(sample) and sample != '':  # Check if it's not NaN and not empty
                return sample

    def generate_hc(self):
        return random.randint(1, 5)

    def get_department_and_area(self):
        return get_dataframe_from_csv("src/models/department_area.csv")

    def get_employee_perms(self):
        return get_dataframe_from_csv("src/models/employee_perms.csv")
    
    def get(self):
        return self.get_staffing_plan()

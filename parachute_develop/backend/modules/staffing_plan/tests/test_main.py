import sys
from pathlib import Path
import unittest
import pandas as pd

# Add the src and app directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent / "src"))
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent / "app"))

from models.area import Area
from models.department import Department
from utils.helper import load_area_data, load_department_data

class TestStaffingPlan(unittest.TestCase):

    def setUp(self):
        # Assuming helper functions load data and return Area/Department objects
        self.area_df = load_area_data("src/models/department_area.csv")
        self.department_df = load_department_data("src/models/department_process_code.csv")
        
        self.area = Area()
        self.department = Department("Inbound", True)

    def test_load_area_data(self):
        """Test loading of area data from CSV."""
        areas = self.area_df['Area'].unique()
        self.assertGreater(len(areas), 0, "Area data should be loaded successfully")

    def test_load_department_data(self):
        """Test loading of department data from CSV."""
        departments = self.department_df['Department'].unique()
        self.assertGreater(len(departments), 0, "Department data should be loaded successfully")

    def test_add_area_to_department(self):
        """Test adding an area to a department."""
        area = Area()
        area.set_name("North")
        self.department.add_area(area)
        self.assertIn(area, self.department.areas, "Area should be added to the department")

    def test_delete_area_from_department(self):
        """Test deleting an area from a department by area name."""
        area = Area()
        area.set_name("South")
        self.department.add_area(area)
        self.department.delete_area_by_name("South")
        self.assertNotIn(area, self.department.areas, "Area should be removed from the department")

if __name__ == "__main__":
    unittest.main()

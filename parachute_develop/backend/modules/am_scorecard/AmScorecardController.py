import src.utils.syspath
import subprocess
import io
import pandas as pd
import numpy as np
import xarray as xr
import numpy as np
import math
import datetime

from src.utils.midway import amzn_requests
from src.utils.helper import get_dataframe_from_csv, get_dataframe_from_excel, annual_weeks


# Controller to manage the business logic
class AmScorecardController:

    async def get_am_scorecards(self):
        # ✔️ Adapts Created: Positive & Negative accountability - https://adapt-reports-iad.amazon.com/#/dashboard/LOCKED-Area-Manager-Dashboard?_g=(refreshInterval:(display:Off,pause:!f,section:0,value:0),time:(from:now-1w%2Fw,mode:quick,to:now-1w%2Fw))&_a=(filters:!(),panels:!((col:1,id:LOCKED-Open-Feedback-by-Manager,row:4,size_x:9,size_y:5,type:visualization),(col:1,id:LOCKED-Above-and-Below-100%25,row:9,size_x:12,size_y:4,type:visualization),(col:1,id:LOCKED-All-Feedback-by-Type-by-Week,row:13,size_x:12,size_y:5,type:visualization),(col:1,id:LOCKED-Exempted-Feedback-by-Type-by-Week,row:18,size_x:12,size_y:5,type:visualization),(col:1,id:LOCKED-LC-Above-and-Below-by-process,row:36,size_x:12,size_y:4,type:visualization),(col:1,id:LOCKED-LC-Overall-%25-to-curve-by-process,row:40,size_x:12,size_y:3,type:visualization),(col:1,id:LOCKED-Productivity-Corrective-Action-by-Level-by-Week,row:23,size_x:12,size_y:5,type:visualization),(col:1,id:LOCKED-LC-Overall-%25-to-curve-by-function,row:43,size_x:12,size_y:5,type:visualization),(col:10,id:LOCKED-Feedback-by-emp.-type,row:4,size_x:3,size_y:5,type:visualization),(col:1,id:LOCKED-LC-Above-and-Below-by-Shift-Code,row:48,size_x:12,size_y:3,type:visualization),(col:1,id:LOCKED-LC-Above-and-Below-by-Function,row:51,size_x:12,size_y:4,type:visualization),(col:1,id:LOCKED-AM-Dashboard-Instructions,row:1,size_x:12,size_y:3,type:visualization),(col:1,id:LOCKED-Productivity-Status-by-Week,row:28,size_x:12,size_y:4,type:visualization),(col:1,id:LOCKED-Quality-Status-by-Week,row:32,size_x:12,size_y:4,type:visualization)),query:(query_string:(analyze_wildcard:!t,query:'Warehouse:%20SWF2')),title:'LOCKED%20-%20Area%20Manager%20Dashboard')
        # ✔️ RBI Completion - https://hs3c-tableau.aka.amazon.com/t/WHS/views/AUSTIN-InspectionsDashboard/InspectionsDataMining?%3Aembed=y&%3AisGuestRedirectFromVizportal=y&Site=SWF2
        # ✔️ Trailer Audit Completion - https://apollo-audit.corp.amazon.com/reporting/audit_execution_metrics?utf8=%E2%9C%93&department=22&start_date=2024-11-17+06%3A00&end_date=2024-11-24+06%3A00&commit=Search
        # ✔️  - IXD+ Inbound Fluid Unload Audit - https://apollo-audit.corp.amazon.com/reporting/results_by_audit?audit_type_id=19769&end_date=2024-11-24+06%3A00%3A00+-0500&start_date=2024-11-17+06%3A00%3A00+-0500
        # ✔️  - IXD+ Outbound Fluid Load Trailer Audit - https://apollo-audit.corp.amazon.com/reporting/results_by_audit?audit_type_id=19725&end_date=2024-11-24+06%3A00%3A00+-0500&start_date=2024-11-17+06%3A00%3A00+-0500
        # Engage % - 
        # Connection Scores (SLI/LBI)
        # ✔️ Huddle Completion
        # ✔️ OPTT - https://us-east-1.quicksight.aws.amazon.com/sn/dashboards/24d8fa53-d573-421f-a9b7-3ab354107ad9/sheets/24d8fa53-d573-421f-a9b7-3ab354107ad9_e75944fa-f76f-4de9-86a2-8fd1ee27313e?#
        

        current_week = datetime.datetime.now().isocalendar()[1]

        # ======================================= ADAPT ========================================
        adapt_feedback = (
            self.get_adapt_feedback()
            .rename(columns={"Top 0 Manager Name": "Full Name", "Count": "Adapts Created"})
        )

        adapt_feedback['Full Name'] = adapt_feedback['Full Name'].apply(self.reformat_name)

        # ======================================= RBI ========================================
        wanted_columns = ["Assignee", "Title", "Status", "% Non-Compliant", "Completion Week", "Due by (Local Time) ", "Complete Date (Local Time)"]
        rbi_compliance = (
            self.get_austin()[wanted_columns]
            .query("Status != 'CANCELLED'")
            .dropna(subset=["Assignee", "% Non-Compliant"])
            .sort_values(by=["Completion Week", "Title"], ascending=[False, True])
            .rename(columns={"Assignee": "Login"})
            .loc[lambda df: df['Title'].str.contains('RBI', case=False, na=False)]
            .pipe(self.count_non_compliance)
            .query("`Completion Week` == @current_week - 1")[["Login", "Non-Comp. Count"]]
            .rename(columns={"Non-Comp. Count": "RBI Non-Compliance"})
        )


        # ======================================= Trailer Audit ========================================
        wanted_columns = ["Created By", "Auditor Role"]
        ib_trailer_audit = (
            self.get_ib_trailer_audit()[wanted_columns]
            .rename(columns={"Created By": "Login"})
            .loc[lambda df: df['Auditor Role'].str.contains('AM', case=False, na=False)]
            .pipe(self.count_df)
            .rename(columns={"Audit Count": "Trailer Audit - Inbound"})
        )

        ob_trailer_audit = (
            self.get_ob_trailer_audit()[wanted_columns]
            .rename(columns={"Created By": "Login"})
            .loc[lambda df: df['Auditor Role'].str.contains('AM', case=False, na=False)]
            .pipe(self.count_df)
            .rename(columns={"Audit Count": "Trailer Audit - Outbound"})
        )

        # ======================================= OPTT ========================================
        wanted_columns = ["employee_login", "C&C Progression %", "Bronze Progression %", "Silver Progression %"]
        filtered_optt = (
            self.get_optt()[wanted_columns]
            .rename(columns={
                "employee_login": "Login",
                "C&C Progression %": "OPTT - C&C %",
                "Bronze Progression %": "OPTT - Bronze %",
                "Silver Progression %": "OPTT - Silver %"
            })
        )

        wanted_columns = ["Manager ID", "Training Status"]
        huddle_completion = (
            self.get_huddle_completion()[wanted_columns]
            .groupby("Manager ID")['Training Status']
            .agg(total_associates="count", completed_training="sum")
            .assign(completion_percentage=lambda x: (x["completed_training"] / x["total_associates"]))
            .reset_index()[["Manager ID", "completion_percentage"]]
            .rename(columns={"Manager ID": "Login"})
            .rename(columns={"completion_percentage": "Huddle Completion %"})
        )

        data = (
            pd.merge(self.get_ams(), adapt_feedback, on="Full Name", how="outer")
            .merge(rbi_compliance, on="Login", how="outer")
            .merge(ib_trailer_audit, on="Login", how="outer")
            .merge(ob_trailer_audit, on="Login", how="outer")
            .merge(filtered_optt, on="Login", how="outer")
            .merge(huddle_completion, on="Login", how="outer")
            .dropna(subset=["Login", "Full Name"])
            .pipe(self.percentize_columns)
            .assign(Engage=np.nan, **{
                "Connection - SLI": np.nan, 
                "Connection - LBI": np.nan})
            .fillna("-")
            .pipe(self.round_up)
        )

        return data

    def get_huddle_completion(self):
        return get_dataframe_from_csv("src/models/am_scorecard/huddle_completion.csv")

    def get_ib_trailer_audit(self):
        return get_dataframe_from_excel("src/models/am_scorecard/trailer_audit_inbound.xlsx")

    def get_ob_trailer_audit(self):
        return get_dataframe_from_excel("src/models/am_scorecard/trailer_audit_outbound.xlsx")
    
    def get_austin(self):
        return get_dataframe_from_csv("src/models/am_scorecard/austin_inspections_data.csv")

    def get_optt(self):
        return get_dataframe_from_csv("src/models/am_scorecard/optt_am.csv")
    
    def get_adapt_feedback(self):
        return get_dataframe_from_csv("src/models/am_scorecard/adapt_feedback.csv")

    def get_ams(self):
        return get_dataframe_from_csv("src/models/am_scorecard/area_managers.csv")
    
    def percentize_columns(self, df):
        for col in [col for col in df.columns if "%" in col]:
            df[col] = df[col].apply(lambda x: f"{round(x * 100)}%" if pd.notnull(x) else "N/A")
        return df
    
    def round_up(self, df):
        for col in df.columns:
            df[col] = df[col].apply(lambda x: math.ceil(x) if isinstance(x, float) else x)
        return df
    
    def reformat_name(self, name):
        parts = name.split(',')
        return f"{parts[1].strip()} {parts[0].strip()}" if len(parts) == 2 else name
    
    def count_non_compliance(self, df):
        return df[df["% Non-Compliant"] > 0].groupby(["Login", "Completion Week"]).size().reset_index(name="Non-Comp. Count")
    
    def count_df(self, df):
        return df.groupby(["Login"]).size().reset_index(name="Audit Count").astype({"Audit Count": "int"})

    def ispercentage(self, str):
        return str.endswith('%') and str[:-1].replace('.', '', 1).isdigit()

    def df2xarray(self, df):
        return self.prepare_data_for_template(df)
    
    def df_columns(self, df):
        return [{'name': col[0][0], 'class': col[0][1]} for col in self.prepare_column_for_template(df)] 
    
    def get_css_class(self, value):
        # if isinstance(value, (str)) and len(value) > 5: return "wide" # uncomment this if we want rotated column titles
        if isinstance(value, (int, float)):
            return "green" if value > 5 else "red"
        if isinstance(value, str) and value == "N/A" or self.ispercentage(value) and value != "100%":
            return "red"
        return "green" if self.ispercentage(value) and value == "100%" else ""

    def apply_escape_class(self, data, columns, escape_columns):
        escape_indices = {i for i, col in enumerate(columns) if col['name'] in escape_columns}
        return [
            [
                (value, f"{css_class} escape_color" if i in escape_indices else css_class)
                for i, (value, css_class) in enumerate(row)
            ]
            for row in data
        ]

    def get_css_header_class(self, value):
        # return "rotate" if value not in ["Login", "Full Name", "Department"] else "" # uncomment this if we want rotated column titles
        return ""

    def prepare_data_for_template(self, df):
        return [
            [(value, self.get_css_class(value)) for value in row]
            for row in df.values
        ]

    def prepare_column_for_template(self, df):
        return [
            [(column, self.get_css_header_class(column))]
            for column in df.columns
        ]

    async def fetch_something_passing_midway(self):
        url = "https://fclm-portal.amazon.com/reports/audit/timeOnTask?reportFormat=CSV&warehouseId=SWF2&startDate=2024%2F11%2F21&endDate=2024%2F11%2F22"

        response = amzn_requests(url)

        # If status code is not 200, run the shell command
        if response.status_code != 200:
            try:
                subprocess.run(["mwinit", "-o"], check=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to run 'mwinit -o'. Error: {e}") from e

        response.raise_for_status()  # Raise an error for unsuccessful responses
        
        return get_dataframe_from_csv(io.StringIO(response.text)) #returning csv content in a dataframe format
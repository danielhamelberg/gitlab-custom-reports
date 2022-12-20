import pandas as pd
from matplotlib import pyplot as plt
import requests

class ReportGenerator:
    def __init__(self, project_id, private_token):
        self.project_id = project_id
        self.private_token = private_token
        
    def generate_report(self):
        # Set the date range for the report
        start_date_2022 = pd.to_datetime("2022-01-01")
        end_date_2022 = pd.to_datetime("2022-12-31")
        start_date_2021 = pd.to_datetime("2021-01-01")
        end_date_2021 = pd.to_datetime("2021-12-31")

        # Set the base URL for the GitLab API
        base_url = "https://gitlab.com/api/v4/projects/{}/pipelines".format(self.project_id)
        
        # Set the headers for the API request
        headers = {
            "Private-Token": self.private_token
        }
        
        # Retrieve the pipelines for 2022
        params = {
            "created_after": start_date_2022.strftime("%Y-%m-%d"),
            "created_before": end_date_2022.strftime("%Y-%m-%d")
        }
        response = requests.get(base_url, headers=headers, params=params)
        pipelines_2022 = response.json()
        
        # Retrieve the pipelines for 2021
        params = {
            "created_after": start_date_2021.strftime("%Y-%m-%d"),
            "created_before": end_date_2021.strftime("%Y-%m-%d")
        }
        response = requests.get(base_url, headers=headers, params=params)
        pipelines_2021 = response.json()
        
        # Create a dataframe for the pipelines in 2022
        df_2022 = pd.DataFrame(pipelines_2022)
        
        # Create a dataframe for the pipelines in 2021
        df_2021 = pd.DataFrame(pipelines_2021)
        
        # Filter the dataframes to include only successful pipelines
        df_2022 = df_2022[df_2022["status"] == "success"]
        df_2021 = df_2021[df_2021["status"] == "success"]
        
        # Extract the STAGE and ENVIRONMENT variables from the variables column
        df_2022["STAGE"] = df_2022["variables"].apply(lambda x: x["STAGE"] if "STAGE" in x else "")
        df_2022["ENVIRONMENT"] = df_2022["variables"].apply(lambda x: x["ENVIRONMENT"] if "ENVIRONMENT" in x else "")
        df_2021["STAGE"] = df_2021["variables"].apply(lambda x: x["STAGE"] if "STAGE" in x else "")
        df_2021["ENVIRONMENT"] = df_2021["variables"].apply(lambda x: x["ENVIRONMENT"] if "ENVIRONMENT" in x else "")

    # Group the data by STAGE and ENVIRONMENT and count the number of successful pipelines
    grouped_2022 = df_2022.groupby(["STAGE", "ENVIRONMENT"]).size().reset_index(name="count")
    grouped_2021 = df_2021.groupby(["STAGE", "ENVIRONMENT"]).size().reset_index(name="count")

    # Merge the data for 2021 and 2022
    merged = pd.merge(grouped_2022, grouped_2021, on=["STAGE", "ENVIRONMENT"], suffixes=("_2022", "_2021"))

    # Calculate the percentage change in successful pipelines between 2021 and 2022
    merged["percent_change"] = ((merged["count_2022"] - merged["count_2021"]) / merged["count_2021"]) * 100

    # Export the data to a CSV file
    merged.to_csv("pipeline_report.csv", index=False)

    # Create a bar chart to compare the number of successful pipelines between 2021 and 2022
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(merged["STAGE"] + " - " + merged["ENVIRONMENT"], merged["count_2022"], label="2022")
    ax.bar(merged["STAGE"] + " - " + merged["ENVIRONMENT"], merged["count_2021"], label="2021")
    ax.legend()
    ax.set_ylabel("Number of Successful Pipelines")
    ax.set_xlabel("STAGE - ENVIRONMENT")
    ax.set_title("Successful Pipelines per STAGE and ENVIRONMENT")

    # Save the chart as an SVG file
    plt.savefig("pipeline_chart.svg")

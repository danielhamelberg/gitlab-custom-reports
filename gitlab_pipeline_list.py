"""
To use this class, you will need to pass in the project_id and private_token when creating an instance of the class. 
You can then call the list_pipelines method and pass in the start and end dates for the date range you want to retrieve pipelines for. 
The method will make a request to the GitLab API to retrieve the pipelines within the specified date range and print the pipeline ID 
and any pipeline variables that are not empty.

Usage example:

import datetime

gitlab = GitLabPipelineList(<project id>, "your_private_token")

# List pipelines created in the last 7 days
today = datetime.datetime.today()
start_date = today - datetime.timedelta(days=7)
end_date = today

gitlab.list_pipelines(start_date, end_date)
"""
import requests
from datetime import datetime, timedelta

class GitLabPipelineList:
    def __init__(self, project_id, private_token):
        self.project_id = project_id
        self.private_token = private_token
        self.base_url = "https://gitlab.com/api/v4/projects/{}/pipelines".format(self.project_id)
    
    def list_pipelines(self, start_date, end_date):
        headers = {
            "Private-Token": self.private_token
        }
        
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        params = {
            "created_after": start_date_str,
            "created_before": end_date_str
        }
        
        response = requests.get(self.base_url, headers=headers, params=params)
        pipelines = response.json()
        
        for pipeline in pipelines:
            print("Pipeline ID:", pipeline["id"])
            if "STAGE" in pipeline["variables"]:
                print("STAGE:", pipeline["variables"]["STAGE"])
            if "ENVIRONMENT" in pipeline["variables"]:
                print("ENVIRONMENT:", pipeline["variables"]["ENVIRONMENT"])

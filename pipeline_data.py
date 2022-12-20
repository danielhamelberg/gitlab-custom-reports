import os
import requests
import pandas as pd

class GitLabAPI:
    def __init__(self, base_url, private_token):
        self.base_url = base_url
        self.private_token = private_token
        self.headers = {'Private-Token': self.private_token}

    def list_pipeline_ids(self, project_id, start_date, end_date):
        # API endpoint for getting all pipelines in a project
        endpoint = f"{self.base_url}/api/v4/projects/{project_id}/pipelines"

        # Query parameters to filter pipelines by date range
        params = {
            'created_after': start_date,
            'created_before': end_date
        }

        # Make GET request to the API endpoint
        response = requests.get(endpoint, params=params, headers=self.headers)

        # Extract the pipeline IDs from the response
        pipeline_ids = [pipeline['id'] for pipeline in response.json()]

        return pipeline_ids

    def get_pipeline_variables(self, project_id, pipeline_id):
        # API endpoint for getting pipeline variables
        endpoint = f"{self.base_url}/api/v4/projects/{project_id}/pipelines/{pipeline_id}/variables"

        # Make GET request to the API endpoint
        response = requests.get(endpoint, headers=self.headers)

        # Extract the variables from the response
        variables = {variable['key']: variable['value'] for variable in response.json()}

        return variables

class PipelineData:
    def __init__(self, gitlab_api, project_id, start_date, end_date):
        self.gitlab_api = gitlab_api
        self.project_id = project_id
        self.start_date = start_date
        self.end_date = end_date

        # Get the pipeline IDs within the specified date range
        self.pipeline_ids = self.gitlab_api.list_pipeline_ids(self.project_id, self.start_date, self.end_date)

        # Initialize an empty map to store the pipeline variables
        self.pipeline_variables = {}

        # Iterate over the pipeline IDs and get the variables for each pipeline
        for pipeline_id in self.pipeline_ids:
            variables = self.gitlab_api.get_pipeline_variables(self.project_id, pipeline_id)
            self.pipeline_variables[pipeline_id] = variables

    def to_dataframe(self):
        # Convert the map of pipeline variables to a Pandas Dataframe
        df = pd.DataFrame.from_dict(self.pipeline_variables, orient='index')
        return df
        
"""
To use these classes, you would first need to instantiate a GitLabAPI object with your GitLab base URL and private token. Then, you can use this object to create a PipelineData object, which will use the GitLabAPI object to retrieve the pipeline IDs and variables, store them in a map, and then convert them to a Pandas Dataframe.
"""

token = os.environ("GITLAB_API_TOKEN")
project_id = os.environ("GITLAB_PROJECT_ID")
since = os.environ("START_DATE")
until = os.environ("END_DATE")

# Instantiate a GitLabAPI object
gitlab_api = GitLabAPI(base_url='https://gitlab.com', private_token=token)

# Instantiate a PipelineData object
pipeline_data = PipelineData(gitlab_api=gitlab_api, project_id=project_id, start_date=since, end_date=until)

# Get the Pandas Dataframe
df = pipeline_data.to_dataframe()

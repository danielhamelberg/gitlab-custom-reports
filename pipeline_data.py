import os
import requests
import pandas as pd
logging
from matplotlib import pyplot as plt

"""
To use these classes, you would first need to instantiate a GitLabAPI object with your GitLab base URL and private token. Then, you can use this object to create a PipelineData object, which will use the GitLabAPI object to retrieve the pipeline IDs and variables, store them in a map, and then convert them to a Pandas Dataframe.
"""

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

        # Check if the response is successful
        if response.status_code == 200:
            # Extract the pipeline IDs from the response
            pipeline_ids = [pipeline['id'] for pipeline in response.json()]
            return pipeline_ids
        else:
            # Handle unexpected response
            raise Exception("Unexpected response from API")

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

        # Remove duplicate pipeline IDs
        self.pipeline_ids = list(set(self.pipeline_ids))

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

token = os.getenv("GITLAB_API_TOKEN")
project_id = os.getenv("GITLAB_PROJECT_ID")

# Instantiate a GitLabAPI object
gitlab_api = GitLabAPI(base_url='https://gitlab.com', private_token=token)

# Function to instantiate a PipelineData object for Q4 of both 2021 and 2022
def create_pipeline_data(project_id, since, until):
    # Instantiate a PipelineData object
    pipeline_data = PipelineData(gitlab_api, project_id, since, until)

    # Get the pipeline data
    pipeline_data.get_data()

    # Return the PipelineData object
    return pipeline_data

# Get pipeline data for Q4 in 2021
q4_2021_pipeline_data = create_pipeline_data(project_id, '2021-10-01', '2021-12-31')

# Get pipeline data for Q4 in 2022
q4_2022_pipeline_data = create_pipeline_data(project_id, '2022-10-01', '2022-12-31')

# Create a single dataframe of the pipeline data
df = q4_2021_pipeline_data.dataframe.append(q4_2022_pipeline_data.dataframe)

# Plot correlation matrix
corr = df.corr()

f, ax = plt.subplots(figsize=(10, 8))
ax = plt.imshow(corr, cmap='RdBu', interpolation='nearest')
plt.colorbar(ax)

# Set the labels
labels = [x for x in corr.columns]
ax.set_xticks(range(len(labels)))
ax.set_yticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.set_yticklabels(labels)

plt.title('Correlation Matrix')
plt.xlabel('Variables')
plt.ylabel('Variables')

plt.show()

# export svg
plt.savefig('correlation_matrix.svg')

# Perform additional statistical analysis
df.describe()
df.info()
df.corr()
df.agg(['mean', 'std', 'min', 'max'])

# Create a graph showing % growth month to month, week to week and quarter to quarter for 2021 and 2022.
# Create date column
df['date'] = pd.to_datetime(df['date'])

# Add year and quarter columns
df['year'] = df['date'].dt.year
df['quarter'] = df['date'].dt.quarter

# Calculate month to month growth
monthly_growth = df.groupby('date')['value'].sum()
monthly_growth_pct = monthly_growth.pct_change()

# Calculate week to week growth
weekly_growth = df.groupby(df['date'].dt.week)['value'].sum()
weekly_growth_pct = weekly_growth.pct_change()

# Calculate quarter to quarter growth
quarterly_growth = df.groupby('quarter')['value'].sum()
quarterly_growth_pct = quarterly_growth.pct_change()

# Plot the graphs
f, ax = plt.subplots(figsize=(10, 8))

# Month to month growth
ax.plot(monthly_growth_pct, label="Monthly Growth", color='green')

# Week to week growth
ax.plot(weekly_growth_pct, label="Weekly Growth", color='blue')

# Quarter to quarter growth
ax.plot(quarterly_growth_pct, label="Quarterly Growth", color='red')

# Set the labels
ax.set_title("Growth Rates")
ax.set_xlabel("Time")
ax.set_ylabel("Growth (%)")
ax.legend()

# Save the plot
plt.savefig('growth_rates.png')

# Analyse day of the week with the most pipelines in 2021 and in 2022 and create a separate comparison
# Create day of week column
df['day_of_week'] = df['date'].dt.day_name()

# Get data for 2021
df_2021 = df[df['year'] == 2021]

# Calculate pipelines by day of week in 2021
pipelines_by_day_2021 = df_2021.groupby('day_of_week')['value'].sum()

# Get data for 2022
df_2022 = df[df['year'] == 2022]

# Calculate pipelines by day of week in 2022
pipelines_by_day_2022 = df_2022.groupby('day_of_week')['value'].sum()

# Plot the graphs
f, ax = plt.subplots(figsize=(10, 8))

# Pipelines by day of week in 2021
ax.plot(pipelines_by_day_2021, label="2021", color='green')

# Save the graph
plt.savefig('pipelines_by_day_2021.png')

# Pipelines by day of week in 2022
ax.plot(pipelines_by_day_2022, label="2022", color='blue')

# Save the graph
plt.savefig('pipelines_by_day_2022.png')

# Set the labels
ax.set_title("Pipelines by Day of Week")
ax.set_xlabel("Day of Week")
ax.set_ylabel("Number of Pipelines")
ax.legend()

# Save the graph
plt.savefig('pipelines_by_day.png')

# Create a graph showing the month, week and day with most pipelines
# For both 2021 and 2022 as well as over 2021 and 2022 combined
# Save each graph with a unique and descriptive filename

# For 2021
# Calculate pipelines by month in 2021
pipelines_by_month_2021 = df_2021.groupby(df_2021['date'].dt.month)['value'].sum()

# Calculate pipelines by week in 2021
pipelines_by_week_2021 = df_2021.groupby(df_2021['date'].dt.week)['value'].sum()

# Calculate pipelines by day of week in 2021
pipelines_by_day_2021 = df_2021.groupby(df_2021['date'].dt.day)['value'].sum()

# Plot the graphs
f, ax = plt.subplots(figsize=(10, 8))

# Pipelines by month in 2021
ax.plot(pipelines_by_month_2021, label="Monthly", color='green')

# Save the graph
plt.savefig('pipelines_by_month_2021.png')

# Pipelines by week in 2021
ax.plot(pipelines_by_week_2021, label="Weekly", color='blue')

# Save the graph
plt.savefig('pipelines_by_week_2021.png')

# Pipelines by day of week in 2021
ax.plot(pipelines_by_day_2021, label="Daily", color='red')

# Save the graph
plt.savefig('pipelines_by_day_2021.png')

# Set the labels
ax.set_title("Pipelines by Date Unit in 2021")
ax.set_xlabel("Date Unit")
ax.set_ylabel("Number of Pipelines")
ax.legend()

# Save the graph
plt.savefig('pipelines_by_date_unit_2021.png')

# For 2022
# Calculate pipelines by month in 2022
pipelines_by_month_2022 = df_2022.groupby(df_2022['date'].dt.month)['value'].sum()

# Calculate pipelines by week in 2022
pipelines_by_week_2022 = df_2022.groupby(df_2022['date'].dt.week)['value'].sum()

# Calculate pipelines by day of week in 2022
pipelines_by_day_2022 = df_2022.groupby(df_2022['date'].dt.day)['value'].sum()

# Plot the graphs
f, ax = plt.subplots(figsize=(10, 8))

# Pipelines by month in 2022
ax.plot(pipelines_by_month_2022, label="Monthly", color='green')

# Save the graph
plt.savefig('pipelines_by_month_2022.png')

# Pipelines by week in 2022
ax.plot(pipelines_by_week_2022, label="Weekly", color='blue')

# Save the graph
plt.savefig('pipelines_by_week_2022.png')

# Pipelines by day of week in 2022
ax.plot(pipelines_by_day_2022, label="Daily", color='red')

# Save the graph
plt.savefig('pipelines_by_day_2022.png')

# Set the labels
ax.set_title("Pipelines by Date Unit in 2022")
ax.set_xlabel("Date Unit")
ax.set_ylabel("Number of Pipelines")
ax.legend()

# Save the graph
plt.savefig('pipelines_by_date_unit_2022.png')

# For 2021 and 2022
# Calculate pipelines by month in 2021 and 2022
pipelines_by_month = df.groupby(df['date'].dt.month)['value'].sum()

# Calculate pipelines by week in 2021 and 2022
pipelines_by_week = df.groupby(df['date'].dt.week)['value'].sum()

# Calculate pipelines by day of week in 2021 and 2022
pipelines_by_day = df.groupby(df['date'].dt.day)['value'].sum()

# Plot the graphs
f, ax = plt.subplots(figsize=(10, 8))

# Pipelines by month in 2021 and 2022
ax.plot(pipelines_by_month, label="Monthly", color='green')

# Save the graph
plt.savefig('pipelines_by_month.png')

# Pipelines by week in 2021 and 2022
ax.plot(pipelines_by_week, label="Weekly", color='blue')

# Save the graph
plt.savefig('pipelines_by_week.png')

# Pipelines by day of week in 2021 and 2022
ax.plot(pipelines_by_day, label="Daily", color='red')

# Save the graph
plt.savefig('pipelines_by_day.png')

# Set the labels
ax.set_title("Pipelines by Date Unit in 2021 and 2022")
ax.set_xlabel("Date Unit")
ax.set_ylabel("Number of Pipelines")
ax.legend()

# Save the graph
plt.savefig('pipelines_by_date_unit.png')

# Save the dataframe to a csv file
df.to_csv('pipeline_data.csv')

"""
Docs

GitLabAPI:

The GitLabAPI class provides methods for interacting with the GitLab API. It is initialized with a base URL and private token, and provides methods for retrieving lists of pipeline IDs and pipeline variables.

Methods:
__init__(gitlab_api, project_id, start_date, end_date):
This is the constructor for the PipelineData class. It takes four parameters, gitlab_api, project_id, start_date, and end_date, and stores them in instance variables. It then uses the gitlab_api to get the pipeline IDs between the specified date range and stores them in an instance variable. It also initializes an empty map to store the pipeline variables.

PipelineData:

The PipelineData class provides methods for interacting with the data retrieved from the GitLab API. It is initialized with a GitLabAPI object, a project ID, and a date range, and provides methods for retrieving a list of pipeline IDs and a map of pipeline variables within the specified date range. It also includes a method for converting the pipeline variables map to a Pandas Dataframe.

Methods:
__init__(base_url, private_token):
This is the constructor for the GitLabAPI class. It takes two parameters, base_url and private_token, and stores them in instance variables. It also creates an instance variable, headers, which is a dictionary with the private token as the key.

list_pipeline_ids(project_id, start_date, end_date):
This method takes three parameters, project_id, start_date, and end_date, and returns a list of pipeline IDs between the specified date range. 

get_pipeline_variables(project_id, pipeline_id):
This method takes two parameters, project_id and pipeline_id, and returns a dictionary of the pipeline variables.

to_dataframe():
This method converts the map of pipeline variables to a Pandas Dataframe.

GitLab: 
.gitlab-ci.yml usage example for PipelineData:

# Define variables to be used in the pipeline
variables:
  BRANCH: develop
  START_DATE: "2020-01-01"
  END_DATE: "2020-02-01"

# Define stages for the pipeline
stages:
  - get_pipeline_data

# Define job to get pipeline data
get_pipeline_data:
  stage: get_pipeline_data
  script:
    - export GITLAB_API_TOKEN=$PRIVATE_TOKEN
    - export GITLAB_PROJECT_ID=$CI_PROJECT_ID
    - export START_DATE=$START_DATE
    - export END_DATE=$END_DATE
    - python get_pipeline_data.py
  rules:
    - when: $BRANCH
  artifact:
    paths:
      - pipeline_data.csv
    expire_in: 7 days
"""

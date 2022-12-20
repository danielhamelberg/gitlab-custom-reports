import datetime

def main() {
  project_id = os.environ("GITLAB_PROJECT_ID")
  token = os.environ("GITLAB_API_TOKEN")
  gitlab = GitLabPipelineList(project_id, token)

  # List pipelines created in the last 7 days
  today = datetime.datetime.today()
  start_date = today - datetime.timedelta(days=7)
  end_date = today

  gitlab.list_pipelines(start_date, end_date)
}

from github import Github
import yaml


with open("secrets.yml", "r") as f:
    config = yaml.load(f, yaml.BaseLoader)
    github_token = config['github-token']

repo = Github(github_token).get_repo("enjoy301/plato-auto-attendance-in-github-action")

#repo.create_issue(title="This is a new issue", body="This is the issue body")
opened_issues = repo.get_issues(state='open')
for issue in opened_issues:
    print(issue.number)

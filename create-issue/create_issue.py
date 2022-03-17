from github import Github
import yaml


class Issue:
    def __init__(self):
        self.repo = None
        self.github_token = None
        self.opened_videos = list()
        self.to_open_videos = list()

    def get_github_token(self):
        with open("../secrets.yml") as f:
            config = yaml.load(f, yaml.BaseLoader)
            self.github_token = config['github-token']

    def create_instance(self):
        self.repo = Github(self.github_token).get_repo("enjoy301/plato-auto-attendance-in-github-action")

    def get_open_issue(self):
        open_issues = self.repo.get_issues(state='open')
        for issue in open_issues:
            for row in issue.body.split('\n'):
                video_name = row.strip()
                self.opened_videos.append(video_name)

    def check_to_open_issue(self, non_watched_videos):
        for video in non_watched_videos:
            if video not in self.opened_videos:
                self.to_open_videos.append(video)

    def open_issue(self):
        issue_body = '\n'.join(self.to_open_videos)
        print(issue_body)

    def main(self, non_watched_videos):
        self.get_github_token()
        self.create_instance()
        self.get_open_issue()
        self.check_to_open_issue(non_watched_videos)
        self.open_issue()

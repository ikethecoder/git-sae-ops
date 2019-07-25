
from clients.gitlab_api import GitlabAPI

class Rename():
    def __init__(self, config):
        self.projectsc_host = config['projectsc']['host']
        self.projectsc_token = config['projectsc']['token']
        self.github_token = config['github']['token']
        self.git_user = config['git_user']

    def rename (self, project_name, new_name):
        glapi = GitlabAPI(self.projectsc_host, self.projectsc_token)

        namespace = glapi.get_group("shares")
        project_shares = glapi.get_project(namespace.id, project_name)
        project_shares.name = new_name
        project_shares.path = new_name

        namespace = glapi.get_group("ocwa-checkpoint")
        project_checkpoint = glapi.get_project(namespace.id, project_name)
        project_checkpoint.name = new_name
        project_checkpoint.path = new_name

        project_shares.save()
        project_checkpoint.save()

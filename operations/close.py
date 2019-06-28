
from clients.git_api import GitAPI
from clients.file_api import FileUtils
from clients.gitlab_api import GitlabAPI

class Close():
    def __init__(self, config):
        self.projectsc_host = config['projectsc']['host']
        self.projectsc_token = config['projectsc']['token']
        self.github_token = config['github']['token']
        self.git_user = config['git_user']

    def close_export (self, repoName, branch):
        glapi = GitlabAPI(self.projectsc_host, self.projectsc_token)

        checkpoint = glapi.create_get_group("ocwa-checkpoint")
        cpRepo = glapi.get_project(checkpoint, repoName)

        glapi.delete_branch(cpRepo.id, "%s-outgoing" % branch)

        mr = glapi.get_merge_request (cpRepo.id, "%s-outgoing" % branch, "%s" % branch, None, ['ocwa-export'])

        if mr is not None:
            glapi.close_merge(mr)


    def close_import (self, repoName, branch):
        glapi = GitlabAPI(self.projectsc_host, self.projectsc_token)

        checkpoint = glapi.create_get_group("ocwa-checkpoint")
        cpRepo = glapi.get_project(checkpoint, repoName)

        glapi.delete_branch(cpRepo.id, "%s-incoming" % branch)

        mr = glapi.get_merge_request (cpRepo.id, "%s-incoming" % branch, "%s" % branch, None, ['ocwa-import'])

        if mr is not None:
            glapi.close_merge(mr)


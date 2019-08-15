
from clients.git_api import GitAPI
from clients.file_api import FileUtils
from clients.gitlab_api import GitlabAPI

import logging
log = logging.getLogger(__name__)

class RequestImport():
    def __init__(self, config):
        self.projectsc_host = config['projectsc']['host']
        self.projectsc_token = config['projectsc']['token']
        self.github_token = config['github']['token']
        self.git_user = config['git_user']

    def run (self, repoName, importUrl, branch):
        glapi = GitlabAPI(self.projectsc_host, self.projectsc_token)

        self.init_pri_branch(repoName, branch)

        checkpoint = glapi.create_get_group("ocwa-checkpoint")

        if glapi.has_branch (checkpoint, repoName, "%s-incoming" % branch):
            raise Exception("Import request rejected.  Branch '%s' already exists." % ("%s-incoming" % branch))

        # tgit = self.prep_checkpoint_from_internal (repoName, branch, branch)

        # Source
        cpRepo = glapi.get_project(checkpoint, repoName)
        cpRepoId = cpRepo.id

        sgit = self.prep_external_repo(importUrl, branch)
        commitRef = sgit.head_commit()

        # Target (Temporary incoming branch based on the prepped branch)
        tgit = GitAPI(cpRepo.http_url_to_repo, self.projectsc_token)
        tgit.checkout("%s" % branch)
        tgit.checkout_new("%s-incoming" % branch)
        tgit.info()
        tgit.set_user(self.git_user['username'], self.git_user['email'])

        # Source and target should both have the SRE repo as base
        # Source should also have a latest file copy from external

        # Do a full copy from source to target
        fileutils = FileUtils()
        fileutils.copytree (sgit.dir(), tgit.dir())
        fileutils.sync_deletions (sgit.dir(), tgit.dir(), ["/.gitlab-ci.yml"])

        if len(tgit.has_changes()) == 0:
            print("-- Exiting.  No changes to import.")
            return None

        tgit.commit_and_push("%s-incoming" % branch, "Merged external changes (%s)" % commitRef.hexsha[0:7])

        return glapi.create_get_merge_request (cpRepoId, "Import Request (%s)" % commitRef.hexsha[0:7], "%s-incoming" % branch, "%s" % branch, None, ['ocwa-import'])

    def prep_projectsc_repo (self, url, branch):

        git = GitAPI(url, self.projectsc_token)
        git.info()
        git.checkout(branch)
        return git

    def prep_external_repo (self, url, branch):

        try:
            git = GitAPI(url, self.github_token)
            git.info()
            git.checkout(branch)
            return git
        except BaseException as ex:
            err = str(ex).replace('oauth2', "*****").replace(self.github_token, "*****")
            log.info('{0:30} {1}'.format('prep_external_repo', err))
            raise Exception("There was a problem accessing %s at %s.  Please check there is access, repo and branch exists. (%s)" % (branch, url, err))

    def init_pri_branch (self, repoName, branch):
        glapi = GitlabAPI(self.projectsc_host, self.projectsc_token)

        checkpoint = glapi.create_get_group("ocwa-checkpoint")
        repo = glapi.create_get_project(checkpoint, repoName)


        ciYaml = 'scanjob:\n   script: ocwa-scanner\n'
        glapi.create_get_branch (checkpoint, repoName, branch, 'private')
        glapi.protect_branch(repo, branch)
        glapi.add_file(repo, branch, '.gitlab-ci.yml', ciYaml)

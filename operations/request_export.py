
from clients.git_api import GitAPI
from clients.file_api import FileUtils
from clients.gitlab_api import GitlabAPI

class RequestExport():
    def __init__(self, config):
        self.projectsc_host = config['projectsc']['host']
        self.projectsc_token = config['projectsc']['token']
        self.github_token = config['github']['token']
        self.git_user = config['git_user']

    def run (self, repoName, importUrl, branch):
        glapi = GitlabAPI(self.projectsc_host, self.projectsc_token)

        checkpoint = glapi.create_get_group("ocwa-checkpoint")

        self.init_pri_branch(repoName, branch)

        if glapi.has_branch (checkpoint, repoName, "%s-incoming" % branch):
            raise Exception("Import request rejected.  Branch '%s' already exists." % ("%s-incoming" % branch))

        #tgit = self.prep_checkpoint_from_external(repoName, importUrl, branch, branch, self.github_token)

        # Source (SRE)
        sreShares = glapi.create_get_group("sre-shares")
        glRepo = glapi.get_project(sreShares, repoName)
        teamForkedRepo = glRepo.id

        repoUrl = glRepo.http_url_to_repo

        sgit = GitAPI(repoUrl, self.projectsc_token)
        sgit.info()
        sgit.checkout(branch)
        commitRef = sgit.head_commit()

        cpRepo = glapi.get_project(checkpoint, repoName)

        # Target (Temporary outgoing branch based on the prepped branch)
        #cpRepoUrl = cpRepo.http_url_to_repo
        #tgit = GitAPI(shareRepoUrl, self.projectsc_token)
        #tgit.checkout("%s" % branch)

        tgit = GitAPI(cpRepo.http_url_to_repo, self.projectsc_token)
        tgit.checkout("%s" % branch)
        tgit.checkout_new("%s-outgoing" % branch)

        #tgit.checkout_new("%s-outgoing" % branch)
        tgit.info()
        tgit.set_user(self.git_user['username'], self.git_user['email'])

        # Do a full copy from source to target
        fileutils = FileUtils()
        fileutils.copytree (sgit.dir(), tgit.dir())

        if len(tgit.has_changes()) == 0:
            print("-- Exiting.  No changes to export.")
            return

        # tgit.commit_and_push("%s" % branch, "Merged sae changes (%s)" % commitRef.hexsha[0:7])
        tgit.commit_and_push("%s-outgoing" % branch, "Merged sae changes (%s)" % commitRef.hexsha[0:7])

        # ciYaml = 'scanjob:\n   script: ocwa-scanner\n'
        # glapi.add_file(shareRepoId, "%s-outgoing" % branch, '.gitlab-ci.yml', ciYaml)

        glapi.create_get_merge_request (cpRepo.id, "Export Request (%s)" % commitRef.hexsha[0:7], "%s-outgoing" % branch, "%s" % branch, None, ['ocwa-export'])


    def prep_checkpoint_from_external (self, repoName, url, branch, to_branch, token = None):
        glapi = GitlabAPI(self.projectsc_host, self.projectsc_token)

        # Pull latest from external repo into the checkpoint branch
        cp = glapi.create_get_group("ocwa-checkpoint")

        cpRepo = glapi.get_project(cp, repoName)

        tgit = GitAPI(cpRepo.http_url_to_repo, self.projectsc_token)
        tgit.info()

        commitRef = tgit.pull_from_remote(branch, to_branch, url, token)
        #tgit.push_to_origin(to_branch)

        return tgit


    def init_pri_branch (self, repoName, branch):
        glapi = GitlabAPI(self.projectsc_host, self.projectsc_token)

        checkpoint = glapi.create_get_group("ocwa-checkpoint")
        repo = glapi.create_get_project(checkpoint, repoName)


        ciYaml = 'scanjob:\n   script: ocwa-scanner\n'
        glapi.create_get_branch (checkpoint, repoName, branch, 'private')
        glapi.protect_branch(repo, branch)
        glapi.add_file(repo, branch, '.gitlab-ci.yml', ciYaml)

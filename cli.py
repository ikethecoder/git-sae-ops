import argparse
import gitlab
from clients.git_api import GitAPI
from clients.gitlab_api import GitlabAPI
from clients.file_api import FileUtils
import os
import base64
from urllib.parse import urlparse
from operations.project import ProjectOp
from operations.hello import Hello
from operations.request_export import RequestExport
from operations.request_import import RequestImport
from operations.merge import Merge
from operations.push_changes import PushChanges
from operations.cancel import Cancel

GIT_USER_EMAIL = os.environ.get("GIT_USER_EMAIL")
GIT_USER_USERNAME = os.environ.get("GIT_USER_USERNAME")

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

TOKEN = os.environ['PROJECTSC_TOKEN']

OUTPUTCHECKERS = "oc"

CROSS_PROJECT_CHECKER = "oc"

OCWA_CHECKPOINT = "ocwa-checkpoint"

CROSS_PROJECT_GROUP = ""

parser = argparse.ArgumentParser(description='SRE Project Management')

parser.add_argument('command')

#parser.add_argument('--host',
#                    help='gitlab host')
parser.add_argument('--project', 
                    help='research project')
parser.add_argument('--repo',
                    help='repository')
parser.add_argument('--importUrl',
                    help='importUrl')
parser.add_argument('--branch',
                    help='branch')
parser.add_argument('--team', 
                    help='share team project')
parser.add_argument('--destroy',  default=False, type=bool,
                    help='destroy objects')

parser.add_argument('--hook', 
                    help='Hook for calling back to group-sync')

args = parser.parse_args()

host = os.environ.get('PROJECTSC_HOST')
 
glapi = GitlabAPI("%s" % host, TOKEN)

command = args.command

config = {
    "projectsc": { "host" : os.environ.get('PROJECTSC_HOST'), "token" : os.environ.get('PROJECTSC_TOKEN') },
    "github": { "token" : os.environ.get('GITHUB_TOKEN') },
    "git_user": { "username" : os.environ.get("GIT_USER_USERNAME") , "email" : os.environ.get("GIT_USER_EMAIL") }
}


if command == 'hello' and args.destroy == False:

    Hello().run()

elif command == 'project' and args.destroy == False:
    # glcli --project 99-t05 --repo geekcomputers project
    # glcli --project 99-t05 --importUrl https://github.com/ikethecoder/popdata-infra.git project

    saeProjectName = args.project
    repo = args.repo
    if args.importUrl is not None:
        o = urlparse(args.importUrl)
        parts = o.path.split('/')
        repo = "%s-%s" % (parts[1], parts[2])
        repo = repo[0:-4].lower()
        print ("New repo %s" % repo)

    ProjectOp(glapi).run(saeProjectName, repo)


elif command == 'request-export' and args.destroy == False:
    # glcli --branch master --importUrl https://github.com/ikethecoder/topbar.git request-export

    branch = args.branch
    importUrl = args.importUrl
    repo = args.repo

    if args.importUrl is not None:
        o = urlparse(importUrl)
        parts = o.path.split('/')
        repo = "%s-%s" % (parts[1], parts[2])
        repo = repo[0:-4].lower()
        print ("New repo %s" % repo)

    RequestExport(config).run(repo, importUrl, branch)

elif command == 'approve-export-merge' and args.destroy == False:

    branch = args.branch
    repo = args.repo

    Merge(config).approve_export_mr(repo, branch)

elif command == 'push-to-external' and args.destroy == False:
    # glcli --branch develop --repo ikethecoder-topbar --importUrl https://github.com/ikethecoder/topbar.git push-export-changes

    proj = args.project
    branch = args.branch
    importUrl = args.importUrl
    repo = "%s-repo" % proj # args.repo
    if args.repo is not None:
       repo = args.repo

    PushChanges(config).push_to_external (repo, importUrl, branch)

elif command == 'request-import' and args.destroy == False:

    # glcli --branch develop --importUrl https://github.com/ikethecoder/topbar.git project-import
    proj = args.project
    branch = args.branch
    importUrl = args.importUrl

    o = urlparse(args.importUrl)
    parts = o.path.split('/')
    repo = "%s-%s" % (parts[1], parts[2])
    repo = repo[0:-4].lower()
    print ("New repo %s" % repo)

    RequestImport(config).run(repo, importUrl, branch)

elif command == 'approve-import-merge' and args.destroy == False:

    branch = args.branch
    repo = args.repo

    Merge(config).approve_import_mr(repo, branch)

elif command == 'push-to-sae' and args.destroy == False:
    # glcli --branch develop --repo ikethecoder-topbar --importUrl https://github.com/ikethecoder/topbar.git push-export-changes

    proj = args.project
    branch = args.branch
    repo = "%s-repo" % proj # args.repo
    if args.repo is not None:
       repo = args.repo

    PushChanges(config).push_to_sae (repo, branch)

elif command == 'cancel-export' and args.destroy == False:
    proj = args.project
    branch = args.branch
    repo = "%s-repo" % proj # args.repo
    if args.repo is not None:
       repo = args.repo

    Cancel(config).cancel_export (repo, branch)

elif command == 'cancel-import' and args.destroy == False:
    proj = args.project
    branch = args.branch
    repo = "%s-repo" % proj # args.repo
    if args.repo is not None:
       repo = args.repo

    Cancel(config).cancel_import (repo, branch)


# elif command == 'project-export' and args.destroy == False:
#     # glcli --branch develop --repo ikethecoder-topbar --importUrl https://github.com/ikethecoder/topbar.git project-export
#     proj = args.project
#     branch = args.branch
#     importUrl = args.importUrl

#     repo = "%s-repo" % proj # args.repo
#     if args.repo is not None:
#        repo = args.repo

#     # o = urlparse(args.importUrl)
#     # parts = o.path.split('/')
#     # trepo = "%s-%s" % (parts[1], parts[2])
#     # trepo = trepo[0:-4].lower()
#     # print ("New repo %s" % trepo)

#     # Create a merge request from the project to the 'public'
#     # Outputchecker reviews the change, and once accepted

#     # Output: http://gitlab.example.demo/99-t05/pythonstuff.git
#     # Branch: master
#     # : Create this branch under dip-public project, if not already there
#     # : creates a merge request from this branch to a branch on the outside world

#     public = glapi.create_get_group("ocwa-checkpoint")
#     publicRepo = glapi.create_get_project(public, repo)

#     sharedGroup = glapi.create_get_group("sre-shares")
#     teamForkedRepo = glapi.create_get_fork(publicRepo, "sre-shares")
#     # glapi.create_get_branch(sharedGroup, repo, "develop")
#     # glapi.set_default_branch(sharedGroup, repo, "develop")
#     # glapi.protect_branch(teamForkedRepo, 'master')

#     #glapi.create_get_branch(public, repo, "%s-outgoing" % branch)

#     publicRepoUrl = glapi.get_project(public, repo).http_url_to_repo

#     tgit = GitAPI(publicRepoUrl, TOKEN)
#     tgit.info()
#     # commitRef = tgit.checkout_new("%s-outgoing" % branch)

#     # : Pull changes from remote to tgit <branch>-incoming
#     # : Push new <branch>-incoming to origin
#     #commitRef = tgit.pull_from_remote(branch, "%s-outgoing" % branch, importUrl)
#     #newBranch = tgit.push_to_origin("%s-outgoing" % branch)

#     glapi.create_get_merge_request (publicRepo, "Export Request", "%s-outgoing" % branch, "%s-mirror" % branch, None, ['ocwa-export'])



    

elif command == 'project-import-merged_NOT_USED' and args.destroy == False:

    # glcli --branch develop --importUrl https://github.com/ikethecoder/topbar.git project-import
    proj = args.project
    branch = args.branch
    importUrl = args.importUrl

    o = urlparse(args.importUrl)
    parts = o.path.split('/')
    repo = "%s-%s" % (parts[1], parts[2])
    repo = repo[0:-4].lower()
    print ("New repo %s" % repo)

    # Have a 'public' group
    public = glapi.create_get_group("ocwa-checkpoint")
    publicRepo = glapi.create_get_project(public, repo)

    # Get the corresponding internal group
    sharedGroup = glapi.create_get_group("sre-shares")
    glRepo = glapi.get_project(sharedGroup, repo)
    teamForkedRepo = glRepo.id

    publicRepoUrl = glapi.get_project(public, repo).http_url_to_repo

    tgit = GitAPI(publicRepoUrl, TOKEN)
    tgit.info()

    # : Pull changes from remote to tgit <branch>-incoming
    # : Push new <branch>-incoming to origin
    commitRef = tgit.pull_from_remote(branch, "%s-incoming" % branch, importUrl)
    newBranch = tgit.push_to_origin("%s-incoming" % branch)

    # : Create a merge request in the public repo from <branch>-incoming to <branch>
    glapi.create_get_branch(public, repo, branch)
    glapi.create_get_branch(sharedGroup, repo, branch)

    ciYaml = 'scanjob:\n   script: ocwa-scanner\n'
    glapi.add_file(publicRepo, newBranch, '.gitlab-ci.yml', ciYaml)

    glapi.create_get_merge_request (publicRepo, "Import Request (%s)" % commitRef.hexsha[0:7], newBranch, branch, None, ['ocwa-import'])

    # : Merge request reviewed by outputchecker
    #   be merged by the outputchecker into the real <branch>.
    #   Scanning has to pass.

    # : Once that real branch is merged, then new merge requests are created for each Fork




elif command == 'prepare-repo-for-import' and args.destroy == False:
    # glcli --branch develop --importUrl https://github.com/ikethecoder/topbar.git prepare-repo-for-import

    proj = args.project
    branch = args.branch
    importUrl = args.importUrl

    o = urlparse(importUrl)
    parts = o.path.split('/')
    repo = "%s-%s" % (parts[1], parts[2])
    repo = repo[0:-4].lower()
    print ("New repo %s" % repo)

    # Source
    sgit = GitAPI(importUrl, GITHUB_TOKEN)
    commitRef = sgit.checkout(branch)
    sgit.info()

    # Target
    share = glapi.create_get_group("ocwa-checkpoint")
    shareRepoUrl = glapi.get_project(share, repo).http_url_to_repo
    tgit = GitAPI(shareRepoUrl, TOKEN)
    tgit.checkout_new("%s-incoming" % branch)
    tgit.info()
    tgit.set_user(GIT_USER_USERNAME, GIT_USER_EMAIL)

    # Do a full copy from source to target
    fileutils = FileUtils()
    fileutils.copytree (sgit.dir(), tgit.dir())

    # Commit the changes to the target repo
    tgit.commit_and_push("%s-incoming" % branch, "OCWA import repo (%s)" % commitRef.hexsha[0:7])

elif command == 'push-import-changes' and args.destroy == False:
    # glcli --branch develop --repo ikethecoder-topbar push-import-changes

    proj = args.project
    branch = args.branch
    repo = "%s-repo" % proj # args.repo
    if args.repo is not None:
       repo = args.repo

    # Takes two repository locations (source and target)
    # Clones the two repositories
    # Sets the right branch
    # Copies actual files over to the target
    # Prepare files for commit
    # Push to the target location
    #

    # Source
    public = glapi.create_get_group("ocwa-checkpoint")
    publicRepoUrl = glapi.get_project(public, repo).http_url_to_repo
    sgit = GitAPI(publicRepoUrl, TOKEN)
    commitRef = sgit.checkout(branch)
    sgit.info()

    # Target
    share = glapi.create_get_group("sre-shares")
    shareRepoUrl = glapi.get_project(share, repo).http_url_to_repo
    tgit = GitAPI(shareRepoUrl, TOKEN)
    tgit.checkout(branch)
    tgit.info()
    tgit.set_user(GIT_USER_USERNAME, GIT_USER_EMAIL)

    # Do a full copy from source to target
    fileutils = FileUtils()
    fileutils.copytree (sgit.dir(), tgit.dir())

    # Commit the changes to the target repo
    tgit.commit_and_push(branch, "OCWA import (%s)" % commitRef.hexsha[0:7])

    glapi.delete_branch(glapi.get_project(public, repo).id, "%s-incoming" % branch)



elif command == 'init' and args.destroy == False:

    glapi.update_root_create_groups()

    glapi.create_get_group(OCWA_CHECKPOINT)
    glapi.create_get_group(OUTPUTCHECKERS)

    glapi.create_hook(args.hook)


elif command == 'external-project' and args.destroy == False:

    # In the case of an external project, gitlab CE does not support PULL, 
    # so it is not able to pull from external sources
    # TO emulate it, some custom code would need to be created that 
    # would perform the mirror (git clone, add external remote, pull, etc)
    # .. and then submit the changes back to an external project, which
    # would then go through normal 'input checker' flow.
    #
    print('not implemented!')

else:
    raise Exception("Invalid command %s (destroy=%s)" % (command, args.destroy))


# for item in gl.search('issues', search_str, as_list=False):
#     do_something(item)

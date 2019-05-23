
import gitlab

class ProjectOp():
    def __init__(self, glapi):
        self.glapi = glapi

    def run (self, saeProjectName, repoName):
        glapi = self.glapi

        # Get the outputchecker group
        ocGroup = glapi.create_get_group("oc")

        # Have a 'checkpoint' group that controls movement of files in/out of the SRE
        public = glapi.create_get_group("ocwa-checkpoint")

        publicRepo = glapi.create_get_project(public, repoName)
        glapi.config_project_variant2(publicRepo)

        # Create the corresponding internal group
        sharedGroup = glapi.create_get_group("sre-shares")
        teamGroup = glapi.create_get_group("%s" % saeProjectName)
        glrepo = glapi.create_get_project(sharedGroup, repoName)
        glapi.config_project_variant3(glrepo)

        # glapi.unprotect_branch(teamForkedRepo, 'master')
        
        glapi.share_project(publicRepo, ocGroup, gitlab.MAINTAINER_ACCESS)
        # glapi.share_project(publicRepo, teamGroup, gitlab.GUEST_ACCESS)

        glapi.share_project(glrepo, ocGroup, gitlab.REPORTER_ACCESS)
        glapi.share_project(glrepo, teamGroup, gitlab.DEVELOPER_ACCESS)

        glapi.create_get_branch(public, repoName, "private")
        glapi.set_default_branch(public, repoName, "private")
        glapi.protect_branch(publicRepo, "private")
        glapi.protect_branch(publicRepo, "master")

        glapi.create_get_branch(sharedGroup, repoName, "develop")
        glapi.set_default_branch(sharedGroup, repoName, "develop")
        glapi.unprotect_branch(glrepo, "develop")
        glapi.delete_branch(glrepo, "master")


import gitlab

class RepoOp():
    def __init__(self, glapi):
        self.glapi = glapi

    def run (self, saeProjectName, repoName, private):
        glapi = self.glapi

        # Get the outputchecker group
        ocGroup = glapi.create_get_group("oc")

        # Have a 'checkpoint' group that controls movement of files in/out of the SRE
        public = glapi.create_get_group("ocwa-checkpoint")

        publicRepo = glapi.create_get_project(public, repoName)
        glapi.config_project_variant2(publicRepo)
        glapi.share_project(publicRepo, ocGroup, gitlab.DEVELOPER_ACCESS)

        # Create the corresponding internal group
        sharedGroup = glapi.create_get_group("shares")
        teamGroup = glapi.create_get_group("%s" % saeProjectName)
        glrepo = glapi.create_get_project(sharedGroup, repoName)
        
        if private:
            self.do_private_repo_validation(glrepo, saeProjectName)
            glapi.config_project_variant_private(glrepo)
        else:
            glapi.config_project_variant_shared(glrepo)

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


    def do_private_repo_validation (self, glrepo, project_name):
        glapi = self.glapi

        nonMaintainerGroups = 0

        shares = glapi.get_project_shares(glrepo)

        for s in shares:
            if (s['group_access_level'] == 30 and s['group_name'] != project_name):
                nonMaintainerGroups = nonMaintainerGroups + 1
        
        if (nonMaintainerGroups > 0):
            raise Exception("Private repos can only have one Developer group associated.  This is because Issues and Wiki are enabled.")


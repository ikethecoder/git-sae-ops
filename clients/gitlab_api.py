import gitlab

class GitlabAPI():
    def __init__(self, host, token):
        self.gl = gitlab.Gitlab(host, private_token=token)

    def update_root_create_groups(self):
        print('{0:30}'.format('update_root_create_groups'))

        user = self.gl.users.list(username='root')[0]
        user.can_create_group = 1 
        user.save()

    def create_get_group(self, aGroup):
        print('{0:30} {1}'.format('create_get_group', aGroup))
        groups = self.gl.groups.list(search=aGroup)
        for group in groups:
            if group.name == aGroup:
                return group.id
        print('{0:30} {1} CREATING'.format('', aGroup))
        group = self.gl.groups.create({'name':aGroup, 'path':aGroup, 'visibility':'private'})
        return group.id

    def create_get_project(self, aNamespaceId, aProject):
        print('{0:30} {1}'.format('create_get_project', aProject))
        projects = self.gl.projects.list(search=aProject)
        for project in projects:
            if project.name == aProject and project.namespace['id'] == aNamespaceId:
                return project.id
        print('{0:30} {1} CREATING'.format('', aProject))
        project = self.gl.projects.create({'name':aProject, 'namespace_id':aNamespaceId, 'initialize_with_readme':False})
        return project.id

    def import_get_project(self, aNamespaceId, aProject, aUrl):
        print('{0:30} {1} URL {2}'.format('import_get_project', aProject, aUrl))
        projects = self.gl.projects.list(search=aProject)
        for project in projects:
            if project.name == aProject and project.namespace['id'] == aNamespaceId:
                return project.id
        print('{0:30} {1} IMPORTING'.format('', aProject))
        project = self.gl.projects.create({'name':aProject, 'path':aProject, 'namespace_id':aNamespaceId, 'import_url':aUrl})
        return project.id

    def set_custom_attribute (self, aProjectId, key, value):
        print('{0:30} {1} : {2} = {3}'.format('set_custom_attribute', aProjectId, key, value))

        project = self.gl.projects.get(aProjectId)
        project.customattributes.set(key, value)

    def get_custom_attribute (self, aProjectId, key):
        print('{0:30} {1} : {2}'.format('get_custom_attribute', aProjectId, key))
        project = self.gl.projects.get(aProjectId)
        attr = project.customattributes.get(key)
        print('{0:30} {1} : {2} = {3}'.format('', aProjectId, key, attr.value))
        return attr.value

    def config_project_variant1(self, aProjectId):
        print('{0:30} {1} : {2}'.format('config_project', aProjectId, "jobs_enabled"))
        project = self.gl.projects.get(aProjectId)
        if project.jobs_enabled == False:
            project.jobs_enabled = True
        project.repository_enabled = True
        project.issues_enabled = True
        project.wiki_enabled = False
        project.snippets_enabled = False
        project.public_jobs = False
        project.lfs_enabled = False
        project.only_allow_merge_if_pipeline_succeeds = True
        project.only_allow_merge_if_all_discussions_are_resolved = True
        project.save()

    def config_project_variant2(self, aProjectId):
        print('{0:30} {1} : {2}'.format('config_project', aProjectId, "jobs_enabled,issues_enabled,wiki_enabled"))
        project = self.gl.projects.get(aProjectId)
        if project.jobs_enabled == False:
            project.jobs_enabled = True
        project.repository_enabled = True
        project.issues_enabled = False
        project.wiki_enabled = False
        project.snippets_enabled = False
        project.public_jobs = False
        project.lfs_enabled = False
        project.only_allow_merge_if_pipeline_succeeds = False
        project.only_allow_merge_if_all_discussions_are_resolved = True
        # project.auto_devops_attributes = { enabled : False }
        project.save()

    def config_project_variant3(self, aProjectId):
        print('{0:30} {1} : {2}'.format('config_project', aProjectId, "jobs_enabled"))
        project = self.gl.projects.get(aProjectId)
        project.jobs_enabled = False
        project.repository_enabled = True
        project.issues_enabled = False
        project.wiki_enabled = False
        project.snippets_enabled = False
        project.public_jobs = False
        project.lfs_enabled = False
        project.only_allow_merge_if_pipeline_succeeds = False
        project.only_allow_merge_if_all_discussions_are_resolved = False
        project.save()

    def approve_merge (self, mr):

        print('{0:30} id={1} [{2}] {3}'.format('approve_merge', mr.id, mr.state, mr.title))

        mr.merge()

    def delete_merge (self, mr):

        print('{0:30} id={1} [{2}] {3}'.format('delete_merge', mr.id, mr.state, mr.title))

        mr.delete()

    def get_merge_request(self, aProjectId, sourceBranch, targetBranch, targetProjectId, labels):
        print('{0:30} {1} {2} --> {3}'.format('get_merge_request', aProjectId, sourceBranch, targetBranch))

        if targetProjectId is not None:
            for mr in self.gl.projects.get(targetProjectId).mergerequests.list():
                if mr.source_branch == sourceBranch and mr.target_branch == targetBranch and (mr.state != 'closed' and mr.state != 'merged'):
                    return mr

        project = self.gl.projects.get(aProjectId)
        mrs = project.mergerequests.list()
        for mr in mrs:
            if mr.source_branch == sourceBranch and mr.target_branch == targetBranch and (mr.state != 'closed' and mr.state != 'merged'):
                return mr

        print('{0:30} {1}'.format('', ': MERGE NOT FOUND'))
        return None

    def create_get_merge_request(self, aProjectId, title, sourceBranch, targetBranch, targetProjectId, labels):
        mr = self.get_merge_request(aProjectId, sourceBranch, targetBranch, targetProjectId, labels)
        if mr is None:
            return self.create_merge_request(aProjectId, title, sourceBranch, targetBranch, targetProjectId, labels)
        else:
            return mr

    def create_merge_request(self, aProjectId, title, sourceBranch, targetBranch, targetProjectId, labels):
        print('{0:30} {1} {2} : {3} --> {4}'.format('create_merge_request', aProjectId, title, sourceBranch, targetBranch))

        project = self.gl.projects.get(aProjectId)

        print('{0:30} {1} {2} CREATING'.format('', aProjectId, title))
        mr = project.mergerequests.create({'source_branch': sourceBranch,
                                   'target_project_id': targetProjectId,
                                   'target_branch': targetBranch,
                                   'title': title,
                                   'labels': labels})
        return mr

    def create_get_branch(self, aNamespaceId, aProject, aBranch, ref = 'master'):
        print('{0:30} {1} {2}'.format('create_get_branch', aProject, aBranch))
        projects = self.gl.projects.list(search=aProject)
        for project in projects:
            if project.name == aProject and project.namespace['id'] == aNamespaceId:
                branches = project.branches.list()
                for branch in branches:
                    if branch.name == aBranch:
                        return branch.name

                print('{0:30} {1} CREATING'.format('', aBranch))

                create_params = {'branch': aBranch}
                if ref is not None:
                    create_params['ref'] = ref
                branch = project.branches.create(create_params)
                return branch.name
        raise Exception("Project %s in %s not found" % (aProject, aNamespaceId))

    def set_default_branch(self, aNamespaceId, aProject, aBranch):
        print('{0:30} {1} {2}'.format('set_default_branch', aProject, aBranch))
        projects = self.gl.projects.list(search=aProject)
        for project in projects:
            if project.name == aProject and project.namespace['id'] == aNamespaceId:
                project.default_branch = aBranch
                project.save()
                return
        raise Exception("Project %s in %s not found" % (aProject, aNamespaceId))

    def has_branch (self, aNamespaceId, aProject, aBranch):
        print('{0:30} {1} {2}'.format('has_branch', aProject, aBranch))
        projects = self.gl.projects.list(search=aProject)
        for project in projects:
            if project.name == aProject and project.namespace['id'] == aNamespaceId:
                branches = project.branches.list()
                for branch in branches:
                    if branch.name == aBranch:
                        return True
                return False
        raise Exception("Project %s in %s not found" % (aProject, aNamespaceId))

    def get_project(self, aNamespaceId, aProject):
        print('{0:30} {1}'.format('get_project', aProject))
        projects = self.gl.projects.list(search=aProject)
        for project in projects:
            if project.name == aProject and project.namespace['id'] == aNamespaceId:
                return project
        raise Exception("Project %s in %s not found" % (aProject, aNamespaceId))

    def protect_branch(self, aProjectId, branch):
        print('{0:30} branch:{1} for project:{2}'.format('protect_branch', branch, aProjectId))
        project = self.gl.projects.get(aProjectId)
        branch = project.branches.get(branch)
        branch.protect()

    def delete_branch(self, aProjectId, branch):
        print('{0:30} branch:{1} for project:{2}'.format('delete_branch', branch, aProjectId))
        project = self.gl.projects.get(aProjectId)
        branches = project.branches.list()
        for br in branches:
            if br.name == branch:
                print('{0:30} DELETE {1} for project:{2}'.format('', branch, aProjectId))
                br.delete()

    def unprotect_branch(self, aProjectId, branch):
        print('{0:30} branch:{1} for project:{2}'.format('unprotect_branch', branch, aProjectId))
        project = self.gl.projects.get(aProjectId)
        branch = project.branches.get(branch)
        branch.unprotect()

    def share_project(self, aProjectId, aGroupId, access):
        print('{0:30} Access project:{1} by group:{2} with access:{3}'.format('share_project', aProjectId, aGroupId, access))
        project = self.gl.projects.get(aProjectId)
        try:
            project.share(aGroupId, access)
        except gitlab.exceptions.GitlabCreateError as error:
            if error.response_code == 409:
                return
            else:
                raise error


    def create_get_fork(self, aProjectId, aGroupName):
        print('{0:30} Create fork of project:{1} to group:{2}'.format('create_get_fork', aProjectId, aGroupName))

        project = self.gl.projects.get(aProjectId)

        forks = project.forks.list()
        for fork in forks:
            if fork.namespace['name'] == aGroupName:
                return fork.id

        print('{0:30} {1} CREATING'.format('', aGroupName))
        fork = project.forks.create({'namespace': aGroupName})
        return fork.id

    def create_hook(self, url, token = None):
        print('{0:30} {1}'.format('create_hook', url))
        hooks = self.gl.hooks.list()
        for hook in hooks:
            if hook.url == url:
                return
        print('{0:30} {1} CREATED'.format('', url))
        hook = self.gl.hooks.create({'url': url, 'token': token, 'enable_ssl_verification': False, 'merge_requests_events': True, 'repository_update_events': True})

    def add_file (self, aProjectId, branch, fileName, fileContents):
        print('{0:30} Add file:{1} in branch {2} file:{3}'.format('add_file', aProjectId, branch, fileName))
        project = self.gl.projects.get(aProjectId)
        try:
            f = project.files.get(file_path=fileName, ref=branch)
        except gitlab.exceptions.GitlabGetError as error:
            if error.response_code == 404:
                f = project.files.create({'file_path': fileName,
                                'branch': branch,
                                'content': fileContents,
                                'author_email': 'no-reply@popdata.local',
                                'author_name': 'Automation Agent',
                                'commit_message': 'Create file'})
                print(f)


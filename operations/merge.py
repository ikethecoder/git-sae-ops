
from clients.git_api import GitAPI
from clients.file_api import FileUtils
from clients.gitlab_api import GitlabAPI

import time
import logging
log = logging.getLogger(__name__)

class Merge():
    def __init__(self, config):
        self.projectsc_host = config['projectsc']['host']
        self.projectsc_token = config['projectsc']['token']
        self.github_token = config['github']['token']
        self.git_user = config['git_user']

    def wait_for_mr_ready (self, repoName, branch):
        log.info('{0:30}'.format('wait_for_mr_ready'))

        glapi = GitlabAPI(self.projectsc_host, self.projectsc_token)

        checkpoint = glapi.create_get_group("ocwa-checkpoint")
        cpRepo = glapi.get_project(checkpoint, repoName)

        mr = glapi.get_merge_request (cpRepo.id, "%s-outgoing" % branch, "%s" % branch, None, ['ocwa-export'])

        for attempt in range(0,60):
            pipelines = mr.pipelines()
            if len(pipelines) > 0:
                if pipelines[0]['status'] == 'success':
                    log.info('{0:30} Attempt # {1}. Scan passed. Success!'.format('wait_for_mr_ready', attempt))
                    return True
                log.info('{0:30} Attempt # {1}. Sleep and try again ({2}).'.format('wait_for_mr_ready', attempt, pipelines[0]['status']))
            else:
                log.info('{0:30} Attempt # {1}. Sleep and try again.'.format('wait_for_mr_ready', attempt))
            time.sleep(10)

        log.info('{0:30} Attempt # {1}. Giving up :('.format('wait_for_mr_ready', attempt))
        return False

    def approve_export_mr (self, repoName, branch):
        glapi = GitlabAPI(self.projectsc_host, self.projectsc_token)

        checkpoint = glapi.create_get_group("ocwa-checkpoint")
        cpRepo = glapi.get_project(checkpoint, repoName)

        mr = glapi.get_merge_request (cpRepo.id, "%s-outgoing" % branch, "%s" % branch, None, ['ocwa-export'])

        pipelines = mr.pipelines()
        if len(pipelines) > 0:
            log.info('{0:30} Pipeline Status: {1}'.format('approve_export_mr', pipelines[0]['status']))
            if pipelines[0]['status'] == 'success':
                glapi.approve_merge(mr)
                return
            elif pipelines[0]['status'] == 'failed':
                raise Exception("Merge request failed scan.")
            raise Exception("Scanning has not completed.")
        raise Exception("Scanning has not started.")

    def approve_import_mr (self, repoName, branch):
        glapi = GitlabAPI(self.projectsc_host, self.projectsc_token)

        checkpoint = glapi.create_get_group("ocwa-checkpoint")
        cpRepo = glapi.get_project(checkpoint, repoName)

        mr = glapi.get_merge_request (cpRepo.id, "%s-incoming" % branch, "%s" % branch, None, ['ocwa-import'])

        if mr is not None:
            glapi.approve_merge(mr)

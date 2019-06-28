
from urllib.parse import urlparse

import logging
log = logging.getLogger(__name__)

class RepoUtils():

    # Param: https://projectscstg.popdata.bc.ca/shares/ikethecoder-external-test-repo.git
    # Return: ikethecoder-external-test-repo
    def get_repo_name(self, url):
        o = urlparse(url)
        parts = o.path.split('/')
        repo = parts[2]
        repo = repo[0:-4].lower()
        log.info ("New repo %s" % repo)

        return repo

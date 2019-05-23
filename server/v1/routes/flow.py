try:  # Python 3.5+
    from http import HTTPStatus as HTTPStatus
except ImportError:
    from http import client as HTTPStatus
from flask import Blueprint, jsonify, request

from server.config import Config
import requests
import json
import sys
from server.auth.auth import auth
from operations.push_changes import PushChanges

import logging
log = logging.getLogger(__name__)

flow = Blueprint('flow', 'flow')


@flow.route('/webhook',
           methods=['POST'], strict_slashes=False)
@auth
def gitlab_webhook() -> object:
    """
    Takes a gitlab webhook event and processes the event
    """
    conf = Config().data

    data = request.get_json()
    print("---")
    print(data)
    print("---")

    if data['object_kind'] == "merge_request" and data['project']['namespace'] == conf.get('checkpointGroup'):
        print("Merge Request for a checkpoint project detected: %s" % data['repository']['name'])
        if data['object_attributes']['state'] == 'closed':
            print("-- MR Closed - initiate mirroring")
            source = data['object_attributes']['source_branch']
            target = data['object_attributes']['target_branch']
            print("%s --> %s" % (source,target))

            if source.endswith('-outgoing'):
                repoName = data['repository']['name']
                print("push_to_external (%s, %s, %s)" % (repoName, None, target))
                PushChanges(conf).push_to_external(repoName, None, target)

            elif source.endswith('-incoming'):
                repoName = data['repository']['name']
                print("push_to_sae (%s, %s, %s)" % (repoName, importUrl, target))
                PushChanges(conf).push_to_sae(repoName, target)
            else:
                print("ERR: Unexpected source branch %s" % source)
        else:
            print("-- MR Ignored - state %s" % data['object_attributes']['state'])

    return jsonify(status="ok"), HTTPStatus.OK

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
    config = Config()

    data = request.get_json()
    print("---")
    print(data)
    print("---")

    if data['event_type'] == "merge_request" and data['project']['namespace'] == config.data('checkpointGroup'):
        print("Merge Request for a checkpoint project detected: %s" % data['project']['name'])

    return jsonify(status="ok"), HTTPStatus.OK

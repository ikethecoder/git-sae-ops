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
    data = request.get_json()
    print(data)
    print(data['id'])
    return json.dumps(request.get_json()), HTTPStatus.OK
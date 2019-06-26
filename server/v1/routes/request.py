try:  # Python 3.5+
    from http import HTTPStatus as HTTPStatus
except ImportError:
    from http import client as HTTPStatus
from flask import Blueprint, jsonify, request, abort
from flask.wrappers import Response

from server.config import Config
import requests
import json
import sys
from server.auth.auth import auth
from operations.request_import import RequestImport
from operations.request_export import RequestExport
from operations.merge import Merge
from operations.cancel import Cancel
from clients.repo_utils import RepoUtils

import logging
log = logging.getLogger(__name__)

requestApi = Blueprint('request', 'request')

@requestApi.route('/',
           methods=['POST'], strict_slashes=False)
@auth
def create_request() -> object:
    """
    Creates a new import or export request
    """
    conf = Config().data

    data = request.get_json()
    log.debug("---")
    log.debug(data)
    log.debug("---")

    direction = data['direction']

    repository = data['repository']
    branch = data['branch']
    externalRepository = data['externalRepository']

    repo = RepoUtils().get_repo_name(repository)

    if direction == 'export':
        try:
            mr = RequestExport(conf).run(repo, externalRepository, branch)
            return jsonify(status="ok",location=mr.web_url,title=mr.title), HTTPStatus.OK
        except BaseException as error:
            return jsonify(status="error",message=("%s" % error)), HTTPStatus.BAD_REQUEST

    elif direction == 'import':
        try:
            mr = RequestImport(conf).run(repo, externalRepository, branch)
            return jsonify(status="ok",location=mr.web_url,title=mr.title), HTTPStatus.OK
        except BaseException as error:
            return jsonify(status="error",message=("%s" % error)), HTTPStatus.BAD_REQUEST

    abort(Response("The 'direction' must be 'import' or 'export'", 400))

@requestApi.route('/close',
           methods=['PUT'], strict_slashes=False)
@auth
def close_request() -> object:
    """
    Closes a merge request
    """
    conf = Config().data

    data = request.get_json()
    log.debug("---")
    log.debug(data)
    log.debug("---")

    direction = data['direction']

    repository = data['repository']
    branch = data['branch']

    repo = RepoUtils().get_repo_name(repository)

    if direction == 'export':
        try:
            Cancel(conf).cancel_export(repo, branch)
        except BaseException as error:
            return jsonify(status="error",message=("%s" % error)), HTTPStatus.BAD_REQUEST

    elif direction == 'import':
        try:
            Cancel(conf).cancel_import(repo, branch)
        except BaseException as error:
            return jsonify(status="error",message=("%s" % error)), HTTPStatus.BAD_REQUEST

    else:
        abort(Response("The 'direction' must be 'import' or 'export'", 400))

    return jsonify(status="ok"), HTTPStatus.OK

@requestApi.route('/merge',
           methods=['PUT'], strict_slashes=False)
@auth
def merge_request() -> object:
    """
    Approves a merge request
    """
    conf = Config().data

    data = request.get_json()
    log.debug("---")
    log.debug(data)
    log.debug("---")

    direction = data['direction']

    repository = data['repository']
    branch = data['branch']

    repo = RepoUtils().get_repo_name(repository)

    if direction == 'export':
        try:
            Merge(conf).approve_export_mr(repo, branch)
        except BaseException as error:
            return jsonify(status="error",message=("%s" % error)), HTTPStatus.BAD_REQUEST

    elif direction == 'import':
        try:
            Merge(conf).approve_import_mr(repo, branch)
        except BaseException as error:
            return jsonify(status="error",message=("%s" % error)), HTTPStatus.BAD_REQUEST

    else:
        abort(Response("The 'direction' must be 'import' or 'export'", 400))

    return jsonify(status="ok"), HTTPStatus.OK

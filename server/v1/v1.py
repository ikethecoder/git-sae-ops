from flask import Blueprint, jsonify
from server.v1.routes.flow import flow


v1 = Blueprint('v1', 'v1')

@v1.route('/status', methods=['GET'], strict_slashes=False)
def status():
    """
    Returns the overall API status
    :return: JSON of endpoint status
    """
    return jsonify({"status": "ok"})


class Register:
    def __init__(self, app):
        app.register_blueprint(v1, url_prefix="/v1")
        app.register_blueprint(flow, url_prefix="/v1/flow")

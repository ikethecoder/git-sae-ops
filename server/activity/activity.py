
import os
import json
import datetime
from datetime import timezone

def activity (action, repo, team, actor, success, message):

    print("Recording activity")
    with open('/audit/activity.log', 'a', 1) as f:

        payload = {
            "action" : action,
            "repository" : repo,
            "team" : team,
            "actor" : actor,
            "ts" : utc_to_local(datetime.datetime.now()).isoformat(),
            "success": success,
            "message": message
        }
        f.write(json.dumps(payload) + os.linesep)

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

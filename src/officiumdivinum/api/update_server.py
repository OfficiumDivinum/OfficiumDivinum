"""
Re-used from.

https://github.com/SwagLyrics/swaglyrics-backend/blob/35d23d0ba416e742e381da931d592ce6f58fc13f/issue_maker.py

which is under the MIT license.
"""
import hashlib
import hmac
import json
import os
from subprocess import run

import git
from flask import Blueprint
from flask import abort
from flask import request

update_server = Blueprint("update_server", __name__, url_prefix="/update_server")

try:
    w_secret = os.environ["WEBHOOK_SECRET"]
except KeyError:
    pass


def is_valid_signature(x_hub_signature, data, private_key):
    hash_algorithm, github_signature = x_hub_signature.split("=", 1)
    algorithm = hashlib.__dict__.get(hash_algorithm)
    encoded_key = bytes(private_key, "latin-1")
    mac = hmac.new(encoded_key, msg=data, digestmod=algorithm)
    return hmac.compare_digest(mac.hexdigest(), github_signature)


@update_server.route("/", methods=["POST"])
def webhook():
    if request.method != "POST":
        return "OK"
    else:
        abort_code = 418
        # Do initial validations on required headers
        if "X-Github-Event" not in request.headers:
            abort(abort_code)
        if "X-Github-Delivery" not in request.headers:
            abort(abort_code)
        if "X-Hub-Signature" not in request.headers:
            abort(abort_code)
        if not request.is_json:
            abort(abort_code)
        if "User-Agent" not in request.headers:
            abort(abort_code)
        ua = request.headers.get("User-Agent")
        if not ua.startswith("GitHub-Hookshot/"):
            abort(abort_code)

        event = request.headers.get("X-GitHub-Event")
        if event == "ping":
            return json.dumps({"msg": "Hi!"})
        if event != "push":
            return json.dumps({"msg": "Wrong event type"})

        x_hub_signature = request.headers.get("X-Hub-Signature")
        if not is_valid_signature(x_hub_signature, request.get_data(), w_secret):
            print("Deploy signature failed: {sig}".format(sig=x_hub_signature))
            abort(abort_code)

        payload = request.get_json()
        if payload is None:
            print("Deploy payload is empty: {payload}".format(payload=payload))
            abort(abort_code)

        if payload["ref"] != "refs/heads/master":
            return json.dumps({"msg": "Not master; ignoring"})

        repo = git.Repo("~/OfficiumDivinum")
        origin = repo.remotes.origin

        pull_info = origin.pull()

        if len(pull_info) == 0:
            return json.dumps({"msg": "Didn't pull any information from remote!"})
        if pull_info[0].flags > 128:
            return json.dumps({"msg": "Didn't pull any information from remote!"})

        run(["pip3", "install", "-e", "~/OfficiumDivinum"])

        commit_hash = pull_info[0].commit.hexsha
        build_commit = f'build_commit = "{commit_hash}"'
        print(f"{build_commit}")
        return "Updated PythonAnywhere server to commit {commit}".format(
            commit=commit_hash
        )

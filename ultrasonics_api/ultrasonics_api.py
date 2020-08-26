#!/usr/bin/env python3

"""
ultrasonics_api
Used as a proxy server for ultrasonics to forward api requests to various services which require private api keys.

All api requests should be made to /api/<service>/<subpath>
where <subpath> is the same as sending directly to the respective api.

XDGFX, 2020
"""

import os
from urllib.parse import urlencode

import redis
import requests
from flask import Blueprint, Response, jsonify, redirect, request

from . import core

bp = Blueprint('ultrasonics_api', __name__)
limiter = core.limiter

r = redis.from_url(os.environ.get("REDIS_URL"))

@bp.route('/api')
def index():
    return jsonify({
        "name": "ultrasonics_api",
        "supported apis": [
            "spotify"
        ]
    })


@bp.errorhandler(429)
def error_too_many_requests(e):
    return "ultrasonics: Too many requests, try again later", 429


class Spotify:
    def push_valid_state(self, state):
        r.lpush('spotify_valid_states', state)

    def remove_valid_state(self, state):
        return r.lrem('spotify_valid_states', 0, state)

    def auth_headers(self):
        """
        Encode client_id and client_secret into required authorisation header.
        """
        import base64
        data_string = os.environ.get(
            'SPOTIFY_CLIENT_ID') + ":" + os.environ.get('SPOTIFY_CLIENT_SECRET')
        data_bytes = data_string.encode()
        data_encoded = base64.urlsafe_b64encode(data_bytes)
        auth_headers = {
            "Authorization": f"Basic {data_encoded.decode()}"
        }

        return auth_headers


@bp.route('/api/spotify/<path:subpath>', methods=["GET", "POST", "PUT", "DELETE"])
def api_spotify(subpath):
    """
    Spotify api proxy. Adds an app client secret key to all requests.
    If error 401 is returned, the access token must be renewed.
    """
    # TODO implement some logic to only allow certain subpaths

    base_url = "https://api.spotify.com/"
    url = base_url + subpath
    method = request.method
    params = {**request.values.to_dict()}

    if method == "GET":
        r = requests.get(url=url, params=params)
    elif method == "POST":
        r = requests.post(url=url, params=params)
    elif method == "PUT":
        r = requests.put(url=url, params=params)
    elif method == "DELETE":
        r = requests.delete(url=url, params=params)

    return r.json()


@bp.route('/api/spotify_auth_request')
# @limiter.limit("2 per day")
def api_spotify_auth_request():
    """
    Requests authorisation from the Spotify API.
    """
    from uuid import uuid4

    base_url = "https://accounts.spotify.com/authorize/?"

    params = {
        "client_id": os.environ.get('SPOTIFY_CLIENT_ID'),
        "response_type": "code",
        "redirect_uri": "https://ultrasonics-api.herokuapp.com/api/spotify_auth",
        "state": str(uuid4())
    }

    Spotify().push_valid_state(params["state"])

    url = base_url + urlencode(params)

    return redirect(url, 302)


@bp.route('/api/spotify_auth_renew', methods=["POST"])
@limiter.limit("2 per hour")
def api_spotify_auth_renew():
    """
    Requests a refreshed access token. Request must include refresh_token parameter.
    """
    url = "https://accounts.spotify.com/api/token/"
    data = {**request.values.to_dict()}
    data["grant_type"] = "refresh_token"

    r = requests.post(url=url, data=data, headers=Spotify.auth_headers())

    return r.json()


@bp.route('/api/spotify_auth')
@limiter.exempt
def api_spotify_auth():
    """
    Redirect endpoint from Spotify after authentication attempt.
    """
    code = request.args.get("code", None)
    error = request.args.get("error", None)
    state = request.args.get("state")

    if error:
        return error

    # Try to remove from database, return error if not exist
    if not Spotify().remove_valid_state(state):
        return jsonify({
            "error": "State returned was not valid"
        }), 500

    url = "https://accounts.spotify.com/api/token"

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "https://ultrasonics-api.herokuapp.com/api/spotify_auth"
    }

    r = requests.post(url=url, data=data, headers=Spotify().auth_headers())

    return r.text

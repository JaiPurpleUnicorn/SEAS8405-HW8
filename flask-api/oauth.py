# flask-api/oauth.py

import os
import requests
from jose import jwt
from functools import wraps
from flask import request, jsonify, g

# Environment variables (set by docker-compose)
ISSUER    = os.getenv('OIDC_ISSUER')       # e.g. http://localhost:8080/realms/CentralIAM
JWKS_URL  = os.getenv('OIDC_JWKS_URL')     # e.g. http://keycloak:8080/realms/CentralIAM/protocol/openid-connect/certs
CLIENT_ID = os.getenv('OIDC_CLIENT_ID')    # e.g. intranet

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 1) Parse and validate Authorization header
        auth = request.headers.get('Authorization', None)
        if not auth:
            return jsonify({"message": "Missing Authorization header"}), 401

        parts = auth.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            return jsonify({"message": "Invalid Authorization header format"}), 401

        token = parts[1]

        try:
            # 2) Lazy‐fetch the JWKS from Keycloak
            jwks = requests.get(JWKS_URL).json()

            # 3) Decode the token header to get 'kid'
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = next(
                {
                    "kty": k["kty"],
                    "kid": k["kid"],
                    "use": k["use"],
                    "n": k["n"],
                    "e": k["e"]
                }
                for k in jwks["keys"]
                if k["kid"] == unverified_header["kid"]
            )

            # 4) Validate signature and standard claims
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=[unverified_header["alg"]],
                audience=CLIENT_ID,
                issuer=ISSUER,
            )

            # 5) Attach the validated payload to Flask’s context
            g.current_user = payload

        except Exception as e:
            return jsonify({"message": f"Token validation error: {e}"}), 401

        return f(*args, **kwargs)
    return decorated
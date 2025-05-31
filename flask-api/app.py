# flask-api/app.py
from flask import Flask, jsonify, g
from oauth import requires_auth

app = Flask(__name__)

@app.route('/public')
def public():
    return jsonify({"message": "Public endpoint — no auth required"}), 200

@app.route('/protected')
@requires_auth
def protected():
    user = getattr(g, 'current_user', {})
    return jsonify({
        "message": f"Welcome, {user.get('preferred_username', 'unknown')}!",
        "roles":   user.get("realm_access", {}).get("roles", []),
        "scope":   user.get("scope", "")
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
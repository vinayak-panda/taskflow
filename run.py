from app import create_app, db
from models import TokenBlocklist

app = create_app()

from app import jwt

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar() is not None

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {"success": False, "error": "Token expired. Please login again."}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {"success": False, "error": "Invalid token."}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {"success": False, "error": "Authorization token required."}, 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return {"success": False, "error": "Token revoked. Please login again."}, 401

if __name__ == '__main__':
    app.run(debug=False, port=5000)

from functools import wraps
from flask import session, jsonify


def auth_verify(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if session.get('verified') is False:
            return jsonify({'message': 'unverified'}), 401
        
        return func(*args, **kwargs)
    return decorated_view
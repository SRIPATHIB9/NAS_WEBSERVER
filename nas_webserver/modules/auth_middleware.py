from functools import wraps
from flask import session, jsonify

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'username' not in session:
                return jsonify({'error': 'Login required'}), 401
            if role and session.get('role') != role and session.get('role') != 'admin':
                return jsonify({'error': 'Access denied'}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

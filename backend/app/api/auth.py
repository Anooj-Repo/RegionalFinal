"""
Authentication & Role-Based Access Control (RBAC) API Blueprint
"""

from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash
from backend.app.db.models import db, User, AuditLog

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt, jwt_required, verify_jwt_in_request

def role_required(allowed_roles):
    """Decorator enforcing Role-Based Access Control (RBAC)."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if request.method == 'OPTIONS':
                return fn(*args, **kwargs)
            verify_jwt_in_request(optional=True)
            claims = get_jwt() or {}
            user_role = claims.get('role', 'Viewer')
            if allowed_roles and user_role not in allowed_roles:
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'Role "{user_role}" is not authorized to access this resource. Required roles: {allowed_roles}'
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@auth_bp.route('/login', methods=['POST'])
def login():
    """User Login Endpoint - Returns JWT token with role claims."""
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'error': 'Bad Request', 'message': 'Username and password are required.'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        # Audit failed login
        audit = AuditLog(user_name=username, user_role='Anonymous', action='LOGIN_FAILED', details='Invalid credentials')
        db.session.add(audit)
        db.session.commit()
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid username or password.'}), 401

    if not user.is_active:
        return jsonify({'error': 'Forbidden', 'message': 'Account is deactivated. Please contact Administrator.'}), 403

    # Generate JWT Access Token with custom claims
    additional_claims = {
        'role': user.role,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name
    }
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

    # Audit successful login
    audit = AuditLog(user_name=user.username, user_role=user.role, action='LOGIN_SUCCESS', details='User logged in successfully')
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Retrieves authenticated user profile details."""
    current_user_id = get_jwt_identity()
    user = User.query.get(int(current_user_id))
    if not user:
        return jsonify({'error': 'Not Found', 'message': 'User profile not found.'}), 404
    return jsonify({'status': 'success', 'user': user.to_dict()}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User Logout Endpoint."""
    claims = get_jwt()
    username = claims.get('username', 'User')
    role = claims.get('role', 'Viewer')

    audit = AuditLog(user_name=username, user_role=role, action='LOGOUT', details='User logged out')
    db.session.add(audit)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Successfully logged out.'}), 200

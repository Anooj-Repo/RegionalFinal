"""
Flask Application Factory Initialization
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.app.core.config import Config
from backend.app.db.models import db

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)

    # Register API Blueprints

    from backend.app.api.auth import auth_bp
    from backend.app.api.projects import projects_bp
    from backend.app.api.raid import raid_bp
    from backend.app.api.emails import emails_bp
    from backend.app.api.admin import admin_bp
    from backend.app.api.agents import agents_bp
    from backend.app.api.chat_history import chat_history_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(raid_bp)
    app.register_blueprint(emails_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(agents_bp)
    app.register_blueprint(chat_history_bp)

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Enterprise PM AI Assistant Backend',
            'version': '1.0.0'
        }), 200

    return app


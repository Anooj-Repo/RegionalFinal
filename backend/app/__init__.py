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

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Enterprise PM AI Assistant Backend',
            'version': '1.0.0'
        }), 200

    return app

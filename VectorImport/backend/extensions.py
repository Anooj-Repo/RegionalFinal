"""
extensions.py
-------------
Shared Flask extensions, instantiated here (without an app) and
initialized inside create_app() via the init_app() pattern.

Import these singletons anywhere in the project to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# Relational database ORM
db: SQLAlchemy = SQLAlchemy()

# Database migration manager
migrate: Migrate = Migrate()

# Cross-Origin Resource Sharing
cors: CORS = CORS()

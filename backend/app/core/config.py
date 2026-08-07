"""
Core Application Configuration Module
"""

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'app.db').replace('\\', '/')

from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'enterprise-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'enterprise-jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{DB_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False




    # MCP Server Integration Settings
    MCP_HOST = os.getenv('MCP_HOST', '127.0.0.1')
    MCP_PORT = int(os.getenv('MCP_PORT', 5001))
    MCP_API_KEY = os.getenv('MCP_API_KEY', 'mcp-secure-api-key-2026')
    MCP_SERVER_URL = f"http://{MCP_HOST}:{MCP_PORT}"

    # Resend API Key & Email Config
    RESEND_API_KEY = os.getenv('RESEND_API_KEY', 're_123456789_placeholder_key')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'notifications@pmai-assistant.com')

    # RAG Settings
    CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', 'backend/app/rag/storage')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')

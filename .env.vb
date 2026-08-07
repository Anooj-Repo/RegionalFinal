# Backend Configuration
FLASK_APP=backend/run.py
FLASK_ENV=development
SECRET_KEY=sk-qStpysBlPY1OaCJoB_dPHA
JWT_SECRET_KEY=enterprise-jwt-secret-key-change-in-production
DATABASE_URL=sqlite:///C:/source/RegionalFinal/backend/app.db


# MCP Server Configuration
MCP_PORT=5001
MCP_HOST=127.0.0.1
MCP_API_KEY=mcp-secure-api-key-2026
MCP_DATABASE_URL=sqlite:///mcp/mcp.db

# Background Services & Email Configuration
RESEND_API_KEY=7U7gnM3g_eVjMxAQkRi67VP4vJ5HSw3vN
EMAIL_POLL_INTERVAL_SECONDS=5
SENDER_EMAIL=notifications@pmai-assistant.com

# LLM & TCS GenAI Configuration
TCS_GENAI_ENDPOINT=https://genailab.tcs.in/api/v1
TCS_GENAI_API_KEY=placeholder_tcs_genai_key
DEFAULT_MODEL=gemini-1.5-pro

# RAG & Vector Indexing Configuration
CHROMA_PERSIST_DIR=backend/app/rag/storage
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

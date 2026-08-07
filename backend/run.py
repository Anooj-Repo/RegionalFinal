"""
Backend Application Entrypoint (Flask API Server on Port 5000)
"""

import os
import sys

# Ensure root workspace directory is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"[Backend Service] Starting Enterprise PM AI Assistant REST API on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)

"""
Backend Application Debugger Entrypoint (backend/app.py)
Provides entry point for VS Code debugging launchers targeting backend/app.py.
"""

import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"[Backend Service] Starting Enterprise PM AI Assistant REST API on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)

"""
app.py
------
Flask entry point.

Usage:
    flask run              (reads FLASK_APP=app.py automatically)
    python app.py          (direct run, useful in development)
"""

import os
from factory import create_app

# Select environment via FLASK_ENV (defaults to 'development')
env = os.getenv("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=app.config["DEBUG"],
    )

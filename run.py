


import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env before creating app
load_dotenv(Path(__file__).parent / ".env")

from app import create_app
from flask_cors import CORS
from flask import jsonify

def main() -> None:
    app = create_app()
    # Configure CORS for production frontend (placeholder URL)
    CORS(app, origins=["https://your-frontend-url.onrender.com"])  # TODO: Replace with actual frontend URL

    # Health check route for Render
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

if __name__ == "__main__":
    main()

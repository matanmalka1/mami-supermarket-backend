"""Convenience runner for local development."""

from dotenv import load_dotenv
from pathlib import Path

# Load .env before creating app
load_dotenv(Path(__file__).parent / ".env")

from app import create_app


def main() -> None:
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()

"""Guards the env file baked into the server image (docker/Dockerfile -> /app/.env).

Notification and email links are built with full_url(), which joins paths onto
settings.SITE_URL. A missing SITE_URL silently falls back to localhost.
"""

from pathlib import Path

import dotenv

SERVER_ENV = Path(__file__).resolve().parents[3] / "docker" / "config" / "server.env"


def test_server_env_site_url_matches_csrf_origin():
    config = dotenv.dotenv_values(SERVER_ENV)
    site_url = config.get("SITE_URL")
    assert site_url, "SITE_URL missing: notification links would point at localhost"
    assert site_url.startswith("https://")
    assert site_url.rstrip("/") == config["CSRF_TRUSTED_ORIGINS"].rstrip("/")

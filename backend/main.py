"""Vercel service entrypoint.

Vercel Services resolves the FastAPI app as ``main:app`` at the service
root. Re-export the application defined in the ``app`` package so the
entrypoint path exists and matches that convention.
"""

from app.main import app

__all__ = ["app"]

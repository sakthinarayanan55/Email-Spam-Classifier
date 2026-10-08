import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app


class VercelPathMiddleware:
    """Normalizes PATH_INFO when Vercel serverless rewrites prepend /api/index[.py]."""

    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "")
        for prefix in ("/api/index.py", "/api/index"):
            if path == prefix:
                environ["PATH_INFO"] = "/"
                break
            elif path.startswith(prefix + "/"):
                remainder = path[len(prefix):]
                environ["PATH_INFO"] = remainder if remainder.startswith("/") else "/" + remainder
                break
        return self.wsgi_app(environ, start_response)


# Wrap Flask's WSGI app with the path normalizer
app.wsgi_app = VercelPathMiddleware(app.wsgi_app)

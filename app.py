from app import app
from core.config import settings

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.APP_PORT, debug=settings.DEBUG)

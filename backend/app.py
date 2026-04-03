import os
from flask import Flask
from flask_cors import CORS

from database.db import init_db
from routes.tasks import tasks_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173","https://ai-task-mangager.vercel.app"]}},
        supports_credentials=True
    )

    init_db()
    app.register_blueprint(tasks_bp, url_prefix="/api")

    @app.get("/health")
    def health_check():
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)

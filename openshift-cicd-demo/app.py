import os

from flask import Flask, jsonify


APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
app = Flask(__name__)


@app.get("/")
def home():
    """Return a welcome message for the demo application."""
    return "Welcome to openshift-cicd-demo!"


@app.get("/health")
def health():
    """Return the application health status."""
    return jsonify(status="healthy")


@app.get("/version")
def version():
    """Return the current application version."""
    return jsonify(version=APP_VERSION)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)

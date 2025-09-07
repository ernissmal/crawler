# App package initializer
from flask import Flask
from app.views.routes import routes

def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes)
    return app

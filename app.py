from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
from utils import mail
from routes import api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    jwt = JWTManager(app)
    CORS(app, resources=app.config['CORS_RESOURCES'])
    db.init_app(app)
    mail.init_app(app)
    
    app.register_blueprint(api, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from app.routes import main as main_bp
    app.register_blueprint(main_bp)

    from app.controllers.recipes_controller import recipes_bp
    app.register_blueprint(recipes_bp, url_prefix='/recipes')

    from app.controllers.user_controller import user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from app.controllers.api_recipes_controller import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
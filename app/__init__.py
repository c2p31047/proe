from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8'.format(**{
      'user': 'root',
      'password': '',
      'host': 'localhost',
      'db_name': 'app'
    })



    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    migrate.init_app(app, db)

    from .main import main
    app.register_blueprint(main)

    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    from .shelter import shelter_bp
    app.register_blueprint(shelter_bp)
    
    from .stock import stock_bp
    app.register_blueprint(stock_bp)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    return app

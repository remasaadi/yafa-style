from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, makedirs
from flask_login import LoginManager
from werkzeug.security import generate_password_hash


db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hererererer'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Transaction, Client

    with app.app_context():
        create_database(app)
        create_admin_user()  # יצירת משתמש מנהל ראשוני אם לא קיים

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

def create_database(app):
    if not path.exists('website'):
        makedirs('website')
    if not path.exists(path.join('website', DB_NAME)):
        with app.app_context():
            db.create_all()
            print('Created Database!')

def create_admin_user():
    from .models import User
    admin_password = generate_password_hash("admin123", method='pbkdf2:sha256')  # שינוי לאלגוריתם בטוח יותר
    phone_number = "0000000000"
    if not User.query.filter_by(phonenumber=phone_number).first():
        admin_user = User(first_name="Admin", phonenumber=phone_number, password=admin_password, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
        print('Admin user created with default password.')

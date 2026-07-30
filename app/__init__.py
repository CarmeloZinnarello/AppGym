from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from flask_wtf.csrf import CSRFProtect

from config import DevelopmentConfig

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    db.init_app(app)
    login_manager.init_app(app)
    csrf = CSRFProtect(app)
    from .models import User, Parametri  # <--- IMPORTIAMO QUI, DOPO db.init_app()

    with app.app_context():
        db.create_all()

        # Creazione utente admin se non esiste
        if User.query.filter_by(username="admin").first() is None:
            admin_user = User(
                username="admin",
                password=generate_password_hash("1234"),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()

    from .routes.home import bp as home_bp
    from .routes.auth import bp as auth_bp
    from .routes.admin import bp as admin_bp
    from .routes.user import bp as user_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    
    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User  # <--- IMPORTIAMO User SOLO QUI, PER EVITARE IMPORT CIRCOLARE
    return User.query.get(int(user_id))
    
def create_admin(app):
    with app.app_context():  # Necessario per accedere al database
        from app.models import User
        from werkzeug.security import generate_password_hash
        from app import db

        # Controlla se un utente admin esiste già
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Creazione dell'utente admin
            admin = User(
                username='admin',
                password=generate_password_hash('1234'),  # Sostituisci con una password sicura
                is_admin=1,
                is_worker=1
            )
            db.session.add(admin)
            db.session.commit()
            print("Utente admin creato con successo.")


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
import json
from datetime import datetime, timedelta, date

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    static_dir = os.path.abspath(os.path.join(basedir, '..', 'static'))
    app = Flask(__name__, static_folder=static_dir, template_folder='templates')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['OPENWEATHERMAP_API_KEY'] = os.environ.get('OPENWEATHERMAP_API_KEY', '')
    app.config['YANDEX_MAPS_API_KEY'] = os.environ.get('YANDEX_MAPS_API_KEY', '')
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # Токен действителен 1 час

    # Настройки для загрузки файлов
    upload_folder = os.path.join(static_dir, 'uploads', 'reports')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Папки для изображений сущностей
    waterbody_img_folder = os.path.join(static_dir, 'uploads', 'waterbodies')
    fish_img_folder = os.path.join(static_dir, 'uploads', 'fish')
    gear_img_folder = os.path.join(static_dir, 'uploads', 'gear')
    bait_img_folder = os.path.join(static_dir, 'uploads', 'bait')
    os.makedirs(waterbody_img_folder, exist_ok=True)
    os.makedirs(fish_img_folder, exist_ok=True)
    os.makedirs(gear_img_folder, exist_ok=True)
    os.makedirs(bait_img_folder, exist_ok=True)
    app.config['WATERBODY_IMAGES_FOLDER'] = waterbody_img_folder
    app.config['FISH_IMAGES_FOLDER'] = fish_img_folder
    app.config['GEAR_IMAGES_FOLDER'] = gear_img_folder
    app.config['BAIT_IMAGES_FOLDER'] = bait_img_folder

    # Инициализируем CSRF защиту
    csrf.init_app(app)

    @app.template_filter('from_json')
    def from_json_filter(s):
        try:
            return json.loads(s)
        except (TypeError, json.JSONDecodeError):
            return []

    @app.context_processor
    def inject_globals():
        return {
            'datetime': datetime,
            'timedelta': timedelta,
            'date': date,
            'config': {
                'YANDEX_MAPS_API_KEY': app.config.get('YANDEX_MAPS_API_KEY', ''),
            }
        }

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .routes import main
    app.register_blueprint(main)

    from .api import api
    app.register_blueprint(api, url_prefix='/api')

    # Добавляем CSRF токен в контекст для всех шаблонов
    @app.context_processor
    def inject_csrf_token():
        # Flask-WTF предоставляет csrf_token() в шаблонах автоматически
        # Но мы также можем передать его явно
        return {}

    with app.app_context():
        db.create_all()
        from .utils import seed_data
        seed_data()

    return app
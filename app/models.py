from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import validates

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')
    phone = db.Column(db.String(20), nullable=True, unique=True)
    birth_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    basin = db.Column(db.String(100), nullable=True)
    code = db.Column(db.String(10), nullable=True)

class Waterbody(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    area = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    access_info = db.Column(db.Text, default='Информация о доступе уточняется')
    infrastructure = db.Column(db.Text, default='Информация об инфраструктуре уточняется')
    rating = db.Column(db.Float, default=0.0)
    reports_count = db.Column(db.Integer, default=0)
    cover_image = db.Column(db.String(200), nullable=True, default='')
    region = db.relationship('Region', backref=db.backref('waterbodies', lazy=True))

class FishingRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    ban_start = db.Column(db.Date, nullable=True)
    ban_end = db.Column(db.Date, nullable=True)
    daily_limit_kg = db.Column(db.Float, nullable=True)
    allowed_gear = db.Column(db.Text, nullable=True)
    prohibited_gear = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(200), default='Приказ Минсельхоза РФ')
    region = db.relationship('Region', backref=db.backref('rules', lazy=True))

class FishSpecies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    latin_name = db.Column(db.String(50), default='')
    image = db.Column(db.String(200), nullable=True, default='')
    optimal_temp_min = db.Column(db.Float, default=10.0)
    optimal_temp_max = db.Column(db.Float, default=22.0)
    seasonality = db.Column(db.String(100), nullable=True, default='Не указана')
    features = db.Column(db.Text, nullable=True, default='Особенности не указаны')
    description = db.Column(db.Text, nullable=True, default='Описание отсутствует')

class WaterbodyFish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    waterbody_id = db.Column(db.Integer, db.ForeignKey('waterbody.id', ondelete='CASCADE'), nullable=False)
    fish_id = db.Column(db.Integer, db.ForeignKey('fish_species.id', ondelete='CASCADE'), nullable=False)
    fish = db.relationship('FishSpecies')

class FishingReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    waterbody_id = db.Column(db.Integer, db.ForeignKey('waterbody.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    weather = db.Column(db.String(200), default='Не указаны')
    weather_temp = db.Column(db.Float, nullable=True)
    weather_pressure = db.Column(db.Float, nullable=True)
    weather_wind_dir = db.Column(db.String(5), nullable=True)
    weather_wind_speed = db.Column(db.Float, nullable=True)
    weather_clouds = db.Column(db.String(50), nullable=True)
    gear = db.Column(db.String(500), nullable=True)
    bait = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    fish_caught = db.Column(db.String(200), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    rules_warnings = db.Column(db.Text, nullable=True)  # Предупреждения о нарушении правил
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    rejection_reason = db.Column(db.Text, nullable=True)
    moderated_at = db.Column(db.DateTime, nullable=True)
    moderated_by = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)

    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('reports', cascade='all, delete-orphan', lazy=True))
    moderator = db.relationship('User', foreign_keys=[moderated_by])
    waterbody = db.relationship('Waterbody', backref=db.backref('reports', cascade='all, delete-orphan', lazy=True))

    __table_args__ = (
        db.CheckConstraint('rating IS NULL OR (rating >= 1 AND rating <= 5)', name='check_rating_range'),
    )

    @property
    def is_approved(self):
        return self.status == 'approved'

    @is_approved.setter
    def is_approved(self, value):
        self.status = 'approved' if value else 'pending'

    @validates('rating')
    def validate_rating(self, key, rating):
        if rating is not None and (rating < 1 or rating > 5):
            raise ValueError("Рейтинг должен быть от 1 до 5")
        return rating

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    waterbody_id = db.Column(db.Integer, db.ForeignKey('waterbody.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('user_id', 'waterbody_id'),)
    waterbody = db.relationship('Waterbody')
    user = db.relationship('User', backref=db.backref('favorites', cascade='all, delete-orphan'))

class WeatherCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    waterbody_id = db.Column(db.Integer, db.ForeignKey('waterbody.id', ondelete='CASCADE'), nullable=False)
    temperature = db.Column(db.Float)
    pressure = db.Column(db.Float)
    humidity = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    wind_direction = db.Column(db.Float)
    weather_desc = db.Column(db.String(100))
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    waterbody = db.relationship('Waterbody', backref=db.backref('weather_caches', cascade='all, delete-orphan'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('fishing_report.id', ondelete='CASCADE'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('comments', cascade='all, delete-orphan'))
    report = db.relationship('FishingReport', backref=db.backref('comments', cascade='all, delete-orphan', lazy=True))

class DailyLimit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('fishing_rule.id', ondelete='CASCADE'), nullable=False)
    fish_id = db.Column(db.Integer, db.ForeignKey('fish_species.id', ondelete='CASCADE'), nullable=False)
    limit_kg = db.Column(db.Float, nullable=True)
    limit_pcs = db.Column(db.Integer, nullable=True)
    min_size_cm = db.Column(db.Integer, nullable=True)
    is_prohibited = db.Column(db.Boolean, default=False)
    rule = db.relationship('FishingRule', backref=db.backref('daily_limits', cascade='all, delete-orphan', lazy=True))
    fish = db.relationship('FishSpecies')

class Gear(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(200), nullable=True, default='')

class Bait(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(200), nullable=True, default='')

class FishGear(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fish_id = db.Column(db.Integer, db.ForeignKey('fish_species.id', ondelete='CASCADE'), nullable=False)
    gear_id = db.Column(db.Integer, db.ForeignKey('gear.id', ondelete='CASCADE'), nullable=False)
    fish = db.relationship('FishSpecies', backref=db.backref('gear_links', cascade='all, delete-orphan'))
    gear = db.relationship('Gear', backref=db.backref('fish_links', cascade='all, delete-orphan'))

class FishBait(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fish_id = db.Column(db.Integer, db.ForeignKey('fish_species.id', ondelete='CASCADE'), nullable=False)
    bait_id = db.Column(db.Integer, db.ForeignKey('bait.id', ondelete='CASCADE'), nullable=False)
    fish = db.relationship('FishSpecies', backref=db.backref('bait_links', cascade='all, delete-orphan'))
    bait = db.relationship('Bait', backref=db.backref('fish_links', cascade='all, delete-orphan'))

# ============ ТАБЛИЦЫ ДЛЯ СВЯЗИ ОТЧЕТОВ СО СНАСТЯМИ И НАЖИВКАМИ ============

class ReportGear(db.Model):
    __tablename__ = 'report_gear'
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('fishing_report.id', ondelete='CASCADE'), nullable=False)
    gear_id = db.Column(db.Integer, db.ForeignKey('gear.id', ondelete='SET NULL'), nullable=True)
    gear_name = db.Column(db.String(100), nullable=False)
    report = db.relationship('FishingReport', backref=db.backref('report_gears', cascade='all, delete-orphan'))
    gear = db.relationship('Gear')

class ReportBait(db.Model):
    __tablename__ = 'report_bait'
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('fishing_report.id', ondelete='CASCADE'), nullable=False)
    bait_id = db.Column(db.Integer, db.ForeignKey('bait.id', ondelete='SET NULL'), nullable=True)
    bait_name = db.Column(db.String(100), nullable=False)
    report_gear_id = db.Column(db.Integer, db.ForeignKey('report_gear.id', ondelete='CASCADE'), nullable=True)
    report = db.relationship('FishingReport', backref=db.backref('report_baits', cascade='all, delete-orphan'))
    bait = db.relationship('Bait')
    report_gear = db.relationship('ReportGear', backref=db.backref('baits', cascade='all, delete-orphan'))

# ============ НОВЫЕ МОДЕЛИ ДЛЯ ПРАВИЛ РЫБОЛОВСТВА ============

class RegionalFishingRule(db.Model):
    """Региональные правила рыболовства для конкретных видов рыб"""
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    fish_id = db.Column(db.Integer, db.ForeignKey('fish_species.id'), nullable=False)

    # Период нерестового запрета
    ban_start = db.Column(db.Date, nullable=True)
    ban_end = db.Column(db.Date, nullable=True)

    # Ограничения на вылов
    min_size_cm = db.Column(db.Integer, nullable=True, default=0)
    daily_limit_kg = db.Column(db.Float, nullable=True)
    daily_limit_pcs = db.Column(db.Integer, nullable=True)

    # Разрешённые и запрещённые снасти (JSON)
    allowed_gear = db.Column(db.Text, nullable=True)
    prohibited_gear = db.Column(db.Text, nullable=True)

    # Полный запрет на вылов
    is_prohibited = db.Column(db.Boolean, default=False)

    # Связи
    region = db.relationship('Region', backref=db.backref('fishing_rules', lazy=True))
    fish = db.relationship('FishSpecies', backref=db.backref('regional_rules', lazy=True))

class SeasonalBan(db.Model):
    """Сезонные запреты на рыболовство (нерестовые периоды)"""
    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    ban_start = db.Column(db.Date, nullable=False)
    ban_end = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(500), nullable=True)

    region = db.relationship('Region', backref=db.backref('seasonal_bans', lazy=True))

class RestrictedArea(db.Model):
    """Запретные зоны для рыболовства (заказники, нерестилища)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    area_type = db.Column(db.String(100), nullable=True)  # Тип зоны: нерестилище, заповедник и т.д.
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=True)
    geometry_geojson = db.Column(db.Text, nullable=True)  # GeoJSON с координатами зоны
    restriction_start = db.Column(db.Date, nullable=False)
    restriction_end = db.Column(db.Date, nullable=False)

    region = db.relationship('Region', backref=db.backref('restricted_areas', lazy=True))

# ============ МОДЕЛЬ ДЛЯ ИЗОБРАЖЕНИЙ ОТЧЁТОВ ============

class ReportImage(db.Model):
    """Изображения, прикреплённые к отчётам о рыбалке"""
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('fishing_report.id', ondelete='CASCADE'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Имя файла на диске
    original_name = db.Column(db.String(255), nullable=False)  # Оригинальное имя файла
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связь с отчётом
    report = db.relationship('FishingReport', backref=db.backref('images', cascade='all, delete-orphan', lazy=True))
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf.csrf import generate_csrf
from .models import (
    User, Waterbody, Region, FishSpecies, WaterbodyFish,
    FishingRule, FishingReport, Favorite, Gear, Bait,
    FishGear, FishBait, WeatherCache, Comment, DailyLimit,
    ReportGear, ReportBait, ReportImage,
    RegionalFishingRule, SeasonalBan, RestrictedArea
)
from . import db, csrf
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import date, datetime
from sqlalchemy import func
import json
import re
import uuid
import os

main = Blueprint('main', __name__)

# -------------------- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ (импортируется из utils) --------------------
from .utils import update_waterbody_stats

# -------------------- CSRF токен для шаблонов --------------------
@main.context_processor
def inject_csrf_token():
    return {'csrf_token': generate_csrf}

# -------------------- ВРЕМЕННЫЙ МАРШРУТ ДЛЯ ПЕРЕСЧЁТА РЕЙТИНГОВ --------------------
@main.route('/fix-ratings')
def fix_ratings():
    waterbodies = Waterbody.query.all()
    for wb in waterbodies:
        reports = FishingReport.query.filter(
            FishingReport.waterbody_id == wb.id,
            FishingReport.status == 'approved',
            FishingReport.rating.isnot(None)
        ).all()
        valid_ratings = [r.rating for r in reports if 1 <= r.rating <= 5]
        if valid_ratings:
            avg = round(sum(valid_ratings) / len(valid_ratings), 1)
            wb.rating = avg
        else:
            wb.rating = 0.0
        wb.reports_count = FishingReport.query.filter_by(
            waterbody_id=wb.id, status='approved'
        ).count()
        db.session.commit()
    return "Рейтинги пересчитаны. Теперь удалите этот маршрут."

# -------------------- главная --------------------
@main.route('/')
def index():
    regions = Region.query.order_by(Region.name).all()
    fish_species = FishSpecies.query.order_by(FishSpecies.name).all()
    return render_template('index.html', regions=regions, fish_species=fish_species)

# -------------------- каталог водоёмов (карточки) --------------------
@main.route('/waterbodies')
def waterbodies_catalog():
    page = request.args.get('page', 1, type=int)
    per_page = 24
    q = Waterbody.query.order_by(Waterbody.reports_count.desc(), Waterbody.rating.desc())
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    waterbodies = pagination.items
    return render_template('waterbodies_catalog.html', waterbodies=waterbodies, pagination=pagination)

# -------------------- водоём --------------------
@main.route('/waterbody/<int:id>')
def waterbody_detail(id):
    waterbody = Waterbody.query.get_or_404(id)
    region = Region.query.get(waterbody.region_id)
    fish_list = (
        db.session.query(FishSpecies)
        .join(WaterbodyFish)
        .filter(WaterbodyFish.waterbody_id == id)
        .all()
    )
    reports = (
        FishingReport.query
        .filter_by(waterbody_id=id, status='approved')
        .order_by(FishingReport.date.desc())
        .limit(10)
        .all()
    )
    return render_template(
        'waterbody.html',
        waterbody=waterbody,
        region=region,
        fish_list=fish_list,
        reports=reports
    )

# -------------------- регистрация --------------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    username_value = ''
    email_value = ''
    full_name_value = ''
    phone_value = ''
    birth_date_value = ''

    if request.method == 'POST':
        username_value = request.form.get('username', '').strip()
        email_value = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        full_name_value = request.form.get('full_name', '').strip()
        phone_value = (request.form.get('phone') or '').strip()
        birth_date_value = (request.form.get('birth_date') or '').strip()

        errors = []
        if not request.form.get('agree'):
            errors.append('Необходимо принять условия соглашения')
        if not username_value or not email_value or not password or not full_name_value or not phone_value or not birth_date_value:
            errors.append('Все поля обязательны для заполнения (включая телефон и дату рождения)')
        
        if User.query.filter_by(username=username_value).first():
            errors.append('Пользователь с таким логином уже существует')
        
        if User.query.filter_by(email=email_value).first():
            errors.append('Пользователь с таким email уже существует')
        
        if len(password) < 4:
            errors.append('Пароль должен содержать минимум 4 символа')

        if phone_value:
            phone_clean = re.sub(r'\D', '', phone_value)
            if len(phone_clean) != 10:
                errors.append('Телефон должен содержать 10 цифр после +7')
            else:
                formatted_phone = f'+7 ({phone_clean[0:3]}) {phone_clean[3:6]}-{phone_clean[6:8]}-{phone_clean[8:10]}'
                if User.query.filter_by(phone=formatted_phone).first():
                    errors.append('Пользователь с таким телефоном уже существует')

        bd = None
        try:
            bd = date.fromisoformat(birth_date_value)
            today = date.today()
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
            if age < 18:
                errors.append('Регистрация доступна только пользователям старше 18 лет')
            if age > 130:
                errors.append('Указан некорректный возраст (максимум 130 лет)')
        except Exception:
            errors.append('Некорректная дата рождения')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('register.html', 
                                  username_value=username_value,
                                  email_value=email_value,
                                  full_name_value=full_name_value,
                                  phone_value=phone_value,
                                  birth_date_value=birth_date_value)

        phone_clean = re.sub(r'\D', '', phone_value)
        formatted_phone = f'+7 ({phone_clean[0:3]}) {phone_clean[3:6]}-{phone_clean[6:8]}-{phone_clean[8:10]}'

        new_user = User(
            username=username_value, email=email_value, full_name=full_name_value,
            phone=formatted_phone, birth_date=bd
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', 
                          username_value=username_value,
                          email_value=email_value,
                          full_name_value=full_name_value,
                          phone_value=phone_value,
                          birth_date_value=birth_date_value)

# -------------------- вход / выход --------------------
@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Добро пожаловать, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))

        flash('Неверный логин или пароль', 'danger')
        return render_template('login.html', username_value=username)

    return render_template('login.html', username_value='')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('main.index'))

# -------------------- отчёт (создание) --------------------
@main.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    waterbodies = Waterbody.query.order_by(Waterbody.name).all()
    fish_species = FishSpecies.query.order_by(FishSpecies.name).all()
    gears = Gear.query.order_by(Gear.name).all()
    baits = Bait.query.order_by(Bait.name).all()

    waterbody_names = [wb.name for wb in waterbodies]
    fish_names = [f.name for f in fish_species]
    gear_names = [g.name for g in gears]
    bait_names = [b.name for b in baits]

    preselected_waterbody = request.args.get('waterbody_name', '')
    
    form_data = {
        'waterbody_name': '',
        'date': '',
        'time_of_day': 'day',
        'weather_temp': '',
        'weather_pressure': '',
        'weather_wind_dir': '',
        'weather_wind_speed': '',
        'weather_clouds': '',
        'description': '',
        'rating': '',
        'gear_names': [],
        'gear_baits': [],
        'fish_names': [],
        'fish_kg': [],
        'fish_pcs': []
    }

    if request.method == 'POST':
        # === ДИАГНОСТИКА ===
        current_app.logger.info("=== REPORT POST ===")
        current_app.logger.info(f"request.files keys: {list(request.files.keys())}")
        if 'images' in request.files:
            files = request.files.getlist('images')
            current_app.logger.info(f"Number of files in 'images': {len(files)}")
            for idx, f in enumerate(files):
                current_app.logger.info(f"  File {idx}: {f.filename}")
        else:
            current_app.logger.warning("No 'images' field in request.files")
        # === КОНЕЦ ДИАГНОСТИКИ ===

        waterbody_name = request.form.get('waterbody_name', '').strip()
        report_date = request.form.get('date')
        time_of_day = request.form.get('time_of_day', 'day')
        weather_temp = request.form.get('weather_temp', type=float)
        weather_pressure = request.form.get('weather_pressure', type=float)
        if weather_pressure is not None:
            weather_pressure = round(weather_pressure, 1)
        weather_wind_dir = (request.form.get('weather_wind_dir') or '').strip()
        weather_wind_speed = request.form.get('weather_wind_speed', type=float)
        weather_clouds = (request.form.get('weather_clouds') or '').strip()
        description = request.form.get('description', '')[:5000]
        rating = request.form.get('rating', type=int)
        
        form_data['waterbody_name'] = waterbody_name
        form_data['date'] = report_date
        form_data['time_of_day'] = time_of_day
        form_data['weather_temp'] = weather_temp if weather_temp else ''
        form_data['weather_pressure'] = weather_pressure if weather_pressure else ''
        form_data['weather_wind_dir'] = weather_wind_dir
        form_data['weather_wind_speed'] = weather_wind_speed if weather_wind_speed else ''
        form_data['weather_clouds'] = weather_clouds
        form_data['description'] = description
        form_data['rating'] = rating if rating else ''

        errors = []

        waterbody = None
        if not waterbody_name:
            errors.append('Выберите или введите название водоёма')
        else:
            waterbody = Waterbody.query.filter(func.lower(Waterbody.name) == func.lower(waterbody_name)).first()
            if not waterbody:
                errors.append(f'Водоём "{waterbody_name}" не найден в базе')

        if not report_date:
            errors.append('Укажите дату рыбалки')
        else:
            try:
                rdate = date.fromisoformat(report_date)
                if rdate > date.today():
                    errors.append('Дата рыбалки не может быть в будущем')
            except ValueError:
                errors.append('Некорректная дата')

        if weather_temp is not None and (weather_temp < -50 or weather_temp > 60):
            errors.append('Температура должна быть от -50°C до +60°C')
        if weather_pressure is not None and (weather_pressure < 600 or weather_pressure > 850):
            errors.append('Давление должно быть от 600 до 850 мм рт.ст.')
        if weather_wind_speed is not None and (weather_wind_speed < 0 or weather_wind_speed > 50):
            errors.append('Скорость ветра должна быть от 0 до 50 м/с')

        gear_names_list = request.form.getlist('gear_name[]')
        bait_names_for_gear_json = request.form.getlist('bait_names_for_gear[]')
        
        form_data['gear_names'] = gear_names_list
        form_data['gear_baits'] = []
        
        gear_names_list = [g.strip() for g in gear_names_list if g.strip()]
        
        gear_baits_list = []
        for i, bait_json in enumerate(bait_names_for_gear_json):
            if i < len(gear_names_list):
                try:
                    baits_for_gear = json.loads(bait_json) if bait_json else []
                    gear_baits_list.append([b.strip() for b in baits_for_gear if b.strip()])
                except:
                    gear_baits_list.append([])
            else:
                gear_baits_list.append([])
        
        form_data['gear_baits'] = gear_baits_list
        
        all_baits = []
        for baits in gear_baits_list:
            all_baits.extend(baits)
        bait_names_list = list(dict.fromkeys(all_baits))

        fish_names_list = request.form.getlist('fish_name[]')
        fish_kg = request.form.getlist('fish_kg[]')
        fish_pcs = request.form.getlist('fish_pcs[]')
        
        form_data['fish_names'] = fish_names_list
        form_data['fish_kg'] = fish_kg
        form_data['fish_pcs'] = fish_pcs

        fish_caught = []
        has_valid_fish = False

        for i in range(len(fish_names_list)):
            name = fish_names_list[i].strip() if i < len(fish_names_list) else ''
            kg = 0.0
            pcs = 0
            try:
                kg = float(fish_kg[i]) if i < len(fish_kg) and fish_kg[i] else 0.0
            except (ValueError, TypeError):
                kg = 0.0
            try:
                pcs = int(fish_pcs[i]) if i < len(fish_pcs) and fish_pcs[i] else 0
            except (ValueError, TypeError):
                pcs = 0

            if name:
                if kg < 0:
                    errors.append(f'Вес для "{name}" не может быть отрицательным')
                if pcs < 0:
                    errors.append(f'Количество для "{name}" не может быть отрицательным')
                if kg > 100:
                    errors.append(f'Вес для "{name}" не более 100 кг')
                if pcs > 999:
                    errors.append(f'Количество для "{name}" не более 999 шт')
                if kg == 0 and pcs == 0:
                    errors.append(f'Для "{name}" укажите вес ИЛИ количество')
                else:
                    has_valid_fish = True
                    fish_caught.append({'name': name, 'kg': kg, 'pcs': pcs})

        if not has_valid_fish:
            errors.append('Добавьте хотя бы один вид рыбы с указанием веса или количества')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('report.html', waterbodies=waterbodies, fish_species=fish_species,
                                   gears=gears, baits=baits, waterbody_names=waterbody_names,
                                   fish_names=fish_names, gear_names=gear_names, bait_names=bait_names,
                                   preselected_waterbody=preselected_waterbody, form_data=form_data)

        weather_parts = []
        if weather_temp is not None:
            weather_parts.append(f"t={weather_temp}°C")
        if weather_pressure is not None:
            weather_parts.append(f"P={weather_pressure} мм рт.ст.")
        if weather_wind_dir:
            weather_parts.append(f"ветер {weather_wind_dir}")
        if weather_wind_speed is not None:
            weather_parts.append(f"{weather_wind_speed} м/с")
        if weather_clouds:
            weather_parts.append(weather_clouds)
        weather = ", ".join(weather_parts) if weather_parts else 'Не указаны'
        
        gear_str = ", ".join(gear_names_list) if gear_names_list else ''
        bait_str = ", ".join(bait_names_list) if bait_names_list else ''
        
        if rating and (rating < 1 or rating > 5):
            rating = None

        r = FishingReport(
            user_id=current_user.id,
            waterbody_id=waterbody.id,
            date=date.fromisoformat(report_date),
            weather=weather,
            weather_temp=weather_temp,
            weather_pressure=weather_pressure,
            weather_wind_dir=weather_wind_dir or None,
            weather_wind_speed=weather_wind_speed,
            weather_clouds=weather_clouds or None,
            gear=gear_str,
            bait=bait_str,
            description=description,
            fish_caught=json.dumps(fish_caught, ensure_ascii=False),
            rating=rating if rating else None,
            status='pending'
        )
        db.session.add(r)
        db.session.flush()

        # Обработка загруженных изображений (исправленная версия)
        if 'images' in request.files:
            files = request.files.getlist('images')
            current_app.logger.info(f"Saving {len(files)} images for report {r.id}")
            for file in files:
                if file and file.filename != '':
                    file.seek(0, os.SEEK_END)
                    size = file.tell()
                    file.seek(0)
                    if size == 0:
                        current_app.logger.warning(f"Empty file skipped: {file.filename}")
                        continue

                    original_filename = file.filename
                    # Определяем расширение из оригинального имени (в нижнем регистре)
                    if '.' in original_filename:
                        ext = original_filename.rsplit('.', 1)[1].lower()
                        name_part = original_filename.rsplit('.', 1)[0]
                    else:
                        ext = ''
                        name_part = original_filename

                    if ext not in current_app.config['ALLOWED_EXTENSIONS']:
                        current_app.logger.warning(f"Invalid file type: {original_filename} (ext: {ext})")
                        continue

                    # Безопасное имя без расширения
                    safe_name = secure_filename(name_part) if name_part else 'image'
                    if not safe_name:
                        safe_name = 'image'
                    # Собираем полное безопасное имя
                    safe_filename = f"{safe_name}.{ext}"
                    unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
                    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                    file.save(upload_path)
                    current_app.logger.info(f"Saved image: {unique_filename} ({size} bytes)")

                    report_image = ReportImage(
                        report_id=r.id,
                        filename=unique_filename,
                        original_name=original_filename
                    )
                    db.session.add(report_image)
        else:
            current_app.logger.info("No images in request")

        for idx, gear_name in enumerate(gear_names_list):
            gear = Gear.query.filter(func.lower(Gear.name) == func.lower(gear_name)).first()
            report_gear = ReportGear(
                report_id=r.id,
                gear_id=gear.id if gear else None,
                gear_name=gear_name
            )
            db.session.add(report_gear)
            db.session.flush()

            baits_for_this_gear = gear_baits_list[idx] if idx < len(gear_baits_list) else []
            for bait_name in baits_for_this_gear:
                bait = Bait.query.filter(func.lower(Bait.name) == func.lower(bait_name)).first()
                report_bait = ReportBait(
                    report_id=r.id,
                    bait_id=bait.id if bait else None,
                    bait_name=bait_name,
                    report_gear_id=report_gear.id
                )
                db.session.add(report_bait)

        try:
            db.session.commit()
            current_app.logger.info(f"Report {r.id} committed, images count: {len(r.images) if r.images else 0}")
            flash('Отчёт успешно добавлен и отправлен на модерацию', 'success')
            return redirect(url_for('main.profile'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to commit report: {str(e)}")
            flash('Произошла ошибка при сохранении отчёта. Пожалуйста, попробуйте ещё раз.', 'danger')
            return render_template('report.html', waterbodies=waterbodies, fish_species=fish_species,
                                   gears=gears, baits=baits, waterbody_names=waterbody_names,
                                   fish_names=fish_names, gear_names=gear_names, bait_names=bait_names,
                                   preselected_waterbody=preselected_waterbody, form_data=form_data)

    return render_template('report.html', waterbodies=waterbodies, fish_species=fish_species,
                           gears=gears, baits=baits, waterbody_names=waterbody_names,
                           fish_names=fish_names, gear_names=gear_names, bait_names=bait_names,
                           preselected_waterbody=preselected_waterbody, form_data=form_data)

# -------------------- просмотр одного отчёта (с подгрузкой связанных данных) --------------------
@main.route('/report/<int:id>')
def view_report(id):
    from sqlalchemy.orm import joinedload
    report = FishingReport.query.options(
        joinedload(FishingReport.report_gears).joinedload(ReportGear.baits),
        joinedload(FishingReport.images)
    ).get_or_404(id)
    can_view = report.status == 'approved' or (
        current_user.is_authenticated and (
            current_user.id == report.user_id or
            current_user.role in ('moderator', 'admin')
        )
    )
    if not can_view:
        flash('Отчёт не прошёл модерацию или недоступен', 'danger')
        return redirect(url_for('main.index'))
    return render_template('view_report.html', report=report)

# -------------------- общая страница отчётов --------------------
@main.route('/reports')
def reports_page():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    q = FishingReport.query.filter_by(status='approved').order_by(FishingReport.date.desc())
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    reports = pagination.items
    return render_template('reports.html', reports=reports, pagination=pagination)

# -------------------- личный кабинет --------------------
@main.route('/profile')
@login_required
def profile():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    if year and (year < 2000 or year > 2030):
        flash('Год должен быть в диапазоне 2000–2030', 'danger')
        year = None
    if month and (month < 1 or month > 12):
        flash('Месяц должен быть от 1 до 12', 'danger')
        month = None

    q = FishingReport.query.filter_by(user_id=current_user.id).order_by(FishingReport.date.desc())
    if year:
        q = q.filter(db.extract('year', FishingReport.date) == year)
    if month:
        q = q.filter(db.extract('month', FishingReport.date) == month)
    reports = q.all()

    total_trips = len(reports)
    total_kg = 0.0
    waterbody_counts = {}
    fish_counts = {}

    for r in reports:
        waterbody_counts[r.waterbody_id] = waterbody_counts.get(r.waterbody_id, 0) + 1
        try:
            fish_data = json.loads(r.fish_caught) if r.fish_caught else []
        except Exception:
            fish_data = []
        for item in fish_data:
            name = (item.get('name') or '').strip()
            kg = float(item.get('kg') or 0)
            pcs = int(item.get('pcs') or 0)
            total_kg += kg
            if name:
                fish_counts[name] = fish_counts.get(name, 0) + max(1, pcs)

    fav_wb_id = max(waterbody_counts, key=waterbody_counts.get) if waterbody_counts else None
    fav_waterbody = Waterbody.query.get(fav_wb_id) if fav_wb_id else None
    top_fish = max(fish_counts, key=fish_counts.get) if fish_counts else None

    favorites = (
        Favorite.query
        .filter_by(user_id=current_user.id)
        .order_by(Favorite.created_at.desc())
        .all()
    )

    return render_template(
        'profile.html', reports=reports, favorites=favorites,
        stats={
            "total_trips": total_trips,
            "total_kg": round(total_kg, 1),
            "fav_waterbody": fav_waterbody.name if fav_waterbody else "—",
            "top_fish": top_fish or "—",
        },
        year=year, month=month
    )

# -------------------- прогноз клёва --------------------
@main.route('/forecast')
def forecast_page():
    waterbodies = Waterbody.query.order_by(Waterbody.name).all()
    return render_template('forecast.html', waterbodies=waterbodies)

# -------------------- модерация --------------------
@main.route('/moderate')
@login_required
def moderate_page():
    if current_user.role not in ('moderator', 'admin'):
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('main.index'))
    reports = (
        FishingReport.query
        .filter_by(status='pending')
        .order_by(FishingReport.created_at.desc())
        .limit(50)
        .all()
    )
    return render_template('moderate.html', reports=reports)

# -------------------- справочники --------------------
@main.route('/rules')
def rules_page():
    return render_template('rules.html')

@main.route('/fish')
def fish_catalog():
    fish = FishSpecies.query.order_by(FishSpecies.name).all()
    return render_template('fish.html', fish=fish)

@main.route('/fish/<int:id>')
def fish_detail(id):
    fish = FishSpecies.query.get_or_404(id)
    waterbodies = (
        db.session.query(Waterbody)
        .join(WaterbodyFish, WaterbodyFish.waterbody_id == Waterbody.id)
        .filter(WaterbodyFish.fish_id == fish.id)
        .order_by(Waterbody.reports_count.desc(), Waterbody.name.asc())
        .all()
    )
    gears = [link.gear for link in fish.gear_links]
    baits = [link.bait for link in fish.bait_links]
    return render_template('fish_detail.html', fish=fish, waterbodies=waterbodies, gears=gears, baits=baits)

@main.route('/gear')
def gear_page():
    gears = Gear.query.order_by(Gear.category.asc(), Gear.name.asc()).all()
    return render_template('gear.html', gears=gears)

@main.route('/gear/<int:id>')
def gear_detail(id):
    gear = Gear.query.get_or_404(id)
    fish_list = [link.fish for link in gear.fish_links]
    return render_template('gear_detail.html', gear=gear, fish_list=fish_list)

@main.route('/bait')
def bait_page():
    baits = Bait.query.order_by(Bait.category.asc(), Bait.name.asc()).all()
    return render_template('bait.html', baits=baits)

@main.route('/bait/<int:id>')
def bait_detail(id):
    bait = Bait.query.get_or_404(id)
    fish_list = [link.fish for link in bait.fish_links]
    return render_template('bait_detail.html', bait=bait, fish_list=fish_list)

# -------------------- правовая информация --------------------
@main.route('/policy')
def policy():
    return render_template('policy.html', page='policy')

@main.route('/agreement')
def user_agreement():
    return render_template('policy.html', page='agreement')

@main.route('/legal')
def legal():
    return render_template('policy.html', page='legal')

# -------------------- АДМИН-ПАНЕЛЬ --------------------
def admin_required(f):
    from functools import wraps
    @wraps(f)
    @login_required
    def wrap(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Доступ запрещён', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return wrap

def super_admin_required(f):
    from functools import wraps
    @wraps(f)
    @login_required
    def wrap(*args, **kwargs):
        if current_user.id != 1:
            flash('Доступ запрещён. Только главный администратор может выполнять это действие.', 'danger')
            return redirect(url_for('main.admin_users'))
        return f(*args, **kwargs)
    return wrap

@main.route('/admin')
@admin_required
def admin_panel():
    users_count = User.query.count()
    waterbodies_count = Waterbody.query.count()
    reports_count = FishingReport.query.count()
    fish_count = FishSpecies.query.count()
    gear_count = Gear.query.count()
    bait_count = Bait.query.count()
    # Считаем все типы правил
    rules_count = (
        FishingRule.query.count() +
        RegionalFishingRule.query.count() +
        SeasonalBan.query.count() +
        RestrictedArea.query.count() +
        DailyLimit.query.count()
    )
    return render_template(
        'admin/panel.html',
        users_count=users_count, waterbodies_count=waterbodies_count,
        reports_count=reports_count, fish_count=fish_count,
        gear_count=gear_count, bait_count=bait_count, rules_count=rules_count
    )

# --- админ: пользователи ---
@main.route('/admin/users', methods=['GET', 'POST'])
@admin_required
def admin_users():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            role = request.form.get('role', 'user')
            if role == 'admin' and current_user.id != 1:
                flash('Только главный администратор может создавать других администраторов', 'danger')
                return redirect(url_for('main.admin_users'))
            
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            birth_date_str = request.form.get('birth_date', '').strip()
            
            if username and email and password and full_name:
                if User.query.filter_by(username=username).first():
                    flash('Пользователь с таким логином уже существует', 'danger')
                    return redirect(url_for('main.admin_users'))
                if User.query.filter_by(email=email).first():
                    flash('Пользователь с таким email уже существует', 'danger')
                    return redirect(url_for('main.admin_users'))
                
                new_user = User(username=username, email=email, full_name=full_name, role=role)
                if phone:
                    new_user.phone = phone
                if birth_date_str:
                    try:
                        new_user.birth_date = date.fromisoformat(birth_date_str)
                    except ValueError:
                        pass
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                flash('Пользователь создан', 'success')
            else:
                flash('Заполните все обязательные поля', 'danger')
        
        elif action == 'edit':
            user_id = request.form.get('user_id', type=int)
            user = User.query.get_or_404(user_id)
            
            if user.role == 'admin' and current_user.id != 1:
                flash('Только главный администратор может редактировать других администраторов', 'danger')
                return redirect(url_for('main.admin_users'))
            
            new_role = request.form.get('role', user.role)
            if user.role == 'admin' and new_role != 'admin' and current_user.id != 1:
                flash('Только главный администратор может изменять роль администратора', 'danger')
                return redirect(url_for('main.admin_users'))
            
            if new_role == 'admin' and current_user.id != 1:
                flash('Только главный администратор может назначать других администраторов', 'danger')
                return redirect(url_for('main.admin_users'))
            
            user.username = request.form.get('username', '').strip() or user.username
            user.email = request.form.get('email', '').strip() or user.email
            user.full_name = request.form.get('full_name', '').strip() or user.full_name
            user.role = new_role
            
            phone = request.form.get('phone', '').strip()
            user.phone = phone if phone else None
            
            birth_date_str = request.form.get('birth_date', '').strip()
            if birth_date_str:
                try:
                    user.birth_date = date.fromisoformat(birth_date_str)
                except ValueError:
                    pass
            else:
                user.birth_date = None
            
            password = request.form.get('password', '')
            if password:
                user.set_password(password)
            
            db.session.commit()
            flash('Пользователь обновлён', 'success')
        
        elif action == 'delete':
            user_id = request.form.get('user_id', type=int)
            user = User.query.get_or_404(user_id)
            
            if user.id == current_user.id:
                flash('Нельзя удалить самого себя', 'danger')
                return redirect(url_for('main.admin_users'))
            
            if user.role == 'admin' and current_user.id != 1:
                flash('Только главный администратор может удалять других администраторов', 'danger')
                return redirect(url_for('main.admin_users'))
            
            db.session.delete(user)
            db.session.commit()
            flash('Пользователь удалён', 'success')
        
        return redirect(url_for('main.admin_users'))
    
    users = User.query.order_by(User.role.asc(), User.username.asc()).all()
    return render_template('admin/users.html', users=users, current_user_id=current_user.id)

# --- админ: водоёмы ---
@main.route('/admin/waterbodies', methods=['GET', 'POST'])
@admin_required
def admin_waterbodies():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            name = request.form.get('name', '').strip()
            wb_type = request.form.get('type', '').strip()
            region_id = request.form.get('region_id', type=int)
            lat = request.form.get('latitude', type=float)
            lon = request.form.get('longitude', type=float)
            area = request.form.get('area', '').strip()
            access_info = request.form.get('access_info', '').strip()
            infrastructure = request.form.get('infrastructure', '').strip()
            description = request.form.get('description', '').strip()
            fish_ids_str = request.form.get('fish_ids', '').strip()

            # Обработка загруженного изображения
            cover_image_file = request.files.get('cover_image')
            cover_image_filename = ''
            if cover_image_file and cover_image_file.filename:
                ext = cover_image_file.filename.rsplit('.', 1)[1].lower() if '.' in cover_image_file.filename else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    safe_name = secure_filename(cover_image_file.filename.rsplit('.', 1)[0]) or 'image'
                    unique_name = f"{uuid.uuid4().hex}_{safe_name}.{ext}"
                    save_path = os.path.join(current_app.config['WATERBODY_IMAGES_FOLDER'], unique_name)
                    cover_image_file.save(save_path)
                    cover_image_filename = f"uploads/waterbodies/{unique_name}"

            if name and wb_type and region_id:
                wb = Waterbody(
                    name=name, type=wb_type, region_id=region_id,
                    latitude=lat, longitude=lon, area=area,
                    access_info=access_info or 'Информация о доступе уточняется',
                    infrastructure=infrastructure or 'Информация об инфраструктуре уточняется',
                    description=description,
                    cover_image=cover_image_filename
                )
                db.session.add(wb)
                db.session.flush()
                
                if fish_ids_str:
                    fish_ids = [int(x) for x in fish_ids_str.split(',') if x.strip().isdigit()]
                    for fish_id in fish_ids:
                        db.session.add(WaterbodyFish(waterbody_id=wb.id, fish_id=fish_id))
                
                db.session.commit()
                flash('Водоём создан', 'success')
            else:
                flash('Заполните обязательные поля (название, тип, регион)', 'danger')
        
        elif action == 'edit':
            wb_id = request.form.get('wb_id', type=int)
            wb = Waterbody.query.get_or_404(wb_id)

            wb.name = request.form.get('name', '').strip() or wb.name
            wb.type = request.form.get('type', '').strip() or wb.type
            region_id = request.form.get('region_id', type=int)
            if region_id:
                wb.region_id = region_id

            lat = request.form.get('latitude', type=float)
            if lat is not None:
                wb.latitude = lat
            lon = request.form.get('longitude', type=float)
            if lon is not None:
                wb.longitude = lon

            area = request.form.get('area', '').strip()
            if area:
                wb.area = area

            access_info = request.form.get('access_info', '').strip()
            if access_info:
                wb.access_info = access_info

            infrastructure = request.form.get('infrastructure', '').strip()
            if infrastructure:
                wb.infrastructure = infrastructure

            description = request.form.get('description', '').strip()
            if description:
                wb.description = description

            # Обработка загруженного изображения
            cover_image_file = request.files.get('cover_image')
            if cover_image_file and cover_image_file.filename:
                ext = cover_image_file.filename.rsplit('.', 1)[1].lower() if '.' in cover_image_file.filename else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    safe_name = secure_filename(cover_image_file.filename.rsplit('.', 1)[0]) or 'image'
                    unique_name = f"{uuid.uuid4().hex}_{safe_name}.{ext}"
                    save_path = os.path.join(current_app.config['WATERBODY_IMAGES_FOLDER'], unique_name)
                    cover_image_file.save(save_path)
                    new_cover_image_filename = f"uploads/waterbodies/{unique_name}"

                    # Удаление старого файла
                    if wb.cover_image:
                        old_path = os.path.join(current_app.config['WATERBODY_IMAGES_FOLDER'], os.path.basename(wb.cover_image))
                        if os.path.exists(old_path):
                            os.remove(old_path)

                    wb.cover_image = new_cover_image_filename

            fish_ids_str = request.form.get('fish_ids', '').strip()

            WaterbodyFish.query.filter_by(waterbody_id=wb.id).delete()

            if fish_ids_str:
                fish_ids = [int(x) for x in fish_ids_str.split(',') if x.strip().isdigit()]
                for fish_id in fish_ids:
                    db.session.add(WaterbodyFish(waterbody_id=wb.id, fish_id=fish_id))

            db.session.commit()
            flash('Водоём обновлён', 'success')
        
        elif action == 'delete':
            wb_id = request.form.get('wb_id', type=int)
            wb = Waterbody.query.get_or_404(wb_id)

            # Удаление файла изображения
            if wb.cover_image:
                old_path = os.path.join(current_app.config['WATERBODY_IMAGES_FOLDER'], os.path.basename(wb.cover_image))
                if os.path.exists(old_path):
                    os.remove(old_path)

            db.session.delete(wb)
            db.session.commit()
            flash('Водоём удалён', 'success')
        
        return redirect(url_for('main.admin_waterbodies'))
    
    waterbodies = Waterbody.query.order_by(Waterbody.name.asc()).all()
    regions = Region.query.order_by(Region.name.asc()).all()
    return render_template('admin/waterbodies.html', waterbodies=waterbodies, regions=regions)

# --- админ: виды рыб ---
@main.route('/admin/fish', methods=['GET', 'POST'])
@admin_required
def admin_fish():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            name = request.form.get('name', '').strip()
            latin = request.form.get('latin_name', '').strip()
            tmin = request.form.get('optimal_temp_min', type=float)
            tmax = request.form.get('optimal_temp_max', type=float)
            seasonality = request.form.get('seasonality', '').strip()
            features = request.form.get('features', '').strip()
            description = request.form.get('description', '').strip()

            # Обработка загруженного изображения
            image_file = request.files.get('image')
            image_filename = ''
            if image_file and image_file.filename:
                ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    safe_name = secure_filename(image_file.filename.rsplit('.', 1)[0]) or 'image'
                    unique_name = f"{uuid.uuid4().hex}_{safe_name}.{ext}"
                    save_path = os.path.join(current_app.config['FISH_IMAGES_FOLDER'], unique_name)
                    image_file.save(save_path)
                    image_filename = f"uploads/fish/{unique_name}"

            if name:
                fish = FishSpecies(
                    name=name, latin_name=latin,
                    optimal_temp_min=tmin or 10.0, optimal_temp_max=tmax or 22.0,
                    seasonality=seasonality or 'Не указана',
                    features=features or 'Особенности не указаны',
                    description=description or 'Описание отсутствует',
                    image=image_filename
                )
                db.session.add(fish)
                db.session.commit()
                flash('Вид рыбы создан', 'success')
            else:
                flash('Введите название вида рыбы', 'danger')
        
        elif action == 'edit':
            fish_id = request.form.get('fish_id', type=int)
            fish = FishSpecies.query.get_or_404(fish_id)

            if request.form.get('name', '').strip():
                fish.name = request.form.get('name', '').strip()
            if request.form.get('latin_name', '').strip():
                fish.latin_name = request.form.get('latin_name', '').strip()

            tmin = request.form.get('optimal_temp_min', type=float)
            if tmin is not None:
                fish.optimal_temp_min = tmin
            tmax = request.form.get('optimal_temp_max', type=float)
            if tmax is not None:
                fish.optimal_temp_max = tmax

            if request.form.get('seasonality', '').strip():
                fish.seasonality = request.form.get('seasonality', '').strip()
            if request.form.get('features', '').strip():
                fish.features = request.form.get('features', '').strip()
            if request.form.get('description', '').strip():
                fish.description = request.form.get('description', '').strip()

            # Обработка загруженного изображения
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    safe_name = secure_filename(image_file.filename.rsplit('.', 1)[0]) or 'image'
                    unique_name = f"{uuid.uuid4().hex}_{safe_name}.{ext}"
                    save_path = os.path.join(current_app.config['FISH_IMAGES_FOLDER'], unique_name)
                    image_file.save(save_path)
                    new_image_filename = f"uploads/fish/{unique_name}"

                    # Удаление старого файла
                    if fish.image:
                        old_path = os.path.join(current_app.config['FISH_IMAGES_FOLDER'], os.path.basename(fish.image))
                        if os.path.exists(old_path):
                            os.remove(old_path)

                    fish.image = new_image_filename

            db.session.commit()
            flash('Вид рыбы обновлён', 'success')
        
        elif action == 'delete':
            fish_id = request.form.get('fish_id', type=int)
            fish = FishSpecies.query.get_or_404(fish_id)

            # Удаление файла изображения
            if fish.image:
                old_path = os.path.join(current_app.config['FISH_IMAGES_FOLDER'], os.path.basename(fish.image))
                if os.path.exists(old_path):
                    os.remove(old_path)

            db.session.delete(fish)
            db.session.commit()
            flash('Вид рыбы удалён', 'success')
        
        return redirect(url_for('main.admin_fish'))
    
    fish_list = FishSpecies.query.order_by(FishSpecies.name.asc()).all()
    return render_template('admin/fish.html', fish_list=fish_list)

# --- админ: снасти (ИСПРАВЛЕНА ОБРАБОТКА ИЗОБРАЖЕНИЯ ПРИ СОЗДАНИИ) ---
@main.route('/admin/gear', methods=['GET', 'POST'])
@admin_required
def admin_gear():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            name = request.form.get('name', '').strip()
            category = request.form.get('category', '').strip()
            description = request.form.get('description', '').strip()
            
            # Обработка загруженного изображения
            image_file = request.files.get('image')
            image_filename = ''
            if image_file and image_file.filename:
                ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    safe_name = secure_filename(image_file.filename.rsplit('.', 1)[0]) or 'image'
                    unique_name = f"{uuid.uuid4().hex}_{safe_name}.{ext}"
                    save_path = os.path.join(current_app.config['GEAR_IMAGES_FOLDER'], unique_name)
                    image_file.save(save_path)
                    image_filename = f"uploads/gear/{unique_name}"

            if name:
                gear = Gear(
                    name=name,
                    category=category or None,
                    description=description or None,
                    image=image_filename
                )
                db.session.add(gear)
                db.session.commit()
                flash('Снасть создана', 'success')
            else:
                flash('Введите название снасти', 'danger')
        
        elif action == 'edit':
            gear_id = request.form.get('gear_id', type=int)
            gear = Gear.query.get_or_404(gear_id)

            if request.form.get('name', '').strip():
                gear.name = request.form.get('name', '').strip()
            if request.form.get('category', '').strip():
                gear.category = request.form.get('category', '').strip()
            if request.form.get('description', '').strip():
                gear.description = request.form.get('description', '').strip()

            # Обработка загруженного изображения
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    safe_name = secure_filename(image_file.filename.rsplit('.', 1)[0]) or 'image'
                    unique_name = f"{uuid.uuid4().hex}_{safe_name}.{ext}"
                    save_path = os.path.join(current_app.config['GEAR_IMAGES_FOLDER'], unique_name)
                    image_file.save(save_path)
                    new_image_filename = f"uploads/gear/{unique_name}"

                    # Удаление старого файла
                    if gear.image:
                        old_path = os.path.join(current_app.config['GEAR_IMAGES_FOLDER'], os.path.basename(gear.image))
                        if os.path.exists(old_path):
                            os.remove(old_path)

                    gear.image = new_image_filename

            db.session.commit()
            flash('Снасть обновлена', 'success')
        
        elif action == 'delete':
            gear_id = request.form.get('gear_id', type=int)
            gear = Gear.query.get_or_404(gear_id)

            # Удаление файла изображения
            if gear.image:
                old_path = os.path.join(current_app.config['GEAR_IMAGES_FOLDER'], os.path.basename(gear.image))
                if os.path.exists(old_path):
                    os.remove(old_path)

            db.session.delete(gear)
            db.session.commit()
            flash('Снасть удалена', 'success')
        
        return redirect(url_for('main.admin_gear'))
    
    gears = Gear.query.order_by(Gear.name.asc()).all()
    return render_template('admin/gear.html', gears=gears)

# --- админ: наживки ---
@main.route('/admin/bait', methods=['GET', 'POST'])
@admin_required
def admin_bait():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'create':
            name = request.form.get('name', '').strip()
            category = request.form.get('category', '').strip()
            description = request.form.get('description', '').strip()
            # Обработка загруженного изображения
            image_file = request.files.get('image')
            image_filename = ''
            if image_file and image_file.filename:
                ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    safe_name = secure_filename(image_file.filename.rsplit('.', 1)[0]) or 'image'
                    unique_name = f"{uuid.uuid4().hex}_{safe_name}.{ext}"
                    save_path = os.path.join(current_app.config['BAIT_IMAGES_FOLDER'], unique_name)
                    image_file.save(save_path)
                    image_filename = f"uploads/bait/{unique_name}"
            
            if name:
                bait = Bait(
                    name=name,
                    category=category or None,
                    description=description or None,
                    image=image_filename
                )
                db.session.add(bait)
                db.session.commit()
                flash('Наживка создана', 'success')
            else:
                flash('Введите название наживки', 'danger')
        
        elif action == 'edit':
            bait_id = request.form.get('bait_id', type=int)
            bait = Bait.query.get_or_404(bait_id)

            if request.form.get('name', '').strip():
                bait.name = request.form.get('name', '').strip()
            if request.form.get('category', '').strip():
                bait.category = request.form.get('category', '').strip()
            if request.form.get('description', '').strip():
                bait.description = request.form.get('description', '').strip()

            # Обработка загруженного изображения
            image_file = request.files.get('image')
            if image_file and image_file.filename:
                ext = image_file.filename.rsplit('.', 1)[1].lower() if '.' in image_file.filename else ''
                if ext in current_app.config['ALLOWED_EXTENSIONS']:
                    safe_name = secure_filename(image_file.filename.rsplit('.', 1)[0]) or 'image'
                    unique_name = f"{uuid.uuid4().hex}_{safe_name}.{ext}"
                    save_path = os.path.join(current_app.config['BAIT_IMAGES_FOLDER'], unique_name)
                    image_file.save(save_path)
                    new_image_filename = f"uploads/bait/{unique_name}"

                    # Удаление старого файла
                    if bait.image:
                        old_path = os.path.join(current_app.config['BAIT_IMAGES_FOLDER'], os.path.basename(bait.image))
                        if os.path.exists(old_path):
                            os.remove(old_path)

                    bait.image = new_image_filename

            db.session.commit()
            flash('Наживка обновлена', 'success')
        
        elif action == 'delete':
            bait_id = request.form.get('bait_id', type=int)
            bait = Bait.query.get_or_404(bait_id)

            # Удаление файла изображения
            if bait.image:
                old_path = os.path.join(current_app.config['BAIT_IMAGES_FOLDER'], os.path.basename(bait.image))
                if os.path.exists(old_path):
                    os.remove(old_path)

            db.session.delete(bait)
            db.session.commit()
            flash('Наживка удалена', 'success')
        
        return redirect(url_for('main.admin_bait'))
    
    baits = Bait.query.order_by(Bait.name.asc()).all()
    return render_template('admin/bait.html', baits=baits)

# --- админ: отчёты (с удалением файлов) ---
@main.route('/admin/reports', methods=['GET', 'POST'])
@admin_required
def admin_reports():
    if request.method == 'POST':
        action = request.form.get('action')
        report_id = request.form.get('report_id', type=int)

        if action == 'delete' and report_id:
            report = FishingReport.query.get_or_404(report_id)
            import os
            for img in report.images:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], img.filename)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        current_app.logger.error(f"Failed to delete image {file_path}: {str(e)}")
            wb_id = report.waterbody_id
            db.session.delete(report)
            db.session.commit()
            update_waterbody_stats(wb_id)
            flash('Отчёт удалён', 'success')
        elif action == 'toggle_approval' and report_id:
            report = FishingReport.query.get_or_404(report_id)
            if report.status == 'approved':
                report.status = 'pending'
                report.rejection_reason = None
            else:
                report.status = 'approved'
                report.moderated_at = datetime.utcnow()
                report.moderated_by = current_user.id
            db.session.commit()
            update_waterbody_stats(report.waterbody_id)
            status = 'одобрен' if report.status == 'approved' else 'возвращён на модерацию'
            flash(f'Отчёт {status}', 'success')
        return redirect(url_for('main.admin_reports'))

    reports = FishingReport.query.order_by(FishingReport.date.desc()).limit(100).all()
    return render_template('admin/reports.html', reports=reports)

# --- админ: правила (ЕДИНАЯ ФОРМА) ---
@main.route('/admin/rules', methods=['GET', 'POST'])
@admin_required
def admin_rules():
    from .models import RegionalFishingRule, SeasonalBan, RestrictedArea, DailyLimit, FishSpecies

    if request.method == 'POST':
        action = request.form.get('action')
        rule_id = request.form.get('rule_id', type=int)
        rule_type = request.form.get('rule_type', 'general')

        # Вспомогательная функция для преобразования JSON-строки снастей в строку с запятыми
        def parse_gear_field(value):
            if not value:
                return None
            if value.startswith('['):
                try:
                    items = json.loads(value)
                    if isinstance(items, list):
                        return ', '.join(items)
                except:
                    pass
            return value

        if action == 'create':
            if rule_type == 'general':
                region_id = request.form.get('region_id', type=int)
                ban_start_str = request.form.get('ban_start', '').strip()
                ban_end_str = request.form.get('ban_end', '').strip()
                daily_limit_kg = request.form.get('daily_limit_kg', type=float)
                allowed_gear = parse_gear_field(request.form.get('allowed_gear', '').strip())
                prohibited_gear = parse_gear_field(request.form.get('prohibited_gear', '').strip())
                source = request.form.get('source', '').strip()

                if region_id:
                    ban_start = date.fromisoformat(ban_start_str) if ban_start_str else None
                    ban_end = date.fromisoformat(ban_end_str) if ban_end_str else None
                    rule = FishingRule(
                        region_id=region_id, ban_start=ban_start, ban_end=ban_end,
                        daily_limit_kg=daily_limit_kg,
                        allowed_gear=allowed_gear,
                        prohibited_gear=prohibited_gear,
                        source=source or 'Приказ Минсельхоза РФ'
                    )
                    db.session.add(rule)
                    db.session.commit()
                    flash('Общее правило добавлено', 'success')
                else:
                    flash('Выберите регион', 'danger')

            elif rule_type == 'regional':
                region_id = request.form.get('region_id', type=int)
                fish_id = request.form.get('fish_id', type=int)
                ban_start_str = request.form.get('ban_start', '').strip()
                ban_end_str = request.form.get('ban_end', '').strip()
                min_size_cm = request.form.get('min_size_cm', type=int)
                daily_limit_kg = request.form.get('daily_limit_kg', type=float)
                daily_limit_pcs = request.form.get('daily_limit_pcs', type=int)
                allowed_gear = parse_gear_field(request.form.get('allowed_gear', '').strip())
                prohibited_gear = parse_gear_field(request.form.get('prohibited_gear', '').strip())
                is_prohibited = request.form.get('is_prohibited') == 'on'

                if region_id and fish_id:
                    ban_start = date.fromisoformat(ban_start_str) if ban_start_str else None
                    ban_end = date.fromisoformat(ban_end_str) if ban_end_str else None
                    rule = RegionalFishingRule(
                        region_id=region_id, fish_id=fish_id,
                        ban_start=ban_start, ban_end=ban_end,
                        min_size_cm=min_size_cm,
                        daily_limit_kg=daily_limit_kg,
                        daily_limit_pcs=daily_limit_pcs,
                        allowed_gear=allowed_gear,
                        prohibited_gear=prohibited_gear,
                        is_prohibited=is_prohibited
                    )
                    db.session.add(rule)
                    db.session.commit()
                    flash('Региональное правило добавлено', 'success')
                else:
                    flash('Выберите регион и вид рыбы', 'danger')

            elif rule_type == 'seasonal':
                region_id = request.form.get('region_id', type=int)
                ban_start_str = request.form.get('ban_start', '').strip()
                ban_end_str = request.form.get('ban_end', '').strip()
                description = request.form.get('description', '').strip()

                if region_id and ban_start_str and ban_end_str:
                    ban_start = date.fromisoformat(ban_start_str)
                    ban_end = date.fromisoformat(ban_end_str)
                    rule = SeasonalBan(
                        region_id=region_id,
                        ban_start=ban_start, ban_end=ban_end,
                        description=description or None
                    )
                    db.session.add(rule)
                    db.session.commit()
                    flash('Сезонный запрет добавлен', 'success')
                else:
                    flash('Заполните все обязательные поля', 'danger')

            elif rule_type == 'restricted':
                name = request.form.get('name', '').strip()
                area_type = request.form.get('area_type', '').strip()
                region_id = request.form.get('region_id', type=int)
                geometry_geojson = request.form.get('geometry_geojson', '').strip()
                restriction_start_str = request.form.get('restriction_start', '').strip()
                restriction_end_str = request.form.get('restriction_end', '').strip()

                if name and restriction_start_str and restriction_end_str:
                    restriction_start = date.fromisoformat(restriction_start_str)
                    restriction_end = date.fromisoformat(restriction_end_str)
                    rule = RestrictedArea(
                        name=name, area_type=area_type or None,
                        region_id=region_id,
                        geometry_geojson=geometry_geojson or None,
                        restriction_start=restriction_start,
                        restriction_end=restriction_end
                    )
                    db.session.add(rule)
                    db.session.commit()
                    flash('Запретная зона добавлена', 'success')
                else:
                    flash('Заполните все обязательные поля', 'danger')

            elif rule_type == 'daily_limit':
                rule_id_parent = request.form.get('rule_id', type=int)
                fish_id = request.form.get('fish_id', type=int)
                limit_kg = request.form.get('limit_kg', type=float)
                limit_pcs = request.form.get('limit_pcs', type=int)
                min_size_cm = request.form.get('min_size_cm', type=int)
                is_prohibited = request.form.get('is_prohibited') == 'on'

                if rule_id_parent and fish_id:
                    rule = DailyLimit(
                        rule_id=rule_id_parent, fish_id=fish_id,
                        limit_kg=limit_kg,
                        limit_pcs=limit_pcs,
                        min_size_cm=min_size_cm,
                        is_prohibited=is_prohibited
                    )
                    db.session.add(rule)
                    db.session.commit()
                    flash('Суточный лимит добавлен', 'success')
                else:
                    flash('Выберите правило и вид рыбы', 'danger')

        elif action == 'edit' and rule_id:
            if rule_type == 'general':
                rule = FishingRule.query.get_or_404(rule_id)

                region_id = request.form.get('region_id', type=int)
                if region_id:
                    rule.region_id = region_id

                ban_start_str = request.form.get('ban_start', '').strip()
                if ban_start_str:
                    rule.ban_start = date.fromisoformat(ban_start_str)
                else:
                    rule.ban_start = None

                ban_end_str = request.form.get('ban_end', '').strip()
                if ban_end_str:
                    rule.ban_end = date.fromisoformat(ban_end_str)
                else:
                    rule.ban_end = None

                daily_limit_kg = request.form.get('daily_limit_kg', type=float)
                if daily_limit_kg is not None:
                    rule.daily_limit_kg = daily_limit_kg

                allowed_gear = parse_gear_field(request.form.get('allowed_gear', '').strip())
                if allowed_gear is not None:
                    rule.allowed_gear = allowed_gear

                prohibited_gear = parse_gear_field(request.form.get('prohibited_gear', '').strip())
                if prohibited_gear is not None:
                    rule.prohibited_gear = prohibited_gear

                source = request.form.get('source', '').strip()
                if source:
                    rule.source = source

                db.session.commit()
                flash('Общее правило обновлено', 'success')

            elif rule_type == 'regional':
                rule = RegionalFishingRule.query.get_or_404(rule_id)

                region_id = request.form.get('region_id', type=int)
                if region_id:
                    rule.region_id = region_id

                fish_id = request.form.get('fish_id', type=int)
                if fish_id:
                    rule.fish_id = fish_id

                ban_start_str = request.form.get('ban_start', '').strip()
                if ban_start_str:
                    rule.ban_start = date.fromisoformat(ban_start_str)
                else:
                    rule.ban_start = None

                ban_end_str = request.form.get('ban_end', '').strip()
                if ban_end_str:
                    rule.ban_end = date.fromisoformat(ban_end_str)
                else:
                    rule.ban_end = None

                min_size_cm = request.form.get('min_size_cm', type=int)
                if min_size_cm is not None:
                    rule.min_size_cm = min_size_cm

                daily_limit_kg = request.form.get('daily_limit_kg', type=float)
                if daily_limit_kg is not None:
                    rule.daily_limit_kg = daily_limit_kg

                daily_limit_pcs = request.form.get('daily_limit_pcs', type=int)
                if daily_limit_pcs is not None:
                    rule.daily_limit_pcs = daily_limit_pcs

                allowed_gear = parse_gear_field(request.form.get('allowed_gear', '').strip())
                if allowed_gear is not None:
                    rule.allowed_gear = allowed_gear

                prohibited_gear = parse_gear_field(request.form.get('prohibited_gear', '').strip())
                if prohibited_gear is not None:
                    rule.prohibited_gear = prohibited_gear

                is_prohibited = request.form.get('is_prohibited') == 'on'
                rule.is_prohibited = is_prohibited

                db.session.commit()
                flash('Региональное правило обновлено', 'success')

            elif rule_type == 'seasonal':
                rule = SeasonalBan.query.get_or_404(rule_id)

                region_id = request.form.get('region_id', type=int)
                if region_id:
                    rule.region_id = region_id

                ban_start_str = request.form.get('ban_start', '').strip()
                if ban_start_str:
                    rule.ban_start = date.fromisoformat(ban_start_str)

                ban_end_str = request.form.get('ban_end', '').strip()
                if ban_end_str:
                    rule.ban_end = date.fromisoformat(ban_end_str)

                description = request.form.get('description', '').strip()
                if description:
                    rule.description = description

                db.session.commit()
                flash('Сезонный запрет обновлен', 'success')

            elif rule_type == 'restricted':
                rule = RestrictedArea.query.get_or_404(rule_id)

                name = request.form.get('name', '').strip()
                if name:
                    rule.name = name

                area_type = request.form.get('area_type', '').strip()
                if area_type:
                    rule.area_type = area_type

                region_id = request.form.get('region_id', type=int)
                if region_id:
                    rule.region_id = region_id

                geometry_geojson = request.form.get('geometry_geojson', '').strip()
                if geometry_geojson:
                    rule.geometry_geojson = geometry_geojson

                restriction_start_str = request.form.get('restriction_start', '').strip()
                if restriction_start_str:
                    rule.restriction_start = date.fromisoformat(restriction_start_str)

                restriction_end_str = request.form.get('restriction_end', '').strip()
                if restriction_end_str:
                    rule.restriction_end = date.fromisoformat(restriction_end_str)

                db.session.commit()
                flash('Запретная зона обновлена', 'success')

            elif rule_type == 'daily_limit':
                rule = DailyLimit.query.get_or_404(rule_id)

                rule_id_parent = request.form.get('rule_id', type=int)
                if rule_id_parent:
                    rule.rule_id = rule_id_parent

                fish_id = request.form.get('fish_id', type=int)
                if fish_id:
                    rule.fish_id = fish_id

                limit_kg = request.form.get('limit_kg', type=float)
                if limit_kg is not None:
                    rule.limit_kg = limit_kg

                limit_pcs = request.form.get('limit_pcs', type=int)
                if limit_pcs is not None:
                    rule.limit_pcs = limit_pcs

                min_size_cm = request.form.get('min_size_cm', type=int)
                if min_size_cm is not None:
                    rule.min_size_cm = min_size_cm

                is_prohibited = request.form.get('is_prohibited') == 'on'
                rule.is_prohibited = is_prohibited

                db.session.commit()
                flash('Суточный лимит обновлен', 'success')

        elif action == 'delete' and rule_id:
            if rule_type == 'general':
                rule = FishingRule.query.get_or_404(rule_id)
            elif rule_type == 'regional':
                rule = RegionalFishingRule.query.get_or_404(rule_id)
            elif rule_type == 'seasonal':
                rule = SeasonalBan.query.get_or_404(rule_id)
            elif rule_type == 'restricted':
                rule = RestrictedArea.query.get_or_404(rule_id)
            elif rule_type == 'daily_limit':
                rule = DailyLimit.query.get_or_404(rule_id)
            else:
                flash('Неизвестный тип правила', 'danger')
                return redirect(url_for('main.admin_rules'))

            db.session.delete(rule)
            db.session.commit()
            flash('Правило удалено', 'success')

        return redirect(url_for('main.admin_rules'))

    # Получение всех правил разных типов
    general_rules = FishingRule.query.order_by(FishingRule.region_id.asc()).all()
    regional_rules = RegionalFishingRule.query.order_by(RegionalFishingRule.region_id.asc()).all()
    seasonal_bans = SeasonalBan.query.order_by(SeasonalBan.region_id.asc()).all()
    restricted_areas = RestrictedArea.query.order_by(RestrictedArea.name.asc()).all()
    daily_limits = DailyLimit.query.order_by(DailyLimit.rule_id.asc()).all()

    regions = Region.query.order_by(Region.name.asc()).all()
    fish_species = FishSpecies.query.order_by(FishSpecies.name.asc()).all()
    all_gears = Gear.query.order_by(Gear.name).all()

    return render_template('admin/rules.html',
                         general_rules=general_rules,
                         regional_rules=regional_rules,
                         seasonal_bans=seasonal_bans,
                         restricted_areas=restricted_areas,
                         daily_limits=daily_limits,
                         regions=regions,
                         fish_species=fish_species,
                         all_gears=all_gears)
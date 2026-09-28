# app/utils.py
# Основные утилиты для работы с данными

from .models import (
    Region, Waterbody, FishSpecies, WaterbodyFish,
    FishingRule, User, FishingReport, Gear, Bait,
    FishGear, FishBait, RegionalFishingRule, SeasonalBan, RestrictedArea
)
from . import db
from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash
import json
import os
import requests
from shapely.geometry import shape, Point

from .models import WeatherCache
import random

def seed_data():
    """Основная функция для заполнения базы данных демо-данными"""
    if Region.query.first():
        print("База данных уже заполнена, пропускаем seed_data()")
        return

    print("Начинаем заполнение базы данных...")

    # ================================================================
    #  1. РЕГИОНЫ
    # ================================================================
    from .data.regions import regions_data
    region_by_code = {}

    for name, basin, code in regions_data:
        r = Region(name=name, basin=basin, code=code)
        db.session.add(r)
        region_by_code[code] = r

    db.session.commit()
    print(f'Добавлено {len(regions_data)} регионов')

    # ================================================================
    #  2. ВИДЫ РЫБ
    # ================================================================
    from .data.fish import fish_data
    fish_objs = []

    for idx, (name, latin, icon, tmin, tmax, season, features, desc) in enumerate(fish_data):
        f = FishSpecies(
            name=name, latin_name=latin,
            optimal_temp_min=tmin, optimal_temp_max=tmax,
            seasonality=season, features=features, description=desc,
            image=f"https://images.pexels.com/photos/683099{idx+1}/pexels-photo-683099{idx+1}.jpeg?auto=compress&cs=tinysrgb&w=600"
        )
        db.session.add(f)
        fish_objs.append(f)

    db.session.commit()
    print(f'Добавлено {len(fish_objs)} видов рыб')

    # ================================================================
    #  3. СНАСТИ
    # ================================================================
    from .data.gear import gear_data
    gear_objs = []

    for name, desc, cat in gear_data:
        g = Gear(name=name, description=desc, category=cat, image="")
        db.session.add(g)
        gear_objs.append(g)

    db.session.commit()
    print(f'Добавлено {len(gear_objs)} снастей')

    # ================================================================
    #  4. НАЖИВКИ
    # ================================================================
    from .data.bait import bait_data
    bait_objs = []

    for name, desc, cat in bait_data:
        b = Bait(name=name, description=desc, category=cat, image="")
        db.session.add(b)
        bait_objs.append(b)

    db.session.commit()
    print(f'Добавлено {len(bait_objs)} наживок')

    # ================================================================
    #  5. ВОДОЁМЫ
    # ================================================================
    from .data.waterbodies import waterbodies_data
    waterbodies_list = []

    for name, wb_type, rcode, lat, lon, area, desc in waterbodies_data:
        r = region_by_code.get(rcode)
        if r:
            wb = Waterbody(
                name=name, type=wb_type, region_id=r.id,
                latitude=lat, longitude=lon, area=area,
                description=desc,
                access_info="Подъезд возможен | Береговая ловля | Места для палаток | Лодки напрокат",
                infrastructure="Парковка | Место для костра | Магазин рядом | Мусорные баки",
                rating=0.0, reports_count=0,
            )
            db.session.add(wb)
            waterbodies_list.append(wb)

    db.session.commit()
    waterbodies_list = Waterbody.query.all()
    print(f'Добавлено {len(waterbodies_list)} водоёмов')

    # ================================================================
    #  6. СВЯЗИ
    # ================================================================
    from .data.relations import (
        create_fish_gear_relations,
        create_fish_bait_relations,
        create_waterbody_fish_relations
    )

    create_fish_gear_relations(fish_objs, gear_objs, db)
    create_fish_bait_relations(fish_objs, bait_objs, db)
    create_waterbody_fish_relations(waterbodies_list, fish_objs, db)

    # ================================================================
    #  7. ПОЛЬЗОВАТЕЛИ
    # ================================================================
    from .data.users import create_users
    create_users(db)

    # ================================================================
    #  8. ОТЧЁТЫ
    # ================================================================
    from .data.reports import create_demo_reports
    create_demo_reports(db)

    # ================================================================
    #  9. ПРАВИЛА РЫБОЛОВСТВА (НОВЫЕ МОДЕЛИ)
    # ================================================================
    create_fishing_rules(region_by_code)

    # ================================================================
    # 10. ПЕРЕСЧЁТ РЕЙТИНГОВ ВОДОЁМОВ (ИСПРАВЛЕНИЕ)
    # ================================================================
    print("Пересчитываем рейтинги водоёмов...")
    waterbodies = Waterbody.query.all()
    for wb in waterbodies:
        update_waterbody_stats(wb.id)
    print("Рейтинги водоёмов обновлены.")

    print("Заполнение базы данных завершено!")
    print(f"Статистика: {len(regions_data)} регионов, {len(fish_objs)} видов рыб, "
          f"{len(gear_objs)} снастей, {len(bait_objs)} наживок, {len(waterbodies_list)} водоёмов")


def create_fishing_rules(region_by_code):
    """Создаёт правила рыболовства для новых моделей"""
    from .models import RegionalFishingRule, SeasonalBan, RestrictedArea

    for r in region_by_code.values():
        if r.basin == "Балтийский":
            ban_start, ban_end, limit = date(2026, 4, 20), date(2026, 6, 10), 5.0
        elif r.basin == "Азово-Черноморский":
            ban_start, ban_end, limit = date(2026, 4, 1), date(2026, 5, 31), 5.0
        elif r.basin == "Ангаро-Енисейский":
            ban_start, ban_end, limit = date(2026, 4, 25), date(2026, 6, 15), 5.0
        elif r.basin == "Дальневосточный":
            ban_start, ban_end, limit = date(2026, 5, 15), date(2026, 7, 1), 10.0
        elif r.basin == "Северный":
            ban_start, ban_end, limit = date(2026, 5, 20), date(2026, 6, 30), 5.0
        elif r.basin == "Обь-Иртышский":
            ban_start, ban_end, limit = date(2026, 5, 1), date(2026, 6, 15), 5.0
        elif r.basin == "Волжско-Каспийский":
            ban_start, ban_end, limit = date(2026, 4, 15), date(2026, 6, 10), 10.0
        else:
            ban_start, ban_end, limit = date(2026, 4, 15), date(2026, 6, 10), 5.0

        main_fish = ["Щука", "Окунь", "Судак", "Лещ", "Плотва"]
        for fish_name in main_fish:
            fish = FishSpecies.query.filter_by(name=fish_name).first()
            if fish:
                rule = RegionalFishingRule(
                    region_id=r.id,
                    fish_id=fish.id,
                    ban_start=ban_start,
                    ban_end=ban_end,
                    min_size_cm=random.choice([25, 30, 35, 40, 0]) if fish_name != "Плотва" else 0,
                    daily_limit_kg=limit,
                    daily_limit_pcs=random.choice([5, 10, 15, 0]),
                    allowed_gear=json.dumps(["спиннинг", "фидер", "поплавочная удочка", "донка"]),
                    prohibited_gear=json.dumps(["сети", "электроудочки", "остроги"]),
                    is_prohibited=False
                )
                db.session.add(rule)

        seasonal_ban = SeasonalBan(
            region_id=r.id,
            ban_start=ban_start,
            ban_end=ban_end,
            description=f"Нерестовый запрет для {r.basin} бассейна"
        )
        db.session.add(seasonal_ban)

    db.session.commit()
    print(f'Добавлены региональные правила рыболовства')


def is_point_in_restricted_area(lat, lon, date):
    """Проверяет, находится ли точка в запретной зоне"""
    from .models import RestrictedArea
    import json

    point = Point(lon, lat)

    restricted_areas = RestrictedArea.query.filter(
        RestrictedArea.restriction_start <= date,
        RestrictedArea.restriction_end >= date
    ).all()

    for area in restricted_areas:
        if area.geometry_geojson:
            try:
                geom = shape(json.loads(area.geometry_geojson))
                if geom.contains(point):
                    return True
            except:
                continue
    return False


def check_fishing_restrictions(waterbody, report_date, fish_caught):
    """
    Проверяет соблюдение правил рыболовства для отчёта
    Возвращает tuple: (is_valid, warnings, errors)
    """
    from .models import RegionalFishingRule, SeasonalBan
    warnings = []
    errors = []

    seasonal_bans = SeasonalBan.query.filter_by(region_id=waterbody.region_id).all()
    is_banned_period = False

    for ban in seasonal_bans:
        if ban.ban_start <= report_date <= ban.ban_end:
            is_banned_period = True
            errors.append(f"Нерестовый запрет: с {ban.ban_start.strftime('%d.%m')} по {ban.ban_end.strftime('%d.%m')}")
            break

    if is_banned_period:
        return False, warnings, errors

    for fish_item in fish_caught:
        fish_name = fish_item.get('name', '')
        fish = FishSpecies.query.filter_by(name=fish_name).first()
        if not fish:
            continue

        regional_rules = RegionalFishingRule.query.filter_by(
            region_id=waterbody.region_id,
            fish_id=fish.id
        ).first()

        if regional_rules:
            if regional_rules.is_prohibited:
                errors.append(f"Вылов {fish_name} запрещён в этом регионе")
                continue

            if regional_rules.min_size_cm and regional_rules.min_size_cm > 0:
                warnings.append(f"Для {fish_name} установлен минимальный размер {regional_rules.min_size_cm} см")

            if regional_rules.daily_limit_kg:
                fish_weight = fish_item.get('kg', 0)
                if fish_weight > regional_rules.daily_limit_kg:
                    errors.append(f"Превышен суточный лимит для {fish_name}: {regional_rules.daily_limit_kg} кг")

            if regional_rules.daily_limit_pcs and regional_rules.daily_limit_pcs > 0:
                fish_count = fish_item.get('pcs', 0)
                if fish_count > regional_rules.daily_limit_pcs:
                    errors.append(f"Превышен суточный лимит для {fish_name}: {regional_rules.daily_limit_pcs} шт")

    return len(errors) == 0, warnings, errors


def update_waterbody_stats(waterbody_id):
    """Обновляет статистику водоёма (рейтинг, количество отчётов)"""
    from .models import Waterbody, FishingReport
    wb = Waterbody.query.get(waterbody_id)
    if not wb:
        return

    wb.reports_count = FishingReport.query.filter_by(waterbody_id=waterbody_id, status='approved').count()
    reports_with_rating = FishingReport.query.filter_by(waterbody_id=waterbody_id, status='approved').filter(FishingReport.rating.isnot(None)).all()

    if reports_with_rating:
        wb.rating = round(sum(r.rating for r in reports_with_rating) / len(reports_with_rating), 1)
    else:
        wb.rating = 0.0

    db.session.commit()


def get_cached_weather_for_waterbody(waterbody, force_refresh=False):
    """Получает текущую погоду для водоёма (с кэшированием)"""
    if not waterbody or waterbody.latitude is None or waterbody.longitude is None:
        return WeatherCache.query.filter_by(waterbody_id=getattr(waterbody, "id", None)).order_by(WeatherCache.fetched_at.desc()).first()

    now = datetime.utcnow()
    fresh_after = now - timedelta(hours=3)

    if not force_refresh:
        cached = WeatherCache.query.filter(
            WeatherCache.waterbody_id == waterbody.id,
            WeatherCache.fetched_at >= fresh_after
        ).order_by(WeatherCache.fetched_at.desc()).first()
        if cached:
            return cached

    try:
        WeatherCache.query.filter_by(waterbody_id=waterbody.id).delete()

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": waterbody.latitude,
            "longitude": waterbody.longitude,
            "current": "temperature_2m,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m,weather_code",
            "timezone": "Europe/Moscow"
        }

        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        current = data.get("current", {})
        temp = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        pressure_mmhg = float(current.get("pressure_msl")) * 0.750062 if current.get("pressure_msl") else None
        wind_speed = current.get("wind_speed_10m")
        wind_direction = current.get("wind_direction_10m")
        weather_code = current.get("weather_code", 0)

        wmo_codes = {
            0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность", 3: "Пасмурно",
            45: "Туман", 48: "Туман с изморозью", 51: "Слабая морось", 53: "Морось",
            55: "Сильная морось", 61: "Небольшой дождь", 63: "Дождь", 65: "Сильный дождь",
            71: "Небольшой снег", 73: "Снег", 75: "Сильный снег", 80: "Небольшой ливень",
            81: "Ливень", 82: "Сильный ливень", 95: "Гроза",
        }
        weather_desc = wmo_codes.get(weather_code, f"Код погоды: {weather_code}")

        w = WeatherCache(
            waterbody_id=waterbody.id,
            temperature=temp,
            pressure=pressure_mmhg,
            humidity=humidity,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            weather_desc=weather_desc,
            fetched_at=now
        )
        db.session.add(w)
        db.session.commit()
        return w

    except Exception:
        db.session.rollback()
        return WeatherCache.query.filter_by(waterbody_id=waterbody.id).order_by(WeatherCache.fetched_at.desc()).first()


def get_forecast_weather_for_waterbody(waterbody, target_date, target_hour):
    """Получает прогноз погоды для водоёма на указанную дату и час"""
    if not waterbody or waterbody.latitude is None or waterbody.longitude is None:
        return None

    # Проверка кэша
    date_start = datetime(target_date.year, target_date.month, target_date.day, target_hour)
    date_end = date_start + timedelta(hours=1)
    cached = WeatherCache.query.filter(
        WeatherCache.waterbody_id == waterbody.id,
        WeatherCache.fetched_at >= date_start,
        WeatherCache.fetched_at < date_end
    ).order_by(WeatherCache.fetched_at.desc()).first()
    if cached:
        return cached

    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": waterbody.latitude,
            "longitude": waterbody.longitude,
            "hourly": "temperature_2m,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m,weather_code",
            "timezone": "Europe/Moscow",
            "forecast_days": 16
        }
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        if not times:
            return None

        # Формируем целевую строку
        target_str = f"{target_date.strftime('%Y-%m-%d')}T{target_hour:02d}:00"

        # 1. Точное совпадение
        idx = None
        for i, t in enumerate(times):
            if t == target_str:
                idx = i
                break

        # 2. Если нет – любой час в тот же день
        if idx is None:
            target_date_str = target_date.strftime('%Y-%m-%d')
            for i, t in enumerate(times):
                if t.startswith(target_date_str):
                    idx = i
                    break

        # 3. Если всё равно нет – берём первый час (аварийно)
        if idx is None:
            idx = 0

        # Извлечение данных
        temp = hourly.get("temperature_2m", [])[idx] if idx < len(hourly.get("temperature_2m", [])) else None
        humidity = hourly.get("relative_humidity_2m", [])[idx] if idx < len(hourly.get("relative_humidity_2m", [])) else None
        pressure_hpa = hourly.get("pressure_msl", [])[idx] if idx < len(hourly.get("pressure_msl", [])) else None
        wind_speed = hourly.get("wind_speed_10m", [])[idx] if idx < len(hourly.get("wind_speed_10m", [])) else None
        wind_direction = hourly.get("wind_direction_10m", [])[idx] if idx < len(hourly.get("wind_direction_10m", [])) else None
        weather_code = hourly.get("weather_code", [])[idx] if idx < len(hourly.get("weather_code", [])) else None

        pressure_mmhg = pressure_hpa * 0.750062 if pressure_hpa else None

        wmo_codes = {
            0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность", 3: "Пасмурно",
            45: "Туман", 48: "Туман с изморозью", 51: "Слабая морось", 53: "Морось",
            55: "Сильная морось", 61: "Небольшой дождь", 63: "Дождь", 65: "Сильный дождь",
            71: "Небольшой снег", 73: "Снег", 75: "Сильный снег", 80: "Небольшой ливень",
            81: "Ливень", 82: "Сильный ливень", 95: "Гроза",
        }
        weather_desc = wmo_codes.get(weather_code, f"Код погоды: {weather_code}")

        w = WeatherCache(
            waterbody_id=waterbody.id,
            temperature=round(temp, 1) if temp is not None else None,
            pressure=round(pressure_mmhg, 1) if pressure_mmhg is not None else None,
            humidity=humidity,
            wind_speed=round(wind_speed, 1) if wind_speed is not None else None,
            wind_direction=round(wind_direction, 1) if wind_direction is not None else None,
            weather_desc=weather_desc,
            fetched_at=datetime.utcnow()
        )
        db.session.add(w)
        db.session.commit()
        return w

    except Exception as e:
        print(f"Forecast weather error: {e}")
        db.session.rollback()
        return None


def get_historical_weather_for_waterbody(waterbody, target_date, target_hour=12):
    """Получает историческую погоду для водоёма на указанную дату"""
    if not waterbody or waterbody.latitude is None or waterbody.longitude is None:
        return None

    target_datetime = datetime(target_date.year, target_date.month, target_date.day, target_hour)
    date_start = target_datetime
    date_end = date_start + timedelta(hours=1)

    cached = WeatherCache.query.filter(
        WeatherCache.waterbody_id == waterbody.id,
        WeatherCache.fetched_at >= date_start,
        WeatherCache.fetched_at < date_end
    ).order_by(WeatherCache.fetched_at.desc()).first()

    if cached:
        return cached

    try:
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": waterbody.latitude,
            "longitude": waterbody.longitude,
            "start_date": target_date.strftime('%Y-%m-%d'),
            "end_date": target_date.strftime('%Y-%m-%d'),
            "hourly": "temperature_2m,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m,weather_code",
            "timezone": "Europe/Moscow"
        }

        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])

        if not times:
            return None

        target_str = target_datetime.strftime('%Y-%m-%dT%H:00')
        idx = None
        for i, t in enumerate(times):
            if t == target_str:
                idx = i
                break

        if idx is None:
            min_diff = float('inf')
            for i, t in enumerate(times):
                try:
                    time_parts = t.split('T')
                    if len(time_parts) == 2:
                        time_part = time_parts[1]
                        hour = int(time_part.split(':')[0])
                        time_diff = abs(hour - target_hour)
                        if time_diff < min_diff:
                            min_diff = time_diff
                            idx = i
                except (ValueError, IndexError):
                    continue
            if idx is None or min_diff > 3:
                return None

        temp = hourly.get("temperature_2m", [])[idx] if idx < len(hourly.get("temperature_2m", [])) else None
        humidity = hourly.get("relative_humidity_2m", [])[idx] if idx < len(hourly.get("relative_humidity_2m", [])) else None
        pressure_hpa = hourly.get("pressure_msl", [])[idx] if idx < len(hourly.get("pressure_msl", [])) else None
        wind_speed = hourly.get("wind_speed_10m", [])[idx] if idx < len(hourly.get("wind_speed_10m", [])) else None
        wind_direction = hourly.get("wind_direction_10m", [])[idx] if idx < len(hourly.get("wind_direction_10m", [])) else None
        weather_code = hourly.get("weather_code", [])[idx] if idx < len(hourly.get("weather_code", [])) else None

        pressure_mmhg = pressure_hpa * 0.750062 if pressure_hpa else None

        wmo_codes = {
            0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность", 3: "Пасмурно",
            45: "Туман", 48: "Туман с изморозью", 51: "Слабая морось", 53: "Морось",
            55: "Сильная морось", 61: "Небольшой дождь", 63: "Дождь", 65: "Сильный дождь",
            71: "Небольшой снег", 73: "Снег", 75: "Сильный снег", 80: "Небольшой ливень",
            81: "Ливень", 82: "Сильный ливень", 95: "Гроза",
        }
        weather_desc = wmo_codes.get(weather_code, f"Код погоды: {weather_code}")

        w = WeatherCache(
            waterbody_id=waterbody.id,
            temperature=round(temp, 1) if temp is not None else None,
            pressure=round(pressure_mmhg, 1) if pressure_mmhg is not None else None,
            humidity=humidity,
            wind_speed=round(wind_speed, 1) if wind_speed is not None else None,
            wind_direction=round(wind_direction, 1) if wind_direction is not None else None,
            weather_desc=weather_desc,
            fetched_at=datetime.utcnow()
        )
        db.session.add(w)
        db.session.commit()
        return w

    except Exception as e:
        print(f"Historical weather error for {waterbody.name} on {target_date}: {e}")
        db.session.rollback()
        return None
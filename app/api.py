from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from sqlalchemy import or_, case
import json

from . import db
from .models import (
    Waterbody, Region, FishSpecies, WaterbodyFish,
    Favorite, WeatherCache, FishingReport, Comment, Gear, Bait,
    RegionalFishingRule, SeasonalBan, FishingRule, RestrictedArea, DailyLimit
)
from .forecast import build_forecast_table_html
from .utils import (
    get_cached_weather_for_waterbody,
    get_historical_weather_for_waterbody,
    get_forecast_weather_for_waterbody,
    update_waterbody_stats
)

api = Blueprint('api', __name__)


@api.get('/waterbodies/search')
def waterbodies_search():
    q = (request.args.get('q') or '').strip()
    region = (request.args.get('region') or '').strip()
    fish = (request.args.get('fish') or '').strip()
    wb_type = (request.args.get('type') or '').strip()
    history = (request.args.get('history') or '').strip()

    query = Waterbody.query.join(Region, Waterbody.region_id == Region.id)

    if q:
        like = f"%{q}%"
        query = query.filter(or_(Waterbody.name.ilike(like), Region.name.ilike(like)))

    if region:
        try:
            query = query.filter(Waterbody.region_id == int(region))
        except ValueError:
            pass

    if wb_type:
        query = query.filter(Waterbody.type == wb_type)

    if fish:
        try:
            fish_id = int(fish)
            query = query.join(WaterbodyFish, WaterbodyFish.waterbody_id == Waterbody.id).filter(WaterbodyFish.fish_id == fish_id)
        except ValueError:
            fs = FishSpecies.query.filter(FishSpecies.name.ilike(f"%{fish}%")).first()
            if fs:
                query = query.join(WaterbodyFish, WaterbodyFish.waterbody_id == Waterbody.id).filter(WaterbodyFish.fish_id == fs.id)

    history_ids = []
    if history:
        try:
            history_ids = [int(x) for x in history.split(',') if x.strip().isdigit()]
        except (ValueError, TypeError):
            history_ids = []

    if history_ids:
        history_order = case(
            {wb_id: index for index, wb_id in enumerate(history_ids)},
            value=Waterbody.id,
            else_=999999
        )
        items = (
            query
            .order_by(history_order, Waterbody.reports_count.desc(), Waterbody.rating.desc())
            .limit(200)
            .all()
        )
    else:
        items = (
            query
            .order_by(Waterbody.reports_count.desc(), Waterbody.rating.desc())
            .limit(200)
            .all()
        )

    return jsonify({
        "items": [{
            "id": wb.id,
            "name": wb.name,
            "type": wb.type,
            "region_id": wb.region_id,
            "region_name": wb.region.name if wb.region else "",
            "latitude": wb.latitude,
            "longitude": wb.longitude,
            "rating": wb.rating,
            "reports_count": wb.reports_count,
        } for wb in items]
    })


@api.get('/waterbodies/history')
def waterbodies_history():
    ids_str = (request.args.get('ids') or '').strip()
    if not ids_str:
        return jsonify({"items": []})

    try:
        ids = [int(x) for x in ids_str.split(',') if x.strip().isdigit()]
    except (ValueError, TypeError):
        return jsonify({"items": []})

    if not ids:
        return jsonify({"items": []})

    items = Waterbody.query.filter(Waterbody.id.in_(ids)).all()
    items_dict = {wb.id: wb for wb in items}

    result = []
    for wb_id in ids:
        wb = items_dict.get(wb_id)
        if wb:
            result.append({
                "id": wb.id,
                "name": wb.name,
                "type": wb.type,
                "region_id": wb.region_id,
                "region_name": wb.region.name if wb.region else "",
                "latitude": wb.latitude,
                "longitude": wb.longitude,
                "rating": wb.rating,
                "reports_count": wb.reports_count,
            })

    return jsonify({"items": result})


@api.get('/waterbodies/<int:waterbody_id>/forecast')
def waterbody_forecast(waterbody_id: int):
    waterbody = Waterbody.query.get_or_404(waterbody_id)

    date_str = request.args.get('date', '').strip()
    time_of_day = request.args.get('time', 'morning').strip()
    gear_names_str = request.args.get('gears', '').strip()
    bait_names_str = request.args.get('baits', '').strip()

    gear_names = [g.strip() for g in gear_names_str.split(',') if g.strip()]
    bait_names = [b.strip() for b in bait_names_str.split(',') if b.strip()]

    target_date = None
    if date_str:
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            target_date = datetime.now().date()
    else:
        target_date = datetime.now().date()

    today = date.today()
    min_date = today - timedelta(days=7)
    max_date = today + timedelta(days=16)

    if target_date < min_date or target_date > max_date:
        return jsonify({
            "ok": False,
            "html": "<div style='color:var(--text-danger);'>Дата выходит за пределы доступного диапазона прогноза</div>"
        })

    hour_map = {'morning': 6, 'day': 13, 'evening': 20, 'night': 2}
    target_hour = hour_map.get(time_of_day, 12)

    if target_date < today:
        weather_data = get_historical_weather_for_waterbody(waterbody, target_date, target_hour)
    else:
        weather_data = get_forecast_weather_for_waterbody(waterbody, target_date, target_hour)

    if weather_data is None or weather_data.temperature is None:
        html = """
        <div style='background:var(--bg-rejection); border:2px solid var(--text-danger); padding:20px; border-radius:8px; text-align:center;'>
            <div style='font-size:24px; margin-bottom:10px;'>Внимание</div>
            <div style='color:var(--text-danger); font-weight:700; font-size:var(--font-size-lg); margin-bottom:8px;'>
                Метеоданные недоступны
            </div>
            <div style='color:var(--text-muted); font-size:var(--font-size-sm);'>
                Не удалось получить данные о погоде для выбранной даты.<br>
                Прогноз клёва не может быть выполнен. Попробуйте выбрать другую дату.
            </div>
        </div>
        """
        return jsonify({"ok": True, "html": html})

    html = build_forecast_table_html(
        waterbody,
        fish_list=None,
        weather_row=weather_data,
        target_date=target_date,
        time_of_day=time_of_day,
        gear_names=gear_names,
        bait_names=bait_names,
    )
    return jsonify({"ok": True, "html": html})


@api.get('/waterbodies/<int:waterbody_id>/gears')
def waterbody_gears(waterbody_id: int):
    waterbody = Waterbody.query.get_or_404(waterbody_id)

    from .models import FishGear
    fish_ids = (
        db.session.query(WaterbodyFish.fish_id)
        .filter(WaterbodyFish.waterbody_id == waterbody.id)
        .all()
    )
    fish_ids = [f[0] for f in fish_ids]

    if not fish_ids:
        return jsonify({"gears": []})

    gear_ids = (
        db.session.query(FishGear.gear_id)
        .filter(FishGear.fish_id.in_(fish_ids))
        .distinct()
        .all()
    )
    gear_ids = [g[0] for g in gear_ids]

    gears = Gear.query.filter(Gear.id.in_(gear_ids)).order_by(Gear.name).all()
    return jsonify({"gears": [g.name for g in gears]})


@api.get('/waterbodies/<int:waterbody_id>/baits')
def waterbody_baits(waterbody_id: int):
    waterbody = Waterbody.query.get_or_404(waterbody_id)

    from .models import FishBait
    fish_ids = (
        db.session.query(WaterbodyFish.fish_id)
        .filter(WaterbodyFish.waterbody_id == waterbody.id)
        .all()
    )
    fish_ids = [f[0] for f in fish_ids]

    if not fish_ids:
        return jsonify({"baits": []})

    bait_ids = (
        db.session.query(FishBait.bait_id)
        .filter(FishBait.fish_id.in_(fish_ids))
        .distinct()
        .all()
    )
    bait_ids = [b[0] for b in bait_ids]

    baits = Bait.query.filter(Bait.id.in_(bait_ids)).order_by(Bait.name).all()
    return jsonify({"baits": [b.name for b in baits]})


@api.get('/waterbodies/<int:waterbody_id>/weather')
def waterbody_weather(waterbody_id: int):
    waterbody = Waterbody.query.get_or_404(waterbody_id)

    target_date_str = request.args.get('date', '')
    time_of_day = request.args.get('time', 'day')

    if not target_date_str:
        return jsonify({"ok": False, "error": "date parameter required"}), 400

    try:
        target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"ok": False, "error": "invalid date format"}), 400

    today = date.today()
    if target_date > today:
        return jsonify({"ok": False, "error": "date out of range (future dates not available)"}), 400

    hour_map = {'morning': 6, 'day': 13, 'evening': 20, 'night': 2}
    target_hour = hour_map.get(time_of_day, 13)

    if target_date == today:
        w = get_cached_weather_for_waterbody(waterbody, force_refresh=True)
    else:
        w = get_historical_weather_for_waterbody(waterbody, target_date, target_hour)

    if not w:
        return jsonify({"ok": True, "weather": None})

    return jsonify({
        "ok": True,
        "weather": {
            "temperature": w.temperature,
            "pressure": w.pressure,
            "humidity": w.humidity,
            "wind_speed": w.wind_speed,
            "wind_direction": w.wind_direction,
            "weather_desc": w.weather_desc,
        }
    })


@api.get('/waterbodies/<int:waterbody_id>/weather-cache')
def waterbody_weather_cache(waterbody_id: int):
    waterbody = Waterbody.query.get_or_404(waterbody_id)
    w = get_cached_weather_for_waterbody(waterbody)
    if not w:
        return jsonify({"ok": True, "weather": None})
    return jsonify({
        "ok": True,
        "weather": {
            "temperature": w.temperature,
            "pressure": w.pressure,
            "humidity": w.humidity,
            "wind_speed": w.wind_speed,
            "wind_direction": w.wind_direction,
            "weather_desc": w.weather_desc,
            "fetched_at": w.fetched_at.isoformat() if w.fetched_at else None,
        }
    })


@api.post('/favorites/toggle/<int:waterbody_id>')
@login_required
def favorites_toggle(waterbody_id: int):
    fav = Favorite.query.filter_by(user_id=current_user.id, waterbody_id=waterbody_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({"ok": True, "is_favorite": False})

    fav = Favorite(user_id=current_user.id, waterbody_id=waterbody_id)
    db.session.add(fav)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
    return jsonify({"ok": True, "is_favorite": True})


@api.get('/favorites/status/<int:waterbody_id>')
def favorites_status(waterbody_id: int):
    if not current_user.is_authenticated:
        return jsonify({"ok": True, "is_favorite": False})
    fav = Favorite.query.filter_by(user_id=current_user.id, waterbody_id=waterbody_id).first()
    return jsonify({"ok": True, "is_favorite": bool(fav)})


@api.post('/reports/<int:report_id>/comments')
@login_required
def add_comment(report_id: int):
    report = FishingReport.query.get_or_404(report_id)
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "empty"}), 400

    c = Comment(user_id=current_user.id, report_id=report.id, text=text)
    db.session.add(c)
    db.session.commit()
    return jsonify({
        "ok": True,
        "comment": {
            "id": c.id,
            "user": current_user.full_name,
            "text": c.text,
            "created_at": c.created_at.isoformat(),
        }
    })


def _is_moderator():
    return current_user.is_authenticated and current_user.role in ("moderator", "admin")


@api.post('/moderate/reports/<int:report_id>/approve')
@login_required
def moderate_approve(report_id: int):
    if not _is_moderator():
        return jsonify({"ok": False, "error": "forbidden"}), 403
    report = FishingReport.query.get_or_404(report_id)
    report.status = 'approved'
    report.rejection_reason = None
    report.moderated_at = datetime.utcnow()
    report.moderated_by = current_user.id
    db.session.commit()
    update_waterbody_stats(report.waterbody_id)
    return jsonify({"ok": True})


@api.post('/moderate/reports/<int:report_id>/reject')
@login_required
def moderate_reject(report_id: int):
    if not _is_moderator():
        return jsonify({"ok": False, "error": "forbidden"}), 403
    report = FishingReport.query.get_or_404(report_id)

    payload = request.get_json(silent=True) or {}
    reason = (payload.get("reason") or "").strip()
    if not reason:
        reason = "Причина не указана"

    report.status = 'rejected'
    report.rejection_reason = reason
    report.moderated_at = datetime.utcnow()
    report.moderated_by = current_user.id
    db.session.commit()
    update_waterbody_stats(report.waterbody_id)
    return jsonify({"ok": True})


@api.get('/gears/all')
def all_gears():
    gears = Gear.query.order_by(Gear.name).all()
    return jsonify({"gears": [g.name for g in gears]})


@api.get('/baits/all')
def all_baits():
    baits = Bait.query.order_by(Bait.name).all()
    return jsonify({"baits": [b.name for b in baits]})


@api.get('/regions/all')
def all_regions():
    regions = Region.query.order_by(Region.name).all()
    return jsonify({"regions": [{"id": r.id, "name": r.name} for r in regions]})


@api.get('/fish/all')
def all_fish_species():
    fish = FishSpecies.query.order_by(FishSpecies.name).all()
    return jsonify({"fish": [{"id": f.id, "name": f.name} for f in fish]})


@api.get('/waterbodies/<int:waterbody_id>/fish')
def waterbody_fish(waterbody_id: int):
    waterbody = Waterbody.query.get_or_404(waterbody_id)
    fish_ids = [wf.fish_id for wf in WaterbodyFish.query.filter_by(waterbody_id=waterbody_id).all()]
    return jsonify({"fish_ids": fish_ids})


@api.get('/regions/<int:region_id>/rules')
def region_fishing_rules(region_id: int):
    region = Region.query.get_or_404(region_id)

    # Общее правило (FishingRule)
    general_rule = FishingRule.query.filter_by(region_id=region.id).first()
    general_rule_data = None
    if general_rule:
        general_rule_data = {
            "daily_limit_kg": general_rule.daily_limit_kg,
            "allowed_gear": general_rule.allowed_gear,
            "prohibited_gear": general_rule.prohibited_gear,
            "source": general_rule.source,
            "ban_start": general_rule.ban_start.isoformat() if general_rule.ban_start else None,
            "ban_end": general_rule.ban_end.isoformat() if general_rule.ban_end else None,
        }

    # Региональные правила по видам
    regional_rules = RegionalFishingRule.query.filter_by(region_id=region.id).all()
    rules_data = []
    for rule in regional_rules:
        fish = FishSpecies.query.get(rule.fish_id)
        if fish:
            allowed_gear = []
            if rule.allowed_gear:
                try:
                    allowed_gear = json.loads(rule.allowed_gear)
                except:
                    allowed_gear = [rule.allowed_gear] if rule.allowed_gear else []
            prohibited_gear = []
            if rule.prohibited_gear:
                try:
                    prohibited_gear = json.loads(rule.prohibited_gear)
                except:
                    prohibited_gear = [rule.prohibited_gear] if rule.prohibited_gear else []

            rules_data.append({
                "fish_id": fish.id,
                "fish_name": fish.name,
                "ban_start": rule.ban_start.isoformat() if rule.ban_start else None,
                "ban_end": rule.ban_end.isoformat() if rule.ban_end else None,
                "min_size_cm": rule.min_size_cm,
                "daily_limit_kg": rule.daily_limit_kg,
                "daily_limit_pcs": rule.daily_limit_pcs,
                "allowed_gear": allowed_gear,
                "prohibited_gear": prohibited_gear,
                "is_prohibited": rule.is_prohibited
            })

    # Сезонные запреты
    seasonal_bans = SeasonalBan.query.filter_by(region_id=region.id).all()
    seasonal_bans_data = []
    for ban in seasonal_bans:
        seasonal_bans_data.append({
            "ban_start": ban.ban_start.isoformat() if ban.ban_start else None,
            "ban_end": ban.ban_end.isoformat() if ban.ban_end else None,
            "description": ban.description
        })

    # Запретные зоны
    restricted_areas = RestrictedArea.query.filter_by(region_id=region.id).all()
    restricted_areas_data = []
    for area in restricted_areas:
        restricted_areas_data.append({
            "id": area.id,
            "name": area.name,
            "area_type": area.area_type,
            "restriction_start": area.restriction_start.isoformat() if area.restriction_start else None,
            "restriction_end": area.restriction_end.isoformat() if area.restriction_end else None,
            "geometry_geojson": area.geometry_geojson
        })

    # Суточные лимиты
    daily_limits_data = []
    if general_rule:
        daily_limits = DailyLimit.query.filter_by(rule_id=general_rule.id).all()
        for dl in daily_limits:
            fish = FishSpecies.query.get(dl.fish_id)
            if fish:
                daily_limits_data.append({
                    "fish_id": fish.id,
                    "fish_name": fish.name,
                    "limit_kg": dl.limit_kg,
                    "limit_pcs": dl.limit_pcs,
                    "min_size_cm": dl.min_size_cm,
                    "is_prohibited": dl.is_prohibited
                })

    return jsonify({
        "ok": True,
        "region": {
            "id": region.id,
            "name": region.name,
            "basin": region.basin
        },
        "general_rule": general_rule_data,
        "regional_rules": rules_data,
        "seasonal_bans": seasonal_bans_data,
        "restricted_areas": restricted_areas_data,
        "daily_limits": daily_limits_data
    })
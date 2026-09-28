from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, date, time as dtime
from typing import List, Optional
import math


# ============================================================
#  Расчёт фазы Луны на чистом Python (алгоритм Meeus)
# ============================================================

def _julian_day(dt: datetime) -> float:
    year, month, day = dt.year, dt.month, dt.day
    if month <= 2:
        year -= 1
        month += 12
    A = year // 100
    B = 2 - A + A // 4
    return int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5


def _moon_phase_fraction(dt: datetime) -> float:
    jd = _julian_day(dt)
    T = (jd - 2451545.0) / 36525.0
    M = math.radians((357.5291 + 35999.0503 * T) % 360)
    Mp = math.radians((134.9634 + 477198.8676 * T) % 360)
    F = math.radians((93.2721 + 483202.0175 * T) % 360)
    D = math.radians((297.8502 + 445267.1115 * T) % 360)

    phase_angle = (180.0
                   - math.degrees(D)
                   - 6.289 * math.sin(Mp)
                   + 2.100 * math.sin(M)
                   - 1.274 * math.sin(2 * D - Mp)
                   - 0.658 * math.sin(2 * D)
                   - 0.214 * math.sin(2 * Mp)
                   - 0.112 * math.sin(D)) % 360

    return (phase_angle % 360.0) / 360.0


def _moon_phase_name(dt: datetime) -> str:
    frac = _moon_phase_fraction(dt)
    if frac < 0.05 or frac > 0.95:
        return 'Новолуние'
    elif frac < 0.25:
        return 'Растущая Луна'
    elif 0.45 <= frac <= 0.55:
        return 'Полнолуние'
    elif frac < 0.50:
        return 'Первая четверть'
    elif frac < 0.75:
        return 'Убывающая Луна'
    else:
        return 'Последняя четверть'


# ============================================================
#  Вспомогательные классы
# ============================================================

@dataclass
class WeatherLike:
    temperature: float | None = None
    pressure: float | None = None
    wind_speed: float | None = None
    wind_direction: float | None = None
    humidity: float | None = None
    weather_desc: str | None = None
    is_available: bool = True


def _clamp(x: float, a: float = 0.0, b: float = 100.0) -> float:
    return max(a, min(b, x))


# ============================================================
#  ПРОВЕРКА ОГРАНИЧЕНИЙ ПО ДАТЕ
# ============================================================

def check_fishing_restrictions(waterbody, target_date: date):
    from .models import FishingRule, DailyLimit

    result = {
        'is_banned_period': False,
        'ban_description': '',
        'daily_limit_kg': None,
        'allowed_gear': '',
        'prohibited_gear': '',
        'prohibited_fish_ids': [],
    }

    if not waterbody or not waterbody.region_id:
        return result

    rule = FishingRule.query.filter_by(region_id=waterbody.region_id).first()
    if not rule:
        return result

    if rule.ban_start and rule.ban_end:
        if rule.ban_start <= target_date <= rule.ban_end:
            result['is_banned_period'] = True
            result['ban_description'] = (
                f'НЕРЕСТОВЫЙ ЗАПРЕТ действует с {rule.ban_start.strftime("%d.%m.%Y")} '
                f'по {rule.ban_end.strftime("%d.%m.%Y")}. Рыбалка полностью запрещена!'
            )

    result['daily_limit_kg'] = rule.daily_limit_kg
    result['allowed_gear'] = rule.allowed_gear or ''
    result['prohibited_gear'] = rule.prohibited_gear or ''

    prohibited = (
        DailyLimit.query
        .filter_by(rule_id=rule.id, is_prohibited=True)
        .all()
    )
    result['prohibited_fish_ids'] = [dl.fish_id for dl in prohibited]

    return result


def check_gear_restriction(gear_name: str, prohibited_gear_text: str) -> bool:
    if not gear_name or not prohibited_gear_text:
        return False
    gear_lower = gear_name.lower()
    prohibited_lower = prohibited_gear_text.lower()
    return gear_lower in prohibited_lower


# ============================================================
#  РАСЧЁТ ВЛИЯНИЯ ФАКТОРОВ
# ============================================================

def get_moon_multiplier(phase_fraction: float) -> float:
    """Возвращает множитель клёва от фазы луны"""
    if phase_fraction < 0.05 or phase_fraction > 0.95:
        return 1.3
    elif 0.22 < phase_fraction < 0.28 or 0.72 < phase_fraction < 0.78:
        return 0.7
    else:
        return 1.0


def get_time_multiplier(time_of_day: str) -> float:
    """Возвращает множитель клёва от времени суток"""
    multipliers = {
        'morning': 1.25,
        'evening': 1.2,
        'day': 0.8,
        'night': 0.7
    }
    return multipliers.get(time_of_day, 1.0)


def get_pressure_multiplier(pressure: float) -> float:
    """Возвращает множитель клёва от атмосферного давления"""
    if pressure is None:
        return 1.0
    
    if 755 <= pressure <= 765:
        return 1.2
    elif 750 <= pressure <= 770:
        return 1.1
    elif 745 <= pressure <= 775:
        return 1.0
    elif 740 <= pressure <= 780:
        return 0.85
    else:
        return 0.7


def get_wind_multiplier(wind_speed: float) -> float:
    """Возвращает множитель клёва от скорости ветра"""
    if wind_speed is None:
        return 1.0
    
    if wind_speed < 1:
        return 0.95
    elif 1 <= wind_speed <= 3:
        return 1.15
    elif 3 < wind_speed <= 5:
        return 1.1
    elif 5 < wind_speed <= 8:
        return 1.0
    elif 8 < wind_speed <= 11:
        return 0.85
    elif 11 < wind_speed <= 15:
        return 0.7
    else:
        return 0.5


def get_weather_multiplier(weather_desc: str) -> float:
    """Возвращает множитель клёва от погодных условий"""
    if not weather_desc:
        return 1.0
    
    weather_lower = weather_desc.lower()
    
    if 'ясно' in weather_lower:
        return 1.1
    elif 'преимущественно ясно' in weather_lower:
        return 1.05
    elif 'переменная облачность' in weather_lower:
        return 1.0
    elif 'пасмурно' in weather_lower:
        return 0.9
    elif 'туман' in weather_lower:
        return 0.8
    elif 'морось' in weather_lower:
        return 0.75
    elif 'дождь' in weather_lower:
        return 0.65
    elif 'ливень' in weather_lower:
        return 0.5
    elif 'снег' in weather_lower:
        return 0.55
    elif 'гроза' in weather_lower:
        return 0.3
    else:
        return 1.0


def get_temperature_multiplier(temp: float, fish_temp_min: float, fish_temp_max: float) -> float:
    """Возвращает множитель клёва от температуры для конкретной рыбы"""
    if temp is None:
        return 1.0
    
    if fish_temp_min <= temp <= fish_temp_max:
        return 1.2
    elif (fish_temp_min - 3) <= temp <= (fish_temp_max + 3):
        return 1.0
    elif (fish_temp_min - 6) <= temp <= (fish_temp_max + 6):
        return 0.8
    else:
        return 0.5


def get_season_multiplier(target_date: date, fish_seasonality: str) -> float:
    """Возвращает множитель клёва от сезона"""
    if not fish_seasonality or fish_seasonality == 'Не указана':
        return 1.0
    
    month = target_date.month
    if month in [12, 1, 2]:
        season = "зима"
    elif month in [3, 4, 5]:
        season = "весна"
    elif month in [6, 7, 8]:
        season = "лето"
    else:
        season = "осень"
    
    fish_season_lower = fish_seasonality.lower()
    
    if season in fish_season_lower:
        return 1.15
    elif any(s in fish_season_lower for s in ['круглый год', 'круглогодично']):
        return 1.0
    else:
        return 0.7


def get_gear_bait_multiplier(
    gear_names: Optional[List[str]],
    bait_names: Optional[List[str]],
    suitable_gears: List[str],
    suitable_baits: List[str]
) -> float:
    """
    Возвращает множитель клёва от снастей и наживок.
    - Если снасти и наживки не указаны: множитель 1.0 (считаем что для каждой рыбы выбраны подходящие)
    - Если указаны подходящие: множитель 1.0 (такой же, как без выбора)
    - Если указаны неподходящие: множитель < 1.0 (снижение)
    """
    multiplier = 1.0

    # Проверяем снасти (если указаны)
    if gear_names:
        has_suitable_gear = any(g in suitable_gears for g in gear_names)
        if not has_suitable_gear:
            # Неподходящие снасти - значительное снижение клева
            multiplier *= 0.4  # 40% от базового

    # Проверяем наживки (если указаны)
    if bait_names:
        has_suitable_bait = any(b in suitable_baits for b in bait_names)
        if not has_suitable_bait:
            # Неподходящие наживки - умеренное снижение клева
            multiplier *= 0.6  # 60% от базового

    # Если указаны и снасти, и наживки, и обе неподходящие - дополнительное снижение
    if gear_names and bait_names:
        has_suitable_gear = any(g in suitable_gears for g in gear_names)
        has_suitable_bait = any(b in suitable_baits for b in bait_names)
        if not has_suitable_gear and not has_suitable_bait:
            multiplier *= 0.7  # Дополнительное снижение

    return max(0.1, min(multiplier, 1.0))


def get_night_fish_bonus(time_of_day: str, is_night_fish: bool) -> float:
    """Бонус для ночных рыб в ночное время"""
    if is_night_fish and time_of_day == 'night':
        return 1.3
    return 1.0


# ============================================================
#  ОСНОВНАЯ ФУНКЦИЯ — ГЕНЕРАЦИЯ ПРОГНОЗА
# ============================================================

def calculate_bite_index(
    fish,
    weather: WeatherLike,
    moon_phase: float,
    time_of_day: str,
    target_date: date,
    gear_names: List[str] = None,
    bait_names: List[str] = None,
) -> int:
    """Расчёт индекса клёва для конкретной рыбы (0-100%)"""
    if gear_names is None:
        gear_names = []
    if bait_names is None:
        bait_names = []
    
    base_score = 50.0
    total_multiplier = 1.0
    
    # Общие факторы
    total_multiplier *= get_moon_multiplier(moon_phase)
    total_multiplier *= get_time_multiplier(time_of_day)
    total_multiplier *= get_pressure_multiplier(weather.pressure or 760.0)
    total_multiplier *= get_wind_multiplier(weather.wind_speed or 0.0)
    total_multiplier *= get_weather_multiplier(weather.weather_desc or "")
    
    # Индивидуальные факторы для рыбы
    temp_min = getattr(fish, 'optimal_temp_min', 10.0)
    temp_max = getattr(fish, 'optimal_temp_max', 22.0)
    total_multiplier *= get_temperature_multiplier(weather.temperature or 15.0, temp_min, temp_max)
    total_multiplier *= get_season_multiplier(target_date, getattr(fish, 'seasonality', 'Не указана'))
    
    # Снасти и наживки
    suitable_gears = [link.gear.name for link in fish.gear_links]
    suitable_baits = [link.bait.name for link in fish.bait_links]
    total_multiplier *= get_gear_bait_multiplier(gear_names or [], bait_names or [], suitable_gears, suitable_baits)
    
    # Бонус для ночных рыб
    is_night_fish = getattr(fish, 'name', '') in ['Налим', 'Сом']
    total_multiplier *= get_night_fish_bonus(time_of_day, is_night_fish)
    
    final_score = int(round(_clamp(base_score * total_multiplier)))
    return final_score


def get_activity_grade(score: int) -> tuple:
    """Возвращает оценку активности и цвет"""
    if score <= 20:
        return "Очень низкая", "var(--text-danger)"
    elif score <= 40:
        return "Низкая", "var(--text-warning)"
    elif score <= 60:
        return "Средняя", "#c6b34a"
    elif score <= 80:
        return "Хорошая", "#7dbb6a"
    else:
        return "Отличная", "var(--text-success)"


def degrees_to_wind_direction(degrees: float) -> str:
    """Преобразует градусы в текстовое направление ветра"""
    if degrees is None:
        return ""
    if degrees >= 0 and degrees < 22.5:
        return "С"
    elif degrees < 67.5:
        return "СВ"
    elif degrees < 112.5:
        return "В"
    elif degrees < 157.5:
        return "ЮВ"
    elif degrees < 202.5:
        return "Ю"
    elif degrees < 247.5:
        return "ЮЗ"
    elif degrees < 292.5:
        return "З"
    elif degrees < 337.5:
        return "СЗ"
    else:
        return "С"


def build_forecast_table_html(
    waterbody,
    fish_list=None,
    weather_row=None,
    target_date: Optional[date] = None,
    time_of_day: str = 'morning',
    gear_names: List[str] = None,
    bait_names: List[str] = None,
) -> str:
    if target_date is None:
        target_date = datetime.now().date()
    
    if gear_names is None:
        gear_names = []
    if bait_names is None:
        bait_names = []

    # Проверка наличия погодных данных
    weather_available = weather_row is not None and weather_row.temperature is not None
    
    if not weather_available:
        return """
        <div style='background:var(--bg-rejection); border:2px solid var(--text-danger); padding:20px; border-radius:8px; text-align:center;'>
            <div style='font-size:24px; margin-bottom:10px;'>Внимание</div>
            <div style='color:var(--text-danger); font-weight:700; font-size:var(--font-size-lg); margin-bottom:8px;'>
                Метеоданные недоступны
            </div>
            <div style='color:var(--text-muted); font-size:var(--font-size-sm);'>
                Не удалось получить данные о погоде для выбранной даты.<br>
                Прогноз клёва не может быть выполнен.
            </div>
        </div>
        """

    if fish_list is None:
        try:
            from . import db as _db
            from .models import FishSpecies as FS, WaterbodyFish
            fish_list = (
                _db.session.query(FS)
                .join(WaterbodyFish)
                .filter(WaterbodyFish.waterbody_id == waterbody.id)
                .all()
            )
        except Exception:
            fish_list = []

    if not fish_list:
        return "<div style='color:var(--text-muted);'>Нет данных о видах рыб в этом водоёме.</div>"

    restrictions = check_fishing_restrictions(waterbody, target_date)

    # Создаём объект погоды
    base = WeatherLike(
        temperature=weather_row.temperature if weather_row else 15.0,
        pressure=weather_row.pressure if weather_row else 760.0,
        wind_speed=weather_row.wind_speed if weather_row else 0.0,
        wind_direction=weather_row.wind_direction if weather_row else 0.0,
        humidity=weather_row.humidity if weather_row else 50.0,
        weather_desc=weather_row.weather_desc if weather_row else "Ясно",
        is_available=True
    )
    
    # Расчёт фазы луны
    hour_map = {'morning': 6, 'day': 13, 'evening': 20, 'night': 2}
    target_dt = datetime.combine(target_date, dtime(hour_map.get(time_of_day, 12), 0))
    moon_phase = _moon_phase_fraction(target_dt)
    moon_name = _moon_phase_name(target_dt)
    
    parts = []

    time_labels = {'morning': 'Утро (06:00)', 'day': 'День (13:00)', 'evening': 'Вечер (20:00)', 'night': 'Ночь (02:00)'}
    
    gear_info = ""
    if gear_names:
        gear_info += f"Снасти: {', '.join(gear_names)}<br>"
    if bait_names:
        gear_info += f"Наживки: {', '.join(bait_names)}"
    
    parts.append(
        f"<div style='margin-bottom:10px; font-size:var(--font-size-base); color:var(--text-heading);'>"
        f"<strong>{target_date.strftime('%d.%m.%Y')}</strong> • "
        f"{time_labels.get(time_of_day, '')} • "
        f"{moon_name}"
        f"</div>"
    )
    
    if gear_info:
        parts.append(
            f"<div style='margin-bottom:10px; font-size:var(--font-size-sm); color:var(--text-muted); background:var(--bg-input); padding:8px; border-radius:4px;'>"
            f"{gear_info}"
            f"</div>"
        )

    if restrictions['is_banned_period']:
        parts.append(
            "<div style='background:var(--bg-rejection); border:2px solid var(--text-danger); padding:14px; margin-bottom:14px; border-radius:4px;'>"
            f"<div style='color:var(--text-danger); font-weight:700; font-size:var(--font-size-base); margin-bottom:6px;'>"
            f"ВНИМАНИЕ: НЕРЕСТОВЫЙ ЗАПРЕТ!</div>"
            f"<div style='color:var(--text-danger); font-size:var(--font-size-sm);'>{restrictions['ban_description']}</div>"
            f"<div style='color:var(--text-warning); font-size:var(--font-size-sm); margin-top:8px;'>"
            f"В этот период рыбалка полностью запрещена. Прогноз ниже носит справочный характер.</div>"
            "</div>"
        )

    if gear_names and restrictions['prohibited_gear']:
        prohibited_found = []
        for gear in gear_names or []:
            if check_gear_restriction(gear, restrictions['prohibited_gear']):
                prohibited_found.append(gear)
        if prohibited_found:
            parts.append(
                "<div style='background:var(--bg-rejection); border:1px solid var(--text-danger); padding:10px; margin-bottom:12px; border-radius:4px;'>"
                f"<div style='color:var(--text-danger); font-size:var(--font-size-sm);'>"
            f"Снасти «{', '.join(prohibited_found)}» запрещены в этом регионе! "
                f"Запрещённые снасти: {restrictions['prohibited_gear']}</div>"
                "</div>"
            )

    if restrictions['daily_limit_kg']:
        parts.append(
            f"<div style='font-size:var(--font-size-sm); color:var(--text-muted); margin-bottom:10px;'>"
            f"Суточный лимит вылова: <strong>{restrictions['daily_limit_kg']} кг</strong>"
            f"</div>"
        )

    if restrictions['allowed_gear'] or restrictions['prohibited_gear']:
        parts.append(
            "<div style='font-size:var(--font-size-xs); color:var(--text-muted); margin-bottom:10px; line-height:1.6;'>"
            f"Разрешённые снасти: {restrictions['allowed_gear'] or 'не указаны'}<br>"
            f"Запрещённые снасти: <span style='color:var(--text-danger);'>{restrictions['prohibited_gear'] or 'не указаны'}</span>"
            "</div>"
        )

    # Погода с округлением давления до десятых и добавлением направления ветра
    pressure_rounded = round(base.pressure, 1) if base.pressure is not None else None
    
    # Формируем строку с направлением ветра
    wind_str = ""
    if base.wind_speed is not None:
        wind_dir_text = degrees_to_wind_direction(base.wind_direction or 0.0)
        if wind_dir_text:
            wind_str = f"ветер {wind_dir_text} {base.wind_speed} м/с"
        else:
            wind_str = f"ветер {base.wind_speed} м/с"
    
    weather_note = (
        f"<div style='font-size:var(--font-size-sm); color:var(--text-muted); margin-bottom:10px;'>"
        f"Погода: {base.temperature}°C, {pressure_rounded} мм рт.ст., "
        f"{wind_str} • {base.weather_desc or ''}"
        f"</div>"
    )
    parts.append(weather_note)

    cols = (
        "<th style='text-align:left; padding:8px; border-bottom:1px solid var(--border-tag);'>Вид рыбы</th>"
        "<th style='text-align:center; padding:8px; border-bottom:1px solid var(--border-tag);'>Клёв</th>"
    )

    rows = []
    
    for fish in fish_list:
        icon = getattr(fish, 'icon', '')
        name = getattr(fish, 'name', '?')
        
        suitable_gears = [link.gear.name for link in fish.gear_links]
        suitable_baits = [link.bait.name for link in fish.bait_links]
        
        # Фильтрация по снастям и наживкам (если они выбраны)
        has_suitable_gear = not gear_names or any(g in suitable_gears for g in gear_names)
        has_suitable_bait = not bait_names or any(b in suitable_baits for b in bait_names)
        
        if not has_suitable_gear or not has_suitable_bait:
            continue

        if fish.id in restrictions['prohibited_fish_ids']:
            rows.append(
                "<tr>"
                f"<td style='padding:8px; border-bottom:1px solid var(--border-tag); color:var(--text-danger);'>{icon} {name}</td>"
                "<td style='padding:8px; text-align:center; border-bottom:1px solid var(--border-tag);'>"
                "<span style='display:inline-block; padding:4px 8px; border:1px solid var(--border-danger); background:var(--bg-rejection); color:var(--text-danger); font-weight:700;'>ЗАПРЕЩЕН</span>"
                "</td>"
                "</tr>"
            )
            continue

        score = calculate_bite_index(
            fish, base, moon_phase, time_of_day, target_date, gear_names, bait_names
        )
        
        grade, color = get_activity_grade(score)
        
        rows.append(
            "<tr>"
            f"<td style='padding:8px; border-bottom:1px solid var(--border-tag); color:var(--text-heading);'>{icon} {name}</td>"
            f"<td style='padding:8px; border-bottom:1px solid var(--border-tag);'>"
            f"<div style='display:flex; align-items:center; gap:8px; flex-wrap:wrap;'>"
            f"<span style='min-width:60px; font-weight:700; color:{color};'>{score}%</span>"
            f"<div style='flex:1; height:8px; background:var(--border-tag); border-radius:4px; overflow:hidden; max-width:150px;'>"
            f"<div style='width:{score}%; height:100%; background:{color}; border-radius:4px;'></div>"
            f"</div>"
            f"<span style='font-size:var(--font-size-sm); color:var(--text-muted);'>{grade}</span>"
            f"</div>"
            f"</td>"
            "</tr>"
        )

    if not rows:
        parts.append(
            "<div style='color:var(--text-warning); padding:20px; text-align:center;'>"
            "Нет видов рыб, соответствующих выбранным снастям и наживкам. Попробуйте изменить выбор."
            "</div>"
        )
    else:
        parts.append(
            "<div style='overflow:auto;'>"
            "<table style='width:100%; border-collapse:collapse; font-size:var(--font-size-sm);'>"
            "<thead><tr>"
            f"{cols}"
            "</tr></thead>"
            "<tbody>"
            + "".join(rows) +
            "</tbody></table></div>"
        )

    return "".join(parts)
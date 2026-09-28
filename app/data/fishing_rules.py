# app/data/fishing_rules.py
# Правила рыболовства для Волжско-Каспийского рыбохозяйственного бассейна

from datetime import date

# Данные для таблицы FishingRule (общие правила для регионов)
fishing_rules_data = [
    # Астраханская область
    {
        'region_id': 1,  # Астраханская область
        'ban_start': date(2023, 4, 15),
        'ban_end': date(2023, 6, 15),
        'daily_limit_kg': 5.0,
        'allowed_gear': 'Удочка, спиннинг, фидер, поплавочная снасть',
        'prohibited_gear': 'Сеть, электроудочка, взрывчатые вещества',
        'source': 'Приказ Минсельхоза РФ от 13.10.2022 N 695'
    },

    # Волгоградская область
    {
        'region_id': 2,  # Волгоградская область
        'ban_start': date(2023, 4, 10),
        'ban_end': date(2023, 6, 10),
        'daily_limit_kg': 5.0,
        'allowed_gear': 'Удочка, спиннинг, фидер, поплавочная снасть',
        'prohibited_gear': 'Сеть, электроудочка, взрывчатые вещества',
        'source': 'Приказ Минсельхоза РФ от 13.10.2022 N 695'
    },

    # Республика Калмыкия
    {
        'region_id': 3,  # Республика Калмыкия
        'ban_start': date(2023, 4, 1),
        'ban_end': date(2023, 6, 1),
        'daily_limit_kg': 5.0,
        'allowed_gear': 'Удочка, спиннинг, фидер, поплавочная снасть',
        'prohibited_gear': 'Сеть, электроудочка, взрывчатые вещества',
        'source': 'Приказ Минсельхоза РФ от 13.10.2022 N 695'
    }
]

# Данные для таблицы RegionalFishingRule (правила для конкретных видов рыб)
regional_fishing_rules_data = [
    # Астраханская область - Вобла
    {
        'region_id': 1,
        'fish_id': 1,  # Вобла
        'ban_start': date(2023, 4, 15),
        'ban_end': date(2023, 6, 15),
        'min_size_cm': 17,
        'daily_limit_kg': 5.0,
        'daily_limit_pcs': 30,
        'is_prohibited': False,
        'allowed_gear': 'Удочка, спиннинг, фидер, поплавочная снасть',
        'prohibited_gear': 'Сеть с ячеей менее 28 мм'
    },

    # Астраханская область - Лещ
    {
        'region_id': 1,
        'fish_id': 2,  # Лещ
        'ban_start': date(2023, 4, 15),
        'ban_end': date(2023, 6, 15),
        'min_size_cm': 24,
        'daily_limit_kg': 5.0,
        'daily_limit_pcs': 10,
        'is_prohibited': False,
        'allowed_gear': 'Удочка, спиннинг, фидер, поплавочная снасть',
        'prohibited_gear': 'Сеть с ячеей менее 28 мм'
    },

    # Астраханская область - Судак
    {
        'region_id': 1,
        'fish_id': 3,  # Судак
        'ban_start': date(2023, 4, 15),
        'ban_end': date(2023, 6, 15),
        'min_size_cm': 37,
        'daily_limit_kg': 5.0,
        'daily_limit_pcs': 5,
        'is_prohibited': False,
        'allowed_gear': 'Удочка, спиннинг, фидер, поплавочная снасть',
        'prohibited_gear': 'Сеть с ячеей менее 28 мм'
    },

    # Волгоградская область - Вобла
    {
        'region_id': 2,
        'fish_id': 1,  # Вобла
        'ban_start': date(2023, 4, 10),
        'ban_end': date(2023, 6, 10),
        'min_size_cm': 17,
        'daily_limit_kg': 5.0,
        'daily_limit_pcs': 30,
        'is_prohibited': False,
        'allowed_gear': 'Удочка, спиннинг, фидер, поплавочная снасть',
        'prohibited_gear': 'Сеть с ячеей менее 28 мм'
    },

    # Волгоградская область - Лещ
    {
        'region_id': 2,
        'fish_id': 2,  # Лещ
        'ban_start': date(2023, 4, 10),
        'ban_end': date(2023, 6, 10),
        'min_size_cm': 24,
        'daily_limit_kg': 5.0,
        'daily_limit_pcs': 10,
        'is_prohibited': False,
        'allowed_gear': 'Удочка, спиннинг, фидер, поплавочная снасть',
        'prohibited_gear': 'Сеть с ячеей менее 28 мм'
    },

    # Республика Калмыкия - Вобла
    {
        'region_id': 3,
        'fish_id': 1,  # Вобла
        'ban_start': date(2023, 4, 1),
        'ban_end': date(2023, 6, 1),
        'min_size_cm': 17,
        'daily_limit_kg': 5.0,
        'daily_limit_pcs': 30,
        'is_prohibited': False,
        'allowed_gear': 'Удочка, спиннинг, фидер, поплавочная снасть',
        'prohibited_gear': 'Сеть с ячеей менее 28 мм'
    }
]

# Данные для таблицы SeasonalBan (сезонные запреты)
seasonal_bans_data = [
    # Весенний нерестовый запрет - Астраханская область
    {
        'region_id': 1,
        'ban_start': date(2023, 4, 15),
        'ban_end': date(2023, 6, 15),
        'description': 'Весенний нерестовый запрет на всех водных объектах Астраханской области'
    },

    # Весенний нерестовый запрет - Волгоградская область
    {
        'region_id': 2,
        'ban_start': date(2023, 4, 10),
        'ban_end': date(2023, 6, 10),
        'description': 'Весенний нерестовый запрет на всех водных объектах Волгоградской области'
    },

    # Весенний нерестовый запрет - Республика Калмыкия
    {
        'region_id': 3,
        'ban_start': date(2023, 4, 1),
        'ban_end': date(2023, 6, 1),
        'description': 'Весенний нерестовый запрет на всех водных объектах Республики Калмыкия'
    }
]

# Данные для таблицы DailyLimit (суточные лимиты вылова)
daily_limits_data = [
    # Астраханская область - Вобла
    {
        'rule_id': 1,
        'fish_id': 1,  # Вобла
        'limit_kg': 5.0,
        'limit_pcs': 30,
        'min_size_cm': 17,
        'is_prohibited': False
    },

    # Астраханская область - Лещ
    {
        'rule_id': 1,
        'fish_id': 2,  # Лещ
        'limit_kg': 5.0,
        'limit_pcs': 10,
        'min_size_cm': 24,
        'is_prohibited': False
    },

    # Астраханская область - Судак
    {
        'rule_id': 1,
        'fish_id': 3,  # Судак
        'limit_kg': 5.0,
        'limit_pcs': 5,
        'min_size_cm': 37,
        'is_prohibited': False
    },

    # Волгоградская область - Вобла
    {
        'rule_id': 2,
        'fish_id': 1,  # Вобла
        'limit_kg': 5.0,
        'limit_pcs': 30,
        'min_size_cm': 17,
        'is_prohibited': False
    },

    # Волгоградская область - Лещ
    {
        'rule_id': 2,
        'fish_id': 2,  # Лещ
        'limit_kg': 5.0,
        'limit_pcs': 10,
        'min_size_cm': 24,
        'is_prohibited': False
    }
]

# Данные для таблицы RestrictedArea (запретные зоны)
restricted_areas_data = [
    # Запретная зона в дельте Волги
    {
        'name': 'Нерестилище в дельте Волги',
        'area_type': 'нерестилище',
        'region_id': 1,  # Астраханская область
        'geometry_geojson': '{"type": "Polygon", "coordinates": [[[46.0, 48.0], [46.1, 48.0], [46.1, 48.1], [46.0, 48.1], [46.0, 48.0]]]}',
        'restriction_start': date(2023, 4, 15),
        'restriction_end': date(2023, 7, 1)
    },

    # Запретная зона в Волгоградском водохранилище
    {
        'name': 'Заказник в Волгоградском водохранилище',
        'area_type': 'заказник',
        'region_id': 2,  # Волгоградская область
        'geometry_geojson': '{"type": "Polygon", "coordinates": [[[44.0, 56.0], [44.1, 56.0], [44.1, 56.1], [44.0, 56.1], [44.0, 56.0]]]}',
        'restriction_start': date(2023, 4, 10),
        'restriction_end': date(2023, 6, 10)
    }
]
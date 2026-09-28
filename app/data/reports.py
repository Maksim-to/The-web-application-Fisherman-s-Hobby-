# app/data/reports.py
# Создание 200 демо-отчётов

from ..models import FishingReport, User, Waterbody, Gear, Bait, FishSpecies, ReportGear, ReportBait
from datetime import datetime, timedelta
import random
import json

def create_demo_reports(db):
    """Создаёт 200 демо-отчётов с реалистичными данными"""
    # Получаем всех пользователей и водоёмы
    users = User.query.filter_by(role='user').all()
    waterbodies = Waterbody.query.all()

    if not users or not waterbodies:
        print("⚠️ Нет пользователей или водоёмов для создания отчётов")
        return

    # Получаем реальные данные из базы
    all_gears = Gear.query.all()
    all_baits = Bait.query.all()
    all_fish_species = FishSpecies.query.all()

    if not all_gears or not all_baits or not all_fish_species:
        print("⚠️ Нет данных о снастях, наживках или видах рыб в базе")
        return

    # Списки для генерации данных
    weather_types = [
        "Солнечно, безоблачно",
        "Переменная облачность",
        "Пасмурно, небольшой дождь",
        "Дождь, сильный ветер",
        "Гроза, ливень",
        "Туман, высокая влажность",
        "Снег, мороз",
        "Ясно, прохладно",
        "Ясно, тепло",
        "Облачно, прохладный ветер",
        "Пасмурно, без осадков",
        "Солнечно, легкий бриз",
        "Переменная облачность, слабый ветер",
        "Туман, безветрие",
        "Снегопад, умеренный ветер"
    ]

    weather_clouds_options = [
        "Ясно", "Преимущественно ясно", "Малооблачно", "Переменная облачность",
        "Облачно", "Пасмурно", "Сплошная облачность", "Туман", "Дымка",
        "Небольшой дождь", "Дождь", "Сильный дождь", "Гроза", "Снег", "Мокрый снег"
    ]

    descriptions = [
        "Отличная рыбалка! Клёв был с раннего утра до полудня. Использовал активную проводку с частыми паузами. Рыба брала уверенно, поклёвки чёткие. Погода способствовала хорошему клёву.",
        "Рыбалка прошла успешно, несмотря на переменчивую погоду. Пришлось экспериментировать с приманками, но в итоге нашёл рабочую комбинацию. Рыба была активна в придонном слое.",
        "Трофейный улов! Крупная щука клюнула на живца около коряги. Пришлось повозиться с вываживанием, но результат того стоит. Остальная рыба брала на классические приманки.",
        "Спокойная рыбалка с хорошим уловом. Лещ клевал на фидер с кормушкой, заполненной опарышем и мотылём. Поклёвки были нечастые, но уверенные. Отличный день на воде.",
        "Зимняя рыбалка принесла хорошие результаты. Окунь активно клевал на мормышку с мотылём. Пришлось часто менять лунки, но поиск оправдался отличным уловом.",
        "Экспериментальная рыбалка с новыми приманками. Воблер неожиданно сработал на щуку, хотя рассчитывал на окуня. Интересный опыт и хороший трофей.",
        "Семейная рыбалка с детьми. Ловили на поплавочную удочку с червями и опарышами. Дети были в восторге от каждого поклёвка. Хороший отдых и небольшой улов.",
        "Соревновательная рыбалка с друзьями. Уловистая снасть и правильная тактика принесли победу. Ключевым фактором стал выбор места и времени ловли.",
        "Ночная рыбалка на хищника. Сом взял на лягушку около берегового свала. Вываживание заняло более 20 минут, но адреналин того стоил.",
        "Фидерная рыбалка на течении. Лещ клевал уверенно, поклёвки чёткие. Прикормка сработала отлично, рыба держалась в одной точке. Хороший улов и приятный отдых.",
        "Рыбалка на незнакомом водоёме. Пришлось долго искать перспективное место, но поиск оправдался хорошим уловом. Ключевым фактором стал правильный выбор приманки.",
        "Утренняя рыбалка принесла отличные результаты. Рыба активно клевала в первые часы после восхода солнца. Использовал классическую снасть с червями.",
        "Дождливая погода не помешала хорошему клёву. Рыба брала уверенно, особенно на искусственные приманки. Отличный день несмотря на непогоду.",
        "Вечерняя рыбалка с друзьями. Клёв начался с заходом солнца и продолжался до темноты. Использовали светящиеся поплавки для удобства.",
        "Экспедиционная рыбалка на отдалённом озере. Пришлось преодолеть сложный путь, но результат того стоил. Уникальный опыт и отличный улов.",
        "Рыбалка с использованием эхолота. Технология помогла найти перспективные места и значительно увеличить улов. Современные методы работают!",
        "Осенняя рыбалка принесла неожиданно хорошие результаты. Рыба активно кормилась перед зимой, клёв был стабильным на протяжении всего дня."
    ]

    # Создаём 200 отчётов
    for i in range(200):
        # Выбираем случайного пользователя и водоём
        user = random.choice(users)
        waterbody = random.choice(waterbodies)

        # Генерируем случайную дату в течение последнего года
        days_ago = random.randint(1, 365)
        report_date = datetime.utcnow() - timedelta(days=days_ago)

        # Погода - округленные значения
        weather_temp = round(random.uniform(5.0, 30.0), 1)
        weather_pressure = round(random.uniform(740.0, 760.0), 1)
        weather_wind_speed = round(random.uniform(0.0, 15.0), 1)

        # Направление ветра на русском языке (как в форме)
        wind_directions = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
        weather_wind_dir = random.choice(wind_directions) if random.random() > 0.3 else None

        # Облачность
        weather_clouds = random.choice(weather_clouds_options) if random.random() > 0.2 else None

        # Формируем текстовое описание погоды
        weather_parts = []
        weather_parts.append(f"{weather_temp}°C")
        weather_parts.append(f"{weather_pressure} мм рт.ст.")
        if weather_wind_dir:
            weather_parts.append(f"ветер {weather_wind_dir} {weather_wind_speed} м/с")
        if weather_clouds:
            weather_parts.append(weather_clouds)
        weather_description = ", ".join(weather_parts)

        # Выбираем 1-3 снасти для отчета
        num_gears = random.randint(1, 3)
        selected_gears = random.sample(all_gears, min(num_gears, len(all_gears)))

        # Выбираем наживки для каждой снасти (1-3 наживки на снасть)
        gear_names = []
        gear_baits_data = []

        for gear in selected_gears:
            gear_names.append(gear.name)
            num_baits = random.randint(1, 3)
            selected_baits = random.sample(all_baits, min(num_baits, len(all_baits)))
            bait_names = [bait.name for bait in selected_baits]
            gear_baits_data.append(bait_names)

        # Формируем текстовые поля для совместимости
        gear_str = ", ".join(gear_names)
        all_bait_names = [bait for sublist in gear_baits_data for bait in sublist]
        bait_str = ", ".join(list(dict.fromkeys(all_bait_names)))  # Убираем дубликаты

        # Создаём улов в формате JSON
        num_fish_types = random.randint(1, 4)
        selected_fish = random.sample(all_fish_species, min(num_fish_types, len(all_fish_species)))

        fish_caught = []
        for fish in selected_fish:
            # Указываем и вес, и количество для реалистичности
            weight = round(random.uniform(0.5, 15.0), 1)
            count = random.randint(3, 20)
            fish_caught.append({
                'name': fish.name,
                'kg': weight,
                'pcs': count
            })

        # Создаём отчёт
        report = FishingReport(
            user_id=user.id,
            waterbody_id=waterbody.id,
            date=report_date.date(),
            weather=weather_description,
            weather_temp=weather_temp,
            weather_pressure=weather_pressure,
            weather_wind_dir=weather_wind_dir,
            weather_wind_speed=weather_wind_speed,
            weather_clouds=weather_clouds,
            gear=gear_str,
            bait=bait_str,
            description=random.choice(descriptions),
            fish_caught=json.dumps(fish_caught, ensure_ascii=False),
            rating=random.randint(3, 5),
            created_at=report_date,
            status='approved',
            moderated_at=report_date,
            moderated_by=1  # ID администратора
        )

        db.session.add(report)
        db.session.flush()

        # Создаём записи в ReportGear для каждой снасти
        for gear in selected_gears:
            report_gear = ReportGear(
                report_id=report.id,
                gear_id=gear.id,
                gear_name=gear.name
            )
            db.session.add(report_gear)
            db.session.flush()

            # Создаём записи в ReportBait для наживок этой снасти
            gear_baits = gear_baits_data[selected_gears.index(gear)]
            for bait_name in gear_baits:
                bait = next((b for b in all_baits if b.name == bait_name), None)
                if bait:
                    report_bait = ReportBait(
                        report_id=report.id,
                        bait_id=bait.id,
                        bait_name=bait.name,
                        report_gear_id=report_gear.id
                    )
                    db.session.add(report_bait)

        # Коммитим каждые 20 отчётов для оптимизации
        if (i + 1) % 20 == 0:
            db.session.commit()
            print(f"✅ Создано {i + 1} демо-отчётов...")

    db.session.commit()
    print(f'✅ Создано 200 демо-отчётов с реалистичными данными')

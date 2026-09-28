# app/data/users.py
# Создание пользователей (admin, moderator, demo)

from ..models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_users(db):
    """Создаёт пользователей: admin, moderator и demo пользователей"""
    # Проверяем, есть ли уже пользователи
    if User.query.first():
        print("Пользователи уже существуют, пропускаем создание")
        return

    # Создаём администратора
    admin = User(
        username="admin",
        email="admin@fisher.app",
        full_name="Администратор системы",
        role="admin",
        phone="+79991234567",
        birth_date=datetime(1985, 5, 15).date(),
        created_at=datetime.utcnow()
    )
    admin.set_password("1234")
    db.session.add(admin)

    # Создаём модератора
    moderator = User(
        username="moderator",
        email="moderator@fisher.app",
        full_name="Главный модератор",
        role="moderator",
        phone="+79991234568",
        birth_date=datetime(1990, 8, 22).date(),
        created_at=datetime.utcnow()
    )
    moderator.set_password("moderator123")
    db.session.add(moderator)

    # Создаём демо-пользователей
    demo_users = [
        {
            "username": "ivan_fisher",
            "email": "ivan@fisher.app",
            "full_name": "Иван Петров",
            "role": "user",
            "phone": "+79991234569",
            "birth_date": datetime(1988, 3, 10).date()
        },
        {
            "username": "marina_angler",
            "email": "marina@fisher.app",
            "full_name": "Марина Сидорова",
            "role": "user",
            "phone": "+79991234570",
            "birth_date": datetime(1992, 11, 5).date()
        },
        {
            "username": "alex_carp",
            "email": "alex@fisher.app",
            "full_name": "Алексей Карпов",
            "role": "user",
            "phone": "+79991234571",
            "birth_date": datetime(1979, 7, 18).date()
        },
        {
            "username": "olga_spin",
            "email": "olga@fisher.app",
            "full_name": "Ольга Спиннингова",
            "role": "user",
            "phone": "+79991234572",
            "birth_date": datetime(1995, 2, 25).date()
        },
        {
            "username": "sergey_bait",
            "email": "sergey@fisher.app",
            "full_name": "Сергей Наживкин",
            "role": "user",
            "phone": "+79991234573",
            "birth_date": datetime(1983, 9, 30).date()
        }
    ]

    for user_data in demo_users:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            phone=user_data["phone"],
            birth_date=user_data["birth_date"],
            created_at=datetime.utcnow()
        )
        user.set_password("demo123")
        db.session.add(user)

    db.session.commit()
    print(f'Создано {len(demo_users) + 2} пользователей (admin, moderator и {len(demo_users)} демо-пользователей)')

# app/data/relations.py
# Связи между рыбами, снастями и наживками

# Связи рыб и снастей (какие снасти подходят для ловли конкретных видов рыб)
fish_gear_relations = [
    # Вобла
    {'fish_name': 'Вобла', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Вобла', 'gear_name': 'Фидер'},

    # Лещ
    {'fish_name': 'Лещ', 'gear_name': 'Фидер'},
    {'fish_name': 'Лещ', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Лещ', 'gear_name': 'Донка с резинкой'},

    # Судак
    {'fish_name': 'Судак', 'gear_name': 'Спиннинг'},
    {'fish_name': 'Судак', 'gear_name': 'Спиннинг для джига'},
    {'fish_name': 'Судак', 'gear_name': 'Фидер'},

    # Щука
    {'fish_name': 'Щука', 'gear_name': 'Спиннинг'},
    {'fish_name': 'Щука', 'gear_name': 'Зимний жерлица'},
    {'fish_name': 'Щука', 'gear_name': 'Нахлыст'},

    # Сом
    {'fish_name': 'Сом', 'gear_name': 'Карповая снасть'},
    {'fish_name': 'Сом', 'gear_name': 'Донка с резинкой'},
    {'fish_name': 'Сом', 'gear_name': 'Спиннинг'},

    # Сазан
    {'fish_name': 'Сазан', 'gear_name': 'Карповая снасть'},
    {'fish_name': 'Сазан', 'gear_name': 'Фидер'},
    {'fish_name': 'Сазан', 'gear_name': 'Донка с резинкой'},

    # Жерех
    {'fish_name': 'Жерех', 'gear_name': 'Спиннинг'},
    {'fish_name': 'Жерех', 'gear_name': 'Нахлыст'},
    {'fish_name': 'Жерех', 'gear_name': 'Спиннинг для микроджига'},

    # Карась
    {'fish_name': 'Карась', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Карась', 'gear_name': 'Фидер'},
    {'fish_name': 'Карась', 'gear_name': 'Зимняя удочка с кивком'},

    # Красноперка
    {'fish_name': 'Красноперка', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Красноперка', 'gear_name': 'Матчевая удочка'},
    {'fish_name': 'Красноперка', 'gear_name': 'Болоно'},

    # Синец
    {'fish_name': 'Синец', 'gear_name': 'Фидер'},
    {'fish_name': 'Синец', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Синец', 'gear_name': 'Донка с резинкой'},

    # Чехонь
    {'fish_name': 'Чехонь', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Чехонь', 'gear_name': 'Спиннинг для микроджига'},
    {'fish_name': 'Чехонь', 'gear_name': 'Нахлыст'},

    # Кефаль
    {'fish_name': 'Кефаль', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Кефаль', 'gear_name': 'Фидер'},
    {'fish_name': 'Кефаль', 'gear_name': 'Нахлыст'},

    # Килька
    {'fish_name': 'Килька', 'gear_name': 'Спиннинг'},
    {'fish_name': 'Килька', 'gear_name': 'Сеть ставная'},

    # Пузанок
    {'fish_name': 'Пузанок', 'gear_name': 'Спиннинг'},
    {'fish_name': 'Пузанок', 'gear_name': 'Сеть обкидная'},

    # Сельдь
    {'fish_name': 'Сельдь', 'gear_name': 'Сеть ставная'},
    {'fish_name': 'Сельдь', 'gear_name': 'Сеть обкидная'},

    # Запрещенные виды (для справки)
    {'fish_name': 'Белуга', 'gear_name': 'Запрещено'},
    {'fish_name': 'Осетр русский', 'gear_name': 'Запрещено'},
    {'fish_name': 'Севрюга', 'gear_name': 'Запрещено'},

    # Дополнительные виды
    {'fish_name': 'Окунь', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Окунь', 'gear_name': 'Спиннинг'},
    {'fish_name': 'Окунь', 'gear_name': 'Спиннинг для микроджига'},
    {'fish_name': 'Окунь', 'gear_name': 'Зимняя удочка с кивком'},

    {'fish_name': 'Плотва', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Плотва', 'gear_name': 'Фидер'},
    {'fish_name': 'Плотва', 'gear_name': 'Зимняя удочка с кивком'},

    {'fish_name': 'Голавль', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Голавль', 'gear_name': 'Спиннинг'},
    {'fish_name': 'Голавль', 'gear_name': 'Нахлыст'},

    {'fish_name': 'Язь', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Язь', 'gear_name': 'Фидер'},
    {'fish_name': 'Язь', 'gear_name': 'Спиннинг'},

    {'fish_name': 'Ерш', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Ерш', 'gear_name': 'Фидер'},
    {'fish_name': 'Ерш', 'gear_name': 'Зимняя удочка с кивком'},

    {'fish_name': 'Налим', 'gear_name': 'Донка с резинкой'},
    {'fish_name': 'Налим', 'gear_name': 'Зимний жерлица'},
    {'fish_name': 'Налим', 'gear_name': 'Спиннинг'},

    {'fish_name': 'Уклейка', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Уклейка', 'gear_name': 'Спиннинг для микроджига'},

    {'fish_name': 'Пескарь', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Пескарь', 'gear_name': 'Фидер'},

    {'fish_name': 'Густера', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Густера', 'gear_name': 'Фидер'},

    {'fish_name': 'Подлещик', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Подлещик', 'gear_name': 'Фидер'},

    {'fish_name': 'Белоглазка', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Белоглазка', 'gear_name': 'Фидер'},

    {'fish_name': 'Сом солдатов', 'gear_name': 'Донка с резинкой'},
    {'fish_name': 'Сом солдатов', 'gear_name': 'Спиннинг'},

    {'fish_name': 'Угорь', 'gear_name': 'Донка с резинкой'},
    {'fish_name': 'Угорь', 'gear_name': 'Спиннинг'},

    {'fish_name': 'Стерлядь', 'gear_name': 'Донка с резинкой'},
    {'fish_name': 'Стерлядь', 'gear_name': 'Фидер'},

    {'fish_name': 'Хариус', 'gear_name': 'Нахлыст'},
    {'fish_name': 'Хариус', 'gear_name': 'Спиннинг для микроджига'},

    {'fish_name': 'Форель ручьевая', 'gear_name': 'Нахлыст'},
    {'fish_name': 'Форель ручьевая', 'gear_name': 'Спиннинг для микроджига'},

    {'fish_name': 'Ленок', 'gear_name': 'Нахлыст'},
    {'fish_name': 'Ленок', 'gear_name': 'Спиннинг'},

    {'fish_name': 'Таймень', 'gear_name': 'Нахлыст'},
    {'fish_name': 'Таймень', 'gear_name': 'Спиннинг'},

    {'fish_name': 'Голец', 'gear_name': 'Нахлыст'},
    {'fish_name': 'Голец', 'gear_name': 'Спиннинг для микроджига'},

    {'fish_name': 'Сиг', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Сиг', 'gear_name': 'Спиннинг для микроджига'},

    {'fish_name': 'Ряпушка', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Ряпушка', 'gear_name': 'Сеть ставная'},

    {'fish_name': 'Кумжа', 'gear_name': 'Нахлыст'},
    {'fish_name': 'Кумжа', 'gear_name': 'Спиннинг'},

    {'fish_name': 'Минога', 'gear_name': 'Специальные ловушки'},
    {'fish_name': 'Минога', 'gear_name': 'Сеть ставная'},

    {'fish_name': 'Шип', 'gear_name': 'Донка с резинкой'},
    {'fish_name': 'Шип', 'gear_name': 'Сеть ставная'},

    {'fish_name': 'Стерлядь сибирская', 'gear_name': 'Донка с резинкой'},
    {'fish_name': 'Стерлядь сибирская', 'gear_name': 'Фидер'},

    {'fish_name': 'Нельма', 'gear_name': 'Спиннинг'},
    {'fish_name': 'Нельма', 'gear_name': 'Сеть ставная'},

    {'fish_name': 'Омуль', 'gear_name': 'Сеть ставная'},
    {'fish_name': 'Омуль', 'gear_name': 'Поплавочная удочка'},

    {'fish_name': 'Чир', 'gear_name': 'Сеть ставная'},
    {'fish_name': 'Чир', 'gear_name': 'Поплавочная удочка'},

    {'fish_name': 'Муксун', 'gear_name': 'Сеть ставная'},
    {'fish_name': 'Муксун', 'gear_name': 'Поплавочная удочка'},

    {'fish_name': 'Пелядь', 'gear_name': 'Сеть ставная'},
    {'fish_name': 'Пелядь', 'gear_name': 'Поплавочная удочка'},

    {'fish_name': 'Ряпушка сибирская', 'gear_name': 'Сеть ставная'},
    {'fish_name': 'Ряпушка сибирская', 'gear_name': 'Поплавочная удочка'},

    {'fish_name': 'Тугун', 'gear_name': 'Сеть ставная'},
    {'fish_name': 'Тугун', 'gear_name': 'Поплавочная удочка'},

    {'fish_name': 'Валек', 'gear_name': 'Сеть ставная'},
    {'fish_name': 'Валек', 'gear_name': 'Поплавочная удочка'},

    {'fish_name': 'Чивик', 'gear_name': 'Сеть ставная'},
    {'fish_name': 'Чивик', 'gear_name': 'Поплавочная удочка'},

    {'fish_name': 'Пыжьян', 'gear_name': 'Сеть ставная'},
    {'fish_name': 'Пыжьян', 'gear_name': 'Поплавочная удочка'},

    {'fish_name': 'Кунжа', 'gear_name': 'Нахлыст'},
    {'fish_name': 'Кунжа', 'gear_name': 'Спиннинг для микроджига'},

    {'fish_name': 'Налим малый', 'gear_name': 'Донка с резинкой'},
    {'fish_name': 'Налим малый', 'gear_name': 'Зимний жерлица'},

    {'fish_name': 'Щиповка', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Щиповка', 'gear_name': 'Фидер'},

    {'fish_name': 'Вьюн', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Вьюн', 'gear_name': 'Донка с резинкой'},

    {'fish_name': 'Усач', 'gear_name': 'Фидер'},
    {'fish_name': 'Усач', 'gear_name': 'Донка с резинкой'},

    {'fish_name': 'Жерех малый', 'gear_name': 'Спиннинг'},
    {'fish_name': 'Жерех малый', 'gear_name': 'Нахлыст'},

    {'fish_name': 'Линь', 'gear_name': 'Поплавочная удочка'},
    {'fish_name': 'Линь', 'gear_name': 'Фидер'},

    {'fish_name': 'Карп зеркальный', 'gear_name': 'Карповая снасть'},
    {'fish_name': 'Карп зеркальный', 'gear_name': 'Фидер'},

    {'fish_name': 'Карп голый', 'gear_name': 'Карповая снасть'},
    {'fish_name': 'Карп голый', 'gear_name': 'Фидер'},

    {'fish_name': 'Карп чешуйчатый', 'gear_name': 'Карповая снасть'},
    {'fish_name': 'Карп чешуйчатый', 'gear_name': 'Фидер'}
]

# Связи рыб и наживок (какие наживки лучше всего подходят для ловли конкретных видов рыб)
fish_bait_relations = [
    # Вобла
    {'fish_name': 'Вобла', 'bait_name': 'Опарыш'},
    {'fish_name': 'Вобла', 'bait_name': 'Мотыль'},
    {'fish_name': 'Вобла', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Вобла', 'bait_name': 'Кукуруза'},
    {'fish_name': 'Вобла', 'bait_name': 'Тесто'},

    # Лещ
    {'fish_name': 'Лещ', 'bait_name': 'Червь выползок'},
    {'fish_name': 'Лещ', 'bait_name': 'Опарыш'},
    {'fish_name': 'Лещ', 'bait_name': 'Мотыль'},
    {'fish_name': 'Лещ', 'bait_name': 'Горох'},
    {'fish_name': 'Лещ', 'bait_name': 'Перловка'},
    {'fish_name': 'Лещ', 'bait_name': 'Кукуруза'},
    {'fish_name': 'Лещ', 'bait_name': 'Пельмени'},

    # Судак
    {'fish_name': 'Судак', 'bait_name': 'Живец плотва'},
    {'fish_name': 'Судак', 'bait_name': 'Живец уклейка'},
    {'fish_name': 'Судак', 'bait_name': 'Силиконовые приманки'},
    {'fish_name': 'Судак', 'bait_name': 'Воблеры'},
    {'fish_name': 'Судак', 'bait_name': 'Блёсны'},
    {'fish_name': 'Судак', 'bait_name': 'Пиявка'},

    # Щука
    {'fish_name': 'Щука', 'bait_name': 'Живец карась'},
    {'fish_name': 'Щука', 'bait_name': 'Живец плотва'},
    {'fish_name': 'Щука', 'bait_name': 'Силиконовые приманки'},
    {'fish_name': 'Щука', 'bait_name': 'Воблеры'},
    {'fish_name': 'Щука', 'bait_name': 'Блёсны'},
    {'fish_name': 'Щука', 'bait_name': 'Поролон'},

    # Сом
    {'fish_name': 'Сом', 'bait_name': 'Червь выползок'},
    {'fish_name': 'Сом', 'bait_name': 'Личинка майского жука'},
    {'fish_name': 'Сом', 'bait_name': 'Живец карась'},
    {'fish_name': 'Сом', 'bait_name': 'Пиявка'},
    {'fish_name': 'Сом', 'bait_name': 'Куриная печень'},
    {'fish_name': 'Сом', 'bait_name': 'Мясо ракушки'},

    # Сазан
    {'fish_name': 'Сазан', 'bait_name': 'Кукуруза'},
    {'fish_name': 'Сазан', 'bait_name': 'Горох'},
    {'fish_name': 'Сазан', 'bait_name': 'Перловка'},
    {'fish_name': 'Сазан', 'bait_name': 'Бойлы'},
    {'fish_name': 'Сазан', 'bait_name': 'Картофель'},
    {'fish_name': 'Сазан', 'bait_name': 'Пшеница'},

    # Жерех
    {'fish_name': 'Жерех', 'bait_name': 'Живец уклейка'},
    {'fish_name': 'Жерех', 'bait_name': 'Силиконовые приманки'},
    {'fish_name': 'Жерех', 'bait_name': 'Воблеры'},
    {'fish_name': 'Жерех', 'bait_name': 'Блёсны'},
    {'fish_name': 'Жерех', 'bait_name': 'Мушки'},

    # Карась
    {'fish_name': 'Карась', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Карась', 'bait_name': 'Опарыш'},
    {'fish_name': 'Карась', 'bait_name': 'Мотыль'},
    {'fish_name': 'Карась', 'bait_name': 'Кукуруза'},
    {'fish_name': 'Карась', 'bait_name': 'Тесто'},
    {'fish_name': 'Карась', 'bait_name': 'Манная болтушка'},
    {'fish_name': 'Карась', 'bait_name': 'Хлеб'},

    # Красноперка
    {'fish_name': 'Красноперка', 'bait_name': 'Опарыш'},
    {'fish_name': 'Красноперка', 'bait_name': 'Мотыль'},
    {'fish_name': 'Красноперка', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Красноперка', 'bait_name': 'Кукуруза'},
    {'fish_name': 'Красноперка', 'bait_name': 'Тесто'},
    {'fish_name': 'Красноперка', 'bait_name': 'Манная болтушка'},

    # Синец
    {'fish_name': 'Синец', 'bait_name': 'Опарыш'},
    {'fish_name': 'Синец', 'bait_name': 'Мотыль'},
    {'fish_name': 'Синец', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Синец', 'bait_name': 'Горох'},
    {'fish_name': 'Синец', 'bait_name': 'Перловка'},

    # Чехонь
    {'fish_name': 'Чехонь', 'bait_name': 'Опарыш'},
    {'fish_name': 'Чехонь', 'bait_name': 'Мотыль'},
    {'fish_name': 'Чехонь', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Чехонь', 'bait_name': 'Силиконовые приманки'},
    {'fish_name': 'Чехонь', 'bait_name': 'Мушки'},

    # Кефаль
    {'fish_name': 'Кефаль', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Кефаль', 'bait_name': 'Опарыш'},
    {'fish_name': 'Кефаль', 'bait_name': 'Кукуруза'},
    {'fish_name': 'Кефаль', 'bait_name': 'Хлеб'},
    {'fish_name': 'Кефаль', 'bait_name': 'Мушки'},

    # Килька
    {'fish_name': 'Килька', 'bait_name': 'Светящиеся приманки'},
    {'fish_name': 'Килька', 'bait_name': 'Мелкие блёсны'},

    # Пузанок
    {'fish_name': 'Пузанок', 'bait_name': 'Мелкие блёсны'},
    {'fish_name': 'Пузанок', 'bait_name': 'Силиконовые приманки'},

    # Сельдь
    {'fish_name': 'Сельдь', 'bait_name': 'Сетные приманки'},
    {'fish_name': 'Сельдь', 'bait_name': 'Светящиеся приманки'},

    # Запрещенные виды (для справки)
    {'fish_name': 'Белуга', 'bait_name': 'Запрещено'},
    {'fish_name': 'Осетр русский', 'bait_name': 'Запрещено'},
    {'fish_name': 'Севрюга', 'bait_name': 'Запрещено'},

    # Дополнительные виды
    {'fish_name': 'Окунь', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Окунь', 'bait_name': 'Опарыш'},
    {'fish_name': 'Окунь', 'bait_name': 'Мотыль'},
    {'fish_name': 'Окунь', 'bait_name': 'Силиконовые приманки'},
    {'fish_name': 'Окунь', 'bait_name': 'Воблеры'},
    {'fish_name': 'Окунь', 'bait_name': 'Блёсны'},

    {'fish_name': 'Плотва', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Плотва', 'bait_name': 'Опарыш'},
    {'fish_name': 'Плотва', 'bait_name': 'Мотыль'},
    {'fish_name': 'Плотва', 'bait_name': 'Кукуруза'},
    {'fish_name': 'Плотва', 'bait_name': 'Тесто'},
    {'fish_name': 'Плотва', 'bait_name': 'Манная болтушка'},

    {'fish_name': 'Голавль', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Голавль', 'bait_name': 'Опарыш'},
    {'fish_name': 'Голавль', 'bait_name': 'Кузнечик'},
    {'fish_name': 'Голавль', 'bait_name': 'Стрекоза'},
    {'fish_name': 'Голавль', 'bait_name': 'Силиконовые приманки'},

    {'fish_name': 'Язь', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Язь', 'bait_name': 'Опарыш'},
    {'fish_name': 'Язь', 'bait_name': 'Кукуруза'},
    {'fish_name': 'Язь', 'bait_name': 'Горох'},
    {'fish_name': 'Язь', 'bait_name': 'Силиконовые приманки'},

    {'fish_name': 'Ерш', 'bait_name': 'Мотыль'},
    {'fish_name': 'Ерш', 'bait_name': 'Опарыш'},
    {'fish_name': 'Ерш', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Ерш', 'bait_name': 'Мормыш'},

    {'fish_name': 'Налим', 'bait_name': 'Живец плотва'},
    {'fish_name': 'Налим', 'bait_name': 'Живец уклейка'},
    {'fish_name': 'Налим', 'bait_name': 'Личинка майского жука'},
    {'fish_name': 'Налим', 'bait_name': 'Куриная печень'},

    {'fish_name': 'Уклейка', 'bait_name': 'Мотыль'},
    {'fish_name': 'Уклейка', 'bait_name': 'Опарыш'},
    {'fish_name': 'Уклейка', 'bait_name': 'Мелкие блёсны'},

    {'fish_name': 'Пескарь', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Пескарь', 'bait_name': 'Опарыш'},
    {'fish_name': 'Пескарь', 'bait_name': 'Мотыль'},

    {'fish_name': 'Густера', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Густера', 'bait_name': 'Опарыш'},
    {'fish_name': 'Густера', 'bait_name': 'Мотыль'},
    {'fish_name': 'Густера', 'bait_name': 'Кукуруза'},

    {'fish_name': 'Подлещик', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Подлещик', 'bait_name': 'Опарыш'},
    {'fish_name': 'Подлещик', 'bait_name': 'Мотыль'},
    {'fish_name': 'Подлещик', 'bait_name': 'Кукуруза'},

    {'fish_name': 'Белоглазка', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Белоглазка', 'bait_name': 'Опарыш'},
    {'fish_name': 'Белоглазка', 'bait_name': 'Мотыль'},
    {'fish_name': 'Белоглазка', 'bait_name': 'Кукуруза'},

    {'fish_name': 'Сом солдатов', 'bait_name': 'Червь выползок'},
    {'fish_name': 'Сом солдатов', 'bait_name': 'Личинка майского жука'},
    {'fish_name': 'Сом солдатов', 'bait_name': 'Живец карась'},

    {'fish_name': 'Угорь', 'bait_name': 'Червь выползок'},
    {'fish_name': 'Угорь', 'bait_name': 'Личинка майского жука'},
    {'fish_name': 'Угорь', 'bait_name': 'Куриная печень'},

    {'fish_name': 'Стерлядь', 'bait_name': 'Червь выползок'},
    {'fish_name': 'Стерлядь', 'bait_name': 'Опарыш'},
    {'fish_name': 'Стерлядь', 'bait_name': 'Мотыль'},

    {'fish_name': 'Хариус', 'bait_name': 'Мушки'},
    {'fish_name': 'Хариус', 'bait_name': 'Силиконовые приманки'},
    {'fish_name': 'Хариус', 'bait_name': 'Ручейник'},

    {'fish_name': 'Форель ручьевая', 'bait_name': 'Мушки'},
    {'fish_name': 'Форель ручьевая', 'bait_name': 'Силиконовые приманки'},
    {'fish_name': 'Форель ручьевая', 'bait_name': 'Ручейник'},

    {'fish_name': 'Ленок', 'bait_name': 'Мушки'},
    {'fish_name': 'Ленок', 'bait_name': 'Силиконовые приманки'},
    {'fish_name': 'Ленок', 'bait_name': 'Воблеры'},

    {'fish_name': 'Таймень', 'bait_name': 'Мушки'},
    {'fish_name': 'Таймень', 'bait_name': 'Воблеры'},
    {'fish_name': 'Таймень', 'bait_name': 'Силиконовые приманки'},

    {'fish_name': 'Голец', 'bait_name': 'Мушки'},
    {'fish_name': 'Голец', 'bait_name': 'Силиконовые приманки'},
    {'fish_name': 'Голец', 'bait_name': 'Воблеры'},

    {'fish_name': 'Сиг', 'bait_name': 'Мотыль'},
    {'fish_name': 'Сиг', 'bait_name': 'Опарыш'},
    {'fish_name': 'Сиг', 'bait_name': 'Червь навозный'},

    {'fish_name': 'Ряпушка', 'bait_name': 'Мотыль'},
    {'fish_name': 'Ряпушка', 'bait_name': 'Опарыш'},

    {'fish_name': 'Кумжа', 'bait_name': 'Мушки'},
    {'fish_name': 'Кумжа', 'bait_name': 'Силиконовые приманки'},
    {'fish_name': 'Кумжа', 'bait_name': 'Воблеры'},

    {'fish_name': 'Минога', 'bait_name': 'Специальные ловушки'},

    {'fish_name': 'Шип', 'bait_name': 'Червь выползок'},
    {'fish_name': 'Шип', 'bait_name': 'Личинка майского жука'},

    {'fish_name': 'Стерлядь сибирская', 'bait_name': 'Червь выползок'},
    {'fish_name': 'Стерлядь сибирская', 'bait_name': 'Опарыш'},

    {'fish_name': 'Нельма', 'bait_name': 'Силиконовые приманки'},
    {'fish_name': 'Нельма', 'bait_name': 'Воблеры'},

    {'fish_name': 'Омуль', 'bait_name': 'Мотыль'},
    {'fish_name': 'Омуль', 'bait_name': 'Опарыш'},

    {'fish_name': 'Чир', 'bait_name': 'Мотыль'},
    {'fish_name': 'Чир', 'bait_name': 'Опарыш'},

    {'fish_name': 'Муксун', 'bait_name': 'Мотыль'},
    {'fish_name': 'Муксун', 'bait_name': 'Опарыш'},

    {'fish_name': 'Пелядь', 'bait_name': 'Мотыль'},
    {'fish_name': 'Пелядь', 'bait_name': 'Опарыш'},

    {'fish_name': 'Ряпушка сибирская', 'bait_name': 'Мотыль'},
    {'fish_name': 'Ряпушка сибирская', 'bait_name': 'Опарыш'},

    {'fish_name': 'Тугун', 'bait_name': 'Мотыль'},
    {'fish_name': 'Тугун', 'bait_name': 'Опарыш'},

    {'fish_name': 'Валек', 'bait_name': 'Мотыль'},
    {'fish_name': 'Валек', 'bait_name': 'Опарыш'},

    {'fish_name': 'Чивик', 'bait_name': 'Мотыль'},
    {'fish_name': 'Чивик', 'bait_name': 'Опарыш'},

    {'fish_name': 'Пыжьян', 'bait_name': 'Мотыль'},
    {'fish_name': 'Пыжьян', 'bait_name': 'Опарыш'},

    {'fish_name': 'Кунжа', 'bait_name': 'Мушки'},
    {'fish_name': 'Кунжа', 'bait_name': 'Силиконовые приманки'},

    {'fish_name': 'Налим малый', 'bait_name': 'Живец плотва'},
    {'fish_name': 'Налим малый', 'bait_name': 'Личинка майского жука'},

    {'fish_name': 'Щиповка', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Щиповка', 'bait_name': 'Мотыль'},

    {'fish_name': 'Вьюн', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Вьюн', 'bait_name': 'Опарыш'},

    {'fish_name': 'Усач', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Усач', 'bait_name': 'Опарыш'},
    {'fish_name': 'Усач', 'bait_name': 'Кукуруза'},

    {'fish_name': 'Жерех малый', 'bait_name': 'Живец уклейка'},
    {'fish_name': 'Жерех малый', 'bait_name': 'Силиконовые приманки'},

    {'fish_name': 'Линь', 'bait_name': 'Червь навозный'},
    {'fish_name': 'Линь', 'bait_name': 'Опарыш'},
    {'fish_name': 'Линь', 'bait_name': 'Кукуруза'},
    {'fish_name': 'Линь', 'bait_name': 'Тесто'},

    {'fish_name': 'Карп зеркальный', 'bait_name': 'Кукуруза'},
    {'fish_name': 'Карп зеркальный', 'bait_name': 'Бойлы'},
    {'fish_name': 'Карп зеркальный', 'bait_name': 'Горох'},

    {'fish_name': 'Карп голый', 'bait_name': 'Кукуруза'},
    {'fish_name': 'Карп голый', 'bait_name': 'Бойлы'},
    {'fish_name': 'Карп голый', 'bait_name': 'Горох'},

    {'fish_name': 'Карп чешуйчатый', 'bait_name': 'Кукуруза'},
    {'fish_name': 'Карп чешуйчатый', 'bait_name': 'Бойлы'},
    {'fish_name': 'Карп чешуйчатый', 'bait_name': 'Горох'}
]

# Связи снастей и наживок (какие наживки используются с конкретными снастями)
gear_bait_relations = [
    # Поплавочные удочки
    {'gear_name': 'Поплавочная удочка', 'bait_name': 'Червь навозный'},
    {'gear_name': 'Поплавочная удочка', 'bait_name': 'Червь выползок'},
    {'gear_name': 'Поплавочная удочка', 'bait_name': 'Опарыш'},
    {'gear_name': 'Поплавочная удочка', 'bait_name': 'Мотыль'},
    {'gear_name': 'Поплавочная удочка', 'bait_name': 'Кукуруза'},
    {'gear_name': 'Поплавочная удочка', 'bait_name': 'Горох'},
    {'gear_name': 'Поплавочная удочка', 'bait_name': 'Перловка'},
    {'gear_name': 'Поплавочная удочка', 'bait_name': 'Тесто'},
    {'gear_name': 'Поплавочная удочка', 'bait_name': 'Манная болтушка'},
    {'gear_name': 'Поплавочная удочка', 'bait_name': 'Хлеб'},

    # Спиннинговые снасти
    {'gear_name': 'Спиннинг', 'bait_name': 'Силиконовые приманки'},
    {'gear_name': 'Спиннинг', 'bait_name': 'Воблеры'},
    {'gear_name': 'Спиннинг', 'bait_name': 'Блёсны'},
    {'gear_name': 'Спиннинг', 'bait_name': 'Живец плотва'},
    {'gear_name': 'Спиннинг', 'bait_name': 'Живец карась'},
    {'gear_name': 'Спиннинг', 'bait_name': 'Живец уклейка'},
    {'gear_name': 'Спиннинг', 'bait_name': 'Пиявка'},
    {'gear_name': 'Спиннинг', 'bait_name': 'Поролон'},
    {'gear_name': 'Спиннинг', 'bait_name': 'Резина'},
    {'gear_name': 'Спиннинг', 'bait_name': 'Пластик'},

    # Фидерные снасти
    {'gear_name': 'Фидер', 'bait_name': 'Червь навозный'},
    {'gear_name': 'Фидер', 'bait_name': 'Червь выползок'},
    {'gear_name': 'Фидер', 'bait_name': 'Опарыш'},
    {'gear_name': 'Фидер', 'bait_name': 'Мотыль'},
    {'gear_name': 'Фидер', 'bait_name': 'Кукуруза'},
    {'gear_name': 'Фидер', 'bait_name': 'Горох'},
    {'gear_name': 'Фидер', 'bait_name': 'Перловка'},
    {'gear_name': 'Фидер', 'bait_name': 'Бойлы'},
    {'gear_name': 'Фидер', 'bait_name': 'Картофель'},
    {'gear_name': 'Фидер', 'bait_name': 'Пшеница'},

    # Зимние снасти
    {'gear_name': 'Зимняя удочка с кивком', 'bait_name': 'Мотыль'},
    {'gear_name': 'Зимняя удочка с кивком', 'bait_name': 'Опарыш'},
    {'gear_name': 'Зимняя удочка с кивком', 'bait_name': 'Мормыш'},
    {'gear_name': 'Зимняя удочка с кивком', 'bait_name': 'Червь навозный'},
    {'gear_name': 'Зимний жерлица', 'bait_name': 'Живец плотва'},
    {'gear_name': 'Зимний жерлица', 'bait_name': 'Живец карась'},
    {'gear_name': 'Зимний жерлица', 'bait_name': 'Живец уклейка'},

    # Нахлыст
    {'gear_name': 'Нахлыст', 'bait_name': 'Мушки'},
    {'gear_name': 'Нахлыст', 'bait_name': 'Силиконовые приманки'},
    {'gear_name': 'Нахлыст', 'bait_name': 'Воблеры'},

    # Карповые снасти
    {'gear_name': 'Карповая снасть', 'bait_name': 'Бойлы'},
    {'gear_name': 'Карповая снасть', 'bait_name': 'Кукуруза'},
    {'gear_name': 'Карповая снасть', 'bait_name': 'Горох'},
    {'gear_name': 'Карповая снасть', 'bait_name': 'Картофель'},
    {'gear_name': 'Карповая снасть', 'bait_name': 'Пшеница'},
    {'gear_name': 'Карповая снасть', 'bait_name': 'Куриная печень'},
    {'gear_name': 'Карповая снасть', 'bait_name': 'Сыр'},
    {'gear_name': 'Карповая снасть', 'bait_name': 'Колбаса'},

    # Донные снасти
    {'gear_name': 'Донка с резинкой', 'bait_name': 'Червь навозный'},
    {'gear_name': 'Донка с резинкой', 'bait_name': 'Червь выползок'},
    {'gear_name': 'Донка с резинкой', 'bait_name': 'Опарыш'},
    {'gear_name': 'Донка с резинкой', 'bait_name': 'Мотыль'},
    {'gear_name': 'Донка с резинкой', 'bait_name': 'Кукуруза'},
    {'gear_name': 'Донка с резинкой', 'bait_name': 'Горох'},
    {'gear_name': 'Донка с резинкой', 'bait_name': 'Перловка'},
    {'gear_name': 'Донка с резинкой', 'bait_name': 'Картофель'},
    {'gear_name': 'Донка с резинкой', 'bait_name': 'Пшеница'},
    {'gear_name': 'Донка с резинкой', 'bait_name': 'Куриная печень'}
]

# Функции для создания связей в базе данных (оставлены без изменений)
def create_fish_gear_relations(fish_objs, gear_objs, db):
    """Создает связи между рыбами и снастями в базе данных"""
    from ..models import FishGear

    # Создать словарь для быстрого поиска снастей по имени
    gear_dict = {gear.name: gear for gear in gear_objs}

    for relation in fish_gear_relations:
        fish_name = relation['fish_name']
        gear_name = relation['gear_name']

        # Найти рыбу и снасть по имени
        fish = next((f for f in fish_objs if f.name == fish_name), None)
        gear = gear_dict.get(gear_name)

        if fish and gear:
            # Создать связь
            relation_obj = FishGear(fish_id=fish.id, gear_id=gear.id)
            db.session.add(relation_obj)

    db.session.commit()
    print(f'Создано {len(fish_gear_relations)} связей рыба-снасть')

def create_fish_bait_relations(fish_objs, bait_objs, db):
    """Создает связи между рыбами и наживками в базе данных"""
    from ..models import FishBait

    # Создать словарь для быстрого поиска наживок по имени
    bait_dict = {bait.name: bait for bait in bait_objs}

    for relation in fish_bait_relations:
        fish_name = relation['fish_name']
        bait_name = relation['bait_name']

        # Найти рыбу и наживку по имени
        fish = next((f for f in fish_objs if f.name == fish_name), None)
        bait = bait_dict.get(bait_name)

        if fish and bait:
            # Создать связь
            relation_obj = FishBait(fish_id=fish.id, bait_id=bait.id)
            db.session.add(relation_obj)

    db.session.commit()
    print(f'Создано {len(fish_bait_relations)} связей рыба-наживка')

def create_waterbody_fish_relations(waterbodies_list, fish_objs, db):
    """Создает связи между водоемами и рыбами в базе данных"""
    from ..models import WaterbodyFish

    # Если нет водоемов, создать базовые связи
    if not waterbodies_list:
        print('Нет водоёмов для создания связей')
        return

    # Создать связи для каждого водоема с основными видами рыб
    common_fish_names = ['Вобла', 'Лещ', 'Судак', 'Щука', 'Сазан', 'Карась']

    for waterbody in waterbodies_list:
        for fish_name in common_fish_names:
            fish = next((f for f in fish_objs if f.name == fish_name), None)
            if fish:
                relation_obj = WaterbodyFish(waterbody_id=waterbody.id, fish_id=fish.id)
                db.session.add(relation_obj)

    db.session.commit()
    print(f'Создано связей водоём-рыба для {len(waterbodies_list)} водоёмов')
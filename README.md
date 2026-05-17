# PC Build Manager

Веб-застосунок для керування клієнтами, збірками ПК, комплектуючими та замовленнями.

Проєкт побудований на `Flask` і використовує багаторівневу архітектуру:
- `web` — маршрути, контролери, форми, рендеринг
- `services` — бізнес-логіка
- `repositories` — доступ до MySQL
- `infrastructure` — підключення до БД

## Можливості

- дашборд із загальною статистикою
- повний CRUD для клієнтів
- повний CRUD для збірок ПК
- повний CRUD для замовлень
- повний CRUD для комплектуючих
- preview збірки та замовлення
- inline-валідація форм
- regex-валідація телефону та email
- кастомні сторінки помилок `404` і `500`
- модульний frontend на vanilla JavaScript
- unit/integration тести
- Docker і `docker-compose`

## Швидкий старт

### 1. Встановлення залежностей

```powershell
py -m pip install -r requirements.txt
```

### 2. Налаштування змінних середовища

Створіть `.env` на основі `.env.example`:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=lab7
APP_SECRET_KEY=change-me
APP_HOST=127.0.0.1
APP_PORT=5000
FLASK_DEBUG=0
```

### 3. Підготовка бази даних

Виконайте SQL-скрипт:

```powershell
mysql -u root -p < init_db.sql
```

### 4. Запуск

```powershell
py main.py
```

Після запуску відкрийте:

```text
http://127.0.0.1:5000/
```

## Документація

- [Технічна документація](</e:/якість та тестування пз/project/testing-software-project/docs/TECHNICAL_DOCUMENTATION.md>)
- [Керівництво користувача](</e:/якість та тестування пз/project/testing-software-project/docs/USER_GUIDE.md>)
- [Довідник маршрутів і сценаріїв](</e:/якість та тестування пз/project/testing-software-project/docs/API_AND_ROUTES.md>)
- [Супровід і експлуатація](</e:/якість та тестування пз/project/testing-software-project/docs/OPERATIONS_AND_MAINTENANCE.md>)
- [Словник бази даних](</e:/якість та тестування пз/project/testing-software-project/docs/DATABASE_DICTIONARY.md>)
- [Стратегія тестування](</e:/якість та тестування пз/project/testing-software-project/docs/TESTING_STRATEGY.md>)
- [Архітектурні рішення](</e:/якість та тестування пз/project/testing-software-project/docs/ARCHITECTURE_DECISIONS.md>)
- [Безпека і валідація](</e:/якість та тестування пз/project/testing-software-project/docs/SECURITY_AND_VALIDATION.md>)

## Що читати в першу чергу

Якщо документація потрібна для різних ролей, зручно рухатись так:

- для викладача або рев'юера: `README.md` -> `TECHNICAL_DOCUMENTATION.md` -> `DATABASE_DICTIONARY.md`
- для користувача системи: `README.md` -> `USER_GUIDE.md`
- для розробника, який буде продовжувати роботу: `TECHNICAL_DOCUMENTATION.md` -> `API_AND_ROUTES.md` -> `TESTING_STRATEGY.md` -> `OPERATIONS_AND_MAINTENANCE.md`
- для архітектурного рев'ю: `TECHNICAL_DOCUMENTATION.md` -> `ARCHITECTURE_DECISIONS.md` -> `DATABASE_DICTIONARY.md`
- для перевірки безпеки вводу і конфігурації: `SECURITY_AND_VALIDATION.md`
- для швидкої перевірки вимог: `USER_GUIDE.md` і розділи про UX, валідацію та помилки в `TECHNICAL_DOCUMENTATION.md`

## Покриття вимог

Система закриває ключові бізнес- та технічні вимоги:

- веб-інтерфейс замість консольного режиму
- відсутність hardcoded паролів у коді
- dropdown-вибір компонентів і статусів
- оформлення замовлення без ручного введення ID
- серверна і клієнтська валідація критичних полів
- кастомні сторінки помилок `404` і `500`
- повний CRUD для основних сутностей
- багаторівнева архітектура
- модульний frontend
- базове unit та integration test coverage
- контейнеризація через Docker

## Коротка карта сутностей

У предметній області є чотири головні групи даних:

1. `Клієнти`
Користувачі, які оформлюють замовлення. Для них зберігаються ім'я, прізвище, дата народження, телефон та email.

2. `Комплектуючі`
Каталог апаратних компонентів: GPU, CPU, материнські плати, RAM, блоки живлення, корпуси.

3. `Збірки ПК`
Підсумкові конфігурації, які складаються з шести категорій комплектуючих і мають тип та загальну вартість.

4. `Замовлення`
Зв'язують клієнта і збірку, містять статуси оплати та готовності, суму до сплати, дату створення і розрахований виробничий час.

## Тестування

```powershell
py -m pytest -q
```

Очікуваний результат:

```text
23 passed
```

Примітка: у цьому середовищі `pytest` може показувати попередження про неможливість створити `.pytest_cache`. Це не впливає на проходження тестів.

## Docker

```powershell
docker-compose up --build
```

## Структура проєкту

```text
app/
  infrastructure/
  repositories/
  services/
  static/
  templates/
  web/
tests/
main.py
init_db.sql
docker-compose.yaml
Dockerfile
```

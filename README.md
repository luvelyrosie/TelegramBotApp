# TeamTasks: Веб-приложение и Telegram-бот

## О проекте

Это веб-приложение и Telegram-бот для управления задачами в команде. Пользователи могут создавать списки задач, назначать исполнителей и сроки, отслеживать прогресс и получать уведомления. Telegram-бот позволяет:

* Просматривать свои задачи: `/mytasks`
* Отмечать задачи как выполненные: `/done <id>`
* Привязывать аккаунт к боту: `/bind <код>`

Telegram-бот: **[@TeamTasksHelperBot](https://t.me/TeamTasksHelperBot)**

## Быстрый старт (через Docker)

1. Склонируйте репозиторий:

```bash
git clone https://github.com/luvelyrosie/TelegramBotApp.git
cd TelegramBotApp
```

2. Соберите Docker-контейнеры:

```bash
docker-compose build
```

3. Запустите контейнеры:

```bash
docker-compose up -d
```

4. Примените миграции и создайте суперпользователя:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

5. Откройте веб-приложение:
   Перейдите на `http://localhost:8000`, зарегистрируйтесь и войдите.

6. Привяжите Telegram-бота:
   На главной странице будет **Bind Code**. В Telegram отправьте:

```
/bind <код>
```

7. Использование бота:

* `/start` — приветствие и инструкция
* `/bind <код>` — привязка аккаунта
* `/mytasks` — показать задачи
* `/done <id>` — отметить задачу выполненной
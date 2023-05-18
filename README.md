# Foodgram

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, 
добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать список продуктов, 
необходимых для приготовления одного или нескольких выбранных блюд.

![yamdb workflow](https://github.com/Ludmila-Glushkova/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# Стэк технологий

- Python
- Django Rest Framework
- Postgres
- PostgreSQL
- Docker
- nginx
- Github Actions

# Запуск проекта в контейнере

Клонировать репозиторий:

```
git clone git@github.com:Ludmila-Glushkova/foodgram-project-react.git
```

Перейти в папку с файлом docker-compose.yaml:

```
cd infra
```
Создать и запустить контейнеры Docker:
```
sudo docker-compose up -d
```

После успешной сборки выполнить миграции:
```
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate
```

Создать суперпользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

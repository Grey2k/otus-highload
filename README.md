# About

Репозиторий содержит домашние работы по курсу "Архитектор высоких нагрузок"

## Запуск проекта

```
cp .env.example .env
docker-compose up -d
```

## Миграции

```
docker-compose exec social-network bash
cd app
flask migrate
```

## Сиды

```
docker-compose exec social-network bash
cd app
flask seed
```


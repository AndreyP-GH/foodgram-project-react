![example workflow](https://github.com/AndreyP-GH/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?event=push)


# IP боевого сервера для проверки деплоя: 158.160.61.6  

# practicum_new_diploma  

# Cайт Foodgram, «Продуктовый помощник».  

Онлайн-сервис, где пользователи могут публиковать рецепты,  подписываться на публикации других пользователей, добавлять  понравившиеся рецепты в список «Избранное», а перед походом в магазин  скачивать сводный список продуктов, необходимых для приготовления  одного или нескольких выбранных блюд.  

##  шаблон наполнения .env-файла. Располагается в foodgram-project-react/infra/.env:  
    DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql  
    DB_NAME=postgres # имя базы данных  
    POSTGRES_USER=postgres # логин для подключения к базе данных  
    POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)  
    DB_HOST=db # название сервиса (контейнера)  
    DB_PORT=5432 # порт для подключения к БД  


## запуск приложения в контейнерах. Команды выполняются последовательно из директории foodgram-project-react/infra/:  
    - *запускаем docker-compose*:  
        docker-compose up -d --build  
    - *выполняем миграции*:  
        docker-compose exec backend python manage.py migrate  
    - *подтягиваем базу данных с несколькими пользователями и рецептами*:  
        docker-compose exec backend python manage.py loaddata dump.json  
    - *подтягиваем статику*:  
        docker-compose exec backend python manage.py collectstatic --no-input  
    - *после работы с API проекта, останавливаем и удаляем контейнеры (образы останутся)*:  
        docker-compose down -v  


## автор:  
Печников Андрей  

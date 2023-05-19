import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Скрипт для импорта тестовых данных/ингредиентов в БД из csv-файла'

    def handle(self, *args, **options):
        with open('../../data/ingredients.csv',
                  encoding='utf-8') as fixture:
            reader = csv.reader(fixture)
            for row in reader:
                name, measurement_unit = row
                Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit)
        print('Скрипт выполнен. Данные импортированы')

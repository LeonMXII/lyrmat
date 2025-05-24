import csv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from django.utils.dateparse import parse_date

from shop.models import Supplier, Category, Manufacturer, Product


class Command(BaseCommand):
    help = 'Загрузка товаров из CSV-файла'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='D:\\PyCharm\\Final_project\\lyrmat\\products.csv')

    def handle(self, *args, **kwargs):
        file_path = kwargs['csv_file']
        #user = User.objects.first()


        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                name = row['name'].strip()
                description = row['description'].strip()
                category_name = row['category'].strip()
                manufacturer_name = row['manufacturer'].strip()
                price = float(row['price'])
                is_lte_enabled = row['is_lte_enabled'].strip().lower() == 'true'
                release_date = row['release_date'].strip()

                category, _ = Category.objects.get_or_create(name=category_name)

                manufacturer, _ = Manufacturer.objects.get_or_create(name=manufacturer_name)

                user, _ = User.objects.get_or_create(username=manufacturer_name.lower())

                supplier, _ = Supplier.objects.get_or_create(
                    user=user,
                    defaults={'company_name': manufacturer_name}
                )

                product, created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        'description': description,
                        'category': category,
                        'manufacturer': manufacturer,
                        'price': price,
                        'is_lte_enabled': is_lte_enabled,
                        'release_date': release_date
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Добавлен продукт: {name}"))
                else:
                    self.stdout.write(f"Продукт уже существует: {name}")

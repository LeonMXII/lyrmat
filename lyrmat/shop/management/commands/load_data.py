import csv
from django.core.management.base import BaseCommand

from django.utils.dateparse import parse_date

from shop.models import Category, Manufacturer, Product



class Command(BaseCommand):
    help = 'Загрузка товаров из CSV-файла'

    def handle(self, *args, **kwargs):
        file_path = 'products.csv'

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                category, _ = Category.objects.get_or_create(name=row['category'])
                manufacturer, _ = Manufacturer.objects.get_or_create(name=row['manufacturer'])

                product, created = Product.objects.get_or_create(
                    name=row['name'],
                    defaults={
                        'description': row['description'],
                        'category': category,
                        'manufacturer': manufacturer,
                        'price': row['price'],
                        'is_lte_enabled': row['is_lte_enabled'].lower() == 'true',
                        'release_date': parse_date(row['release_date']),
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Добавлен продукт: {product.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Продукт уже существует: {product.name}"))

import csv
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date
from shop.models import Supplier, Product, SupplierInvoice, SupplierInvoiceItem, Order

class Command(BaseCommand):
    help = 'Загрузка накладных из invoice.csv'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='D:\\PyCharm\\Final_project\\lyrmat\\invoice.csv')

    def handle(self, *args, **kwargs):
        file_path = kwargs['csv_file']
        user = User.objects.first()

        if not user:
            self.stdout.write(self.style.ERROR('Нет пользователей в системе. Создайте пользователя.'))
            return

        order = Order.objects.first()
        if not order:
            self.stdout.write(self.style.ERROR('Нет ни одного заказа. Создайте заказ перед загрузкой накладных.'))
            return

        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                supplier_name = row['поставщик']
                supplier, _ = Supplier.objects.get_or_create(
                    company_name=supplier_name,
                    defaults={
                        'user': user,
                        'contact_email': f"{supplier_name.lower()}@example.com"
                    }
                )

                try:
                    product = Product.objects.get(name=row['товар'])
                except Product.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Продукт не найден: {row['товар']}"))
                    continue

                invoice, created = SupplierInvoice.objects.get_or_create(
                    supplier=supplier,
                    order=order,
                    defaults={
                        'file': ContentFile(b'Temporary invoice content', name='temp.txt'),
                        'confirmed': False
                    }
                )

                SupplierInvoiceItem.objects.update_or_create(
                    invoice=invoice,
                    product=product,
                    defaults={
                        'quantity': int(row['количество']),
                        'unit_price': float(row['закупочная_цена']),
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Создана накладная: {row['номер_накладной']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Накладная уже существует: {row['номер_накладной']}"))

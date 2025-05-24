# Lyrmat — онлайн-магазин игровых ПК и консолей

Проект Lyrmat — это backend-приложение для онлайн-магазина, в котором реализованы:

- регистрация и аутентификация пользователей 
- каталог товаров
- корзина
- оформление заказа
- история заказов
- редактирование статуса заказов администраторами

## Установка и запуск

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/LeonMXII/lyrmat.git
cd lyrmat


### 2. Создайте виртуальное окружение

python -m venv venv
source venv/bin/activate  
Windows: venv\Scripts\activate

### 3. Установите зависимости

pip install -r requirements.txt

### 4. Примените миграции и создайте суперпользователя

python manage.py migrate
python manage.py createsuperuser

### 5. Загрузите данные из CSV

python manage.py load_data products.csv

### 6. Запустите сервер

python manage.py runserver

### 7. Создайте заказ перед загрузкой накладных

python manage.py load_invoices invoice.csv


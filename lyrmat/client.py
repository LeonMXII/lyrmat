import requests

# Регистрация пользователя

# base_url = 'http://localhost:8000/api/'
#
# register_data = {
#     "username": "customer1",
#     "password": "pass123456",
#     "email": "customer1@example.com",
#     "role": "customer"
# }
#
# response = requests.post(f"{base_url}register/", json=register_data)
#
# print(f"Status code: {response.status_code}")
# print(f"Response text: {response.text}")






# Использую токен customer1

# token = "3c4245154bb0cf19af85c6d0437dd678c86f7fd1"
# headers = {
#     "Authorization": f"Token {token}",
#     "Content-Type": "application/json"}



# Получение списка товаров

# url = "http://127.0.0.1:8000/api/products/"
# response = requests.get(url, headers=headers)
#
# print("Status Code:", response.status_code)
# print("Response:", response.json())


# Получение деталей конкретного товара

# product_id = 2
# url = f"http://127.0.0.1:8000/api/products/{product_id}/"
# response = requests.get(url, headers=headers)
#
# print("Status Code:", response.status_code)
# print("Response:", response.json())


# Добавление товара в корзину

# url = "http://127.0.0.1:8000/api/cart/add/"
# data = {
#     "product_id": 2,
#     "quantity": 1
# }
# response = requests.post(url, headers=headers, json=data)
#
# print("Status Code:", response.status_code)
# print("Response:", response.json() if response.status_code == 200 else response.text)


# Удаление товара

# url = "http://127.0.0.1:8000/api/cart/remove/"
# data = {
#     "product_id": 2
# }
# response = requests.post(url, headers=headers, json=data)
#
# print("Status Code:", response.status_code)
# print("Response:", response.json() if response.status_code == 200 else response.text)


# Подтверждение заказа

# url = "http://127.0.0.1:8000/api/cart/confirm/"
# response = requests.post(url, headers=headers)
#
# print("Status Code:", response.status_code)
# print("Response:", response.json() if response.status_code == 200 else response.text)


# Подтверждение заказа и отправка email

# url = 'http://localhost:8000/api/cart/confirm/'
# headers = {'Authorization': f'Token {token}',}
#
# response = requests.post(url, headers=headers)
#
# if response.status_code == 200:
#     print("Заказ подтверждён и email отправлен!")
# else:
#     print(f"Ошибка: {response.status_code}")
#     print(response.json())
#


# Добавление адреса доставки
# url = "http://127.0.0.1:8000/api/cart/address/add/"
# data = {
#     "shipping_address": "ул. Ленина, д. 10",
#     "city": "Москва",
#     "postal_code": "123456"
# }
#
# response = requests.post(url, headers=headers, json=data)
# print("Status Code:", response.status_code)
# print("Response:", response.json())


# Удаление адреса доставки

# url = "http://127.0.0.1:8000/api/cart/address/remove/"
# response = requests.post(url, headers=headers)
# print("Status Code:", response.status_code)
# print("Response:", response.json())


# Получение списка заказов
# url = "http://127.0.0.1:8000/api/orders/"
# response = requests.get(url, headers=headers)
#
# print("Status Code:", response.status_code)
# print("Response:", response.json()
#


# Получение деталей заказа
# order_id = 4
# url = f"http://127.0.0.1:8000/api/orders/{order_id}/"
# response = requests.get(url, headers=headers)
#
# print("Status Code:", response.status_code)
# print("Response:", response.json())


# Обновление статуса заказа для админа
# admin_token = ""
# admin_headers = {
#     "Authorization": f"Token {admin_token}",
#     "Content-Type": "application/json"}
#
# url = "http://127.0.0.1:8000/api/orders/1/status/"
# data = {
#     "is_paid": True}
#
# response = requests.post(url, headers=admin_headers, json=data)
#
# print("Status Code:", response.status_code)
# print("Response:", response.json())




# Проверка доступа (для обычного пользователя)

# url = "http://127.0.0.1:8000/api/supplier-orders/"
# response = requests.get(url, headers=headers)
# print("Статус (не поставщик):", response.status_code)
# print("Ответ:", response.json())


# Регистрация поставщика

# url = "http://127.0.0.1:8000/api/register/"
# data = {
#     "username": "supplier_1",
#     "email": "supplier@example.com",
#     "password": "123456",
#     "role": "supplier"
# }
#
# response = requests.post(url, json=data)
# print("Status Code:", response.status_code)
# print("Response:", response.json())


# Проверка доступа (supplier_1)

# url = "http://127.0.0.1:8000/api/supplier-orders/"
#
# supplier_token = ""
# supplier_headers = {
#     "Authorization": f"Token {supplier_token}",
#     "Content-Type": "application/json"}
#
# response = requests.get(url, headers=supplier_headers)
# print("Статус (поставщик):", response.status_code)
# print("Ответ:", response.json())



# admin_token = ""
# admin_headers = {
#     "Authorization": f"Token {admin_token}",
#     "Content-Type": "application/json"}
#
# url = "http://127.0.0.1:8000/api/orders/1/status/"
# data = {"is_paid": True}
#
# response = requests.post(url, headers=admin_headers, json=data)
# print("Status Code:", response.status_code)
# print("Response:", response.json())









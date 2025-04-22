import requests

# Регистрация пользователя
# url = "http://127.0.0.1:8000/api/register/"
# data = {
#     "username": "user_3",
#     "email": "user2@gmal.com",
#     "password": "123456"
# }
#
# response = requests.post(url, json=data)
#
# print("Status Code:", response.status_code)
# print("Response:", response.json())



# Использую токен user_3

token = "c849616cdfd91edb06730feb4aa5763571ab3122"
headers = {
    "Authorization": f"Token {token}",
    "Content-Type": "application/json"}



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
admin_token = ""
admin_headers = {
    "Authorization": f"Token {admin_token}",
    "Content-Type": "application/json"}

url = "http://127.0.0.1:8000/api/orders/1/status/"
data = {
    "is_paid": True}

response = requests.post(url, headers=admin_headers, json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())











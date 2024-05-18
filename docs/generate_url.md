# Url yaratish

Payme ning to'lov qismiga foydalanuvchini yuborish uchun, URL ni yaratib olishimiz kerak bo'ladi

> Namuna
![alt text](https://imgur.com/IE0yV4Z.jpg)

```python
from clickuz import ClickUz

url = ClickUz.generate_url(order_id='123456789',amount='100000')
print(url)
```
Agar client to'lo'v qilib bo'lganidan kegin, saytingizga qaytib kelishini hohlasangiz, `return_url` ga o'zingizdagi URL ni qo'shib qo'yishingiz kerak bo'ladi

```python
from clickuz import ClickUz

url = ClickUz.generate_url(order_id='123456789', amount='100000', return_url='http://example.com')
print(url)
```
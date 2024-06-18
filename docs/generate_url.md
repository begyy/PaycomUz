# Url yaratish

Payme ning to'lov qismiga foydalanuvchini yuborish uchun, URL ni yaratib olishimiz kerak bo'ladi

> Namuna
![alt text](https://imgur.com/IE0yV4Z.jpg)

```python
from paycomuz import Paycom

paycom = Paycom()

url = paycom.create_initialization(amount=100000, order_id='123456789', return_url='https://example.com/success/')
print(url)
```
Amountni berayotganimizda, summani ohiriga ikkta 0 qo'yishimiz kerak bo'ladi, chunki Payme kelayotgan summani tiyinda hisoblaydi.

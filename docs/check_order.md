# Buyurtmani tekshirsh

Payme tamonidan bizga buyurtma (order) haqida ma'lumot kelganida, biz uni database orqali tekshirib, va uning natijasiga mos javob qaytarishimiz kerak bo'ladi. 

Batafsil: [https://developer.help.paycom.uz/protokol-merchant-api/skhema-vzaimodeystviya](https://developer.help.paycom.uz/protokol-merchant-api/skhema-vzaimodeystviya)


## Order model
Orderlarni saqlash uchun yangi model yaratib olamiz

### models.py
```python
class Order(models.Model):
    """Order model"""

    order_no = models.CharField(max_length=150)
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return f"id: {self.id}"
    
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
```

## CheckOrder
Ushbu qismda payme dan kelayotgan malumotlar tekshiriladi, account ni ichida kelayotgan order_id ni ishlatgan holda, database dan ushbu order ni statusini qaytaramiz

### views.py
```python
from paycomuz.views import MerchantAPIView
from paycomuz import Paycom
from django.urls import path

class CheckOrder(Paycom):
    def check_order(self, amount: int, account: dict, *args, **kwargs):
        order = Order.objects.filter(order_no=account["order_id"], is_finished=False).first()

        if not order:
            return self.ORDER_NOT_FOND
        if order.product.price * 100 != amount:
            return self.INVALID_AMOUNT
        
        return self.ORDER_FOUND
        
   def successfully_payment(self, account: dict, transaction, *args, **kwargs):
        order = Order.objects.filter(order_no=transaction.order_key).first()

        if not order:
            return self.ORDER_NOT_FOND
        
        order.is_finished = True
        order.save()

   def cancel_payment(self, account, transaction, *args, **kwargs):
        print(account)
      

class TestView(MerchantAPIView):
    VALIDATE_CLASS = CheckOrder
```
Payment successful bo'lgan holatda, is_finished = True ga o'zgartirib qo'yildi.

Payme status_code larini, ushbu havola orqali tanishib chiqishingiz mumkin: [https://developer.help.paycom.uz/metody-merchant-api/oshibki-errors/](https://developer.help.paycom.uz/metody-merchant-api/oshibki-errors/)

### urls.py
```python
from django.urls import path

urlpatterns = [
    path('payme/', TestView.as_view())
]
```

Endi bularning hammasini test qilish uchun, payme ning sandbox platformasi orqali tekshirishingiz kerak bo'ladi: [https://test.paycom.uz/instruction](https://test.paycom.uz/instruction)

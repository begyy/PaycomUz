# Ishni boshlash

Kerakli modullarni o'rnatib olganimizdan so'ng, keling ishni boshlasak. Avval `settings.py` ga o'tib, quyidagi ma'lumotlarni kiritib olamiz

### settings.py
```python
PAYCOM_SETTINGS = {
    "KASSA_ID": "KASSA_ID",  # token
    "SECRET_KEY": "TEST_KEY OR PRODUCTION_KEY",  # password
    "ACCOUNTS": {
        "KEY": "order_id"
    }
}

INSTALLED_APPS = [
    'rest_framework',
    'paycomuz',
    ...
]
```
> `KASSA_ID` va `SECRET_KEY` ma'lumotlarini Payme hodimlari taqdim etishadi

Va undan so'ng database ni migrate qilib olamiz
```
python manage.py migrate
```

Payme userini yaratib olamiz, bu Payme dan kelayotgan requestlarni authorize qilish uchun kerak bo'ladi
```
python manage.py create_paycom_user
```

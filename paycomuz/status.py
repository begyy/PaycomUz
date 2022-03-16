ORDER_NOT_FOUND = -31050
TRANSACTION_NOT_FOUND = -31003
UNABLE_TO_PERFORM_OPERATION = -31008
INVALID_AMOUNT = -31001
ORDER_FOUND = 200

CREATE_TRANSACTION = 1
CLOSE_TRANSACTION = 2
CANCEL_TRANSACTION_CODE = -1
PERFORM_CANCELED_CODE = -2
ORDER_NOT_FOND_MESSAGE = {
    "uz": "Buyurtma topilmadi",
    "ru": "Заказ не найден",
    "en": "Order not fond"
}
TRANSACTION_NOT_FOUND_MESSAGE = {
    "uz": "Tranzaksiya topilmadi",
    "ru": "Транзакция не найдена",
    "en": "Transaction not found"
}
UNABLE_TO_PERFORM_OPERATION_MESSAGE = {
    "uz": "Ushbu amalni bajarib bo'lmaydi",
    "ru": "Невозможно выполнить данную операцию",
    "en": "Unable to perform operation"
}
INVALID_AMOUNT_MESSAGE = {
    "uz": "Miqdori notog'ri",
    "ru": "Неверная сумма",
    "en": "Invalid amount"
}

AUTH_ERROR = {
    "error": {
        "code": -32504,
        "message": {
            "ru": "пользователь не существует",
            "uz": "foydalanuvchi mavjud emas",
            "en": "user does not exist"
        },
        "data": "user does not exist"
    }
}

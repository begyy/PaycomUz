from .methods_subscribe_api import PayComResponse


class Paycom(PayComResponse):
    ORDER_FOUND = 200
    ORDER_NOT_FOND = -31050
    INVALID_AMOUNT = -31001

    def check_order(self, amount, account, *args, **kwargs):
        """
        >>> self.check_order(amount=amount, account=account)
        """
        pass

    def successfully_payment(self, account, transaction, *args, **kwargs):
        """
        >>> self.successfully_payment(account=account, transaction=transaction)
        """
        pass

    def cancel_payment(self, account, transaction, *args, **kwargs):
        """
        >>> self.cancel_payment(account=account,transaction=transaction)
        """
        pass

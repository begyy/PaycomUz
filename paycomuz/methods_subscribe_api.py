import requests
from django.conf import settings
import base64
from decimal import Decimal

assert settings.PAYCOM_SETTINGS.get('PAYCOM_ENV') != None
assert settings.PAYCOM_SETTINGS.get('TOKEN') != None
assert settings.PAYCOM_SETTINGS.get('ACCOUNTS') != None
assert settings.PAYCOM_SETTINGS['ACCOUNTS'].get('KEY_1') != None

PAYCOM_ENV = settings.PAYCOM_SETTINGS['PAYCOM_ENV']
TOKEN = settings.PAYCOM_SETTINGS['TOKEN']
AUTHORIZATION = {'X-Auth': settings.PAYCOM_SETTINGS['TOKEN']}
KEY_1 = settings.PAYCOM_SETTINGS['ACCOUNTS']['KEY_1']
KEY_2 = settings.PAYCOM_SETTINGS['ACCOUNTS'].get('KEY_2', 'order_type')

RECEIPTS_CREATE = 'receipts.create'
RECEIPTS_PAY = 'receipts.pay'
CARDS_CREATE = 'cards.create'
CARDS_GET_VERIFY_CODE = 'cards.get_verify_code'
CARD_VERIFY = 'cards.verify'


class Response(object):
    TEST_URL = 'https://checkout.test.paycom.uz/api'
    PRODUCTION_URL = 'https://checkout.paycom.uz/api'
    INITIALIZATION_URL = 'https://checkout.paycom.uz/'
    TEST_INITIALIZATION_URL = 'https://checkout.test.paycom.uz'
    URL = PRODUCTION_URL if PAYCOM_ENV else TEST_URL
    LINK = INITIALIZATION_URL if PAYCOM_ENV else TEST_INITIALIZATION_URL

    def create_transaction(self, token, order_id, amount, order_type=None) -> dict:
        """

        documentation : https://help.paycom.uz/ru/metody-subscribe-api/receipts.create
        documentation : https://help.paycom.uz/ru/metody-subscribe-api/receipts.pay


        >>> self.create_transaction(token='token', order_id=1, amount=5000.00)
        """
        data = dict(
            method=RECEIPTS_CREATE,
            params=dict(
                amount=amount * 100,
                account={
                    KEY_1: order_id,
                    KEY_2: order_type
                }
            )
        )
        response = requests.post(
            url=self.URL,
            json=data,
            headers=AUTHORIZATION
        )
        result = response.json()

        if 'error' in result:
            return result

        data = dict(
            method=RECEIPTS_PAY,
            params=dict(
                id=result['result']['receipt']['_id'],
                token=token
            )
        )

        response = requests.post(url=self.URL, json=data, headers=AUTHORIZATION)
        return response.json()

    def create_initialization(self, amount: Decimal, order_id: str, return_url: str, order_type: str = None) -> str:
        """

        documentation : https://help.paycom.uz/ru/initsializatsiya-platezhey/otpravka-cheka-po-metodu-get

        >>> self.create_initialization(amount=Decimal(5000.00), order_id='1', return_url='https://example.com/success/')
        """

        params = f"m={TOKEN};ac.{KEY_1}={order_id};a={amount};c={return_url}"
        if order_type:
            params += f"ac.{KEY_2}"
        encode_params = base64.b64encode(params.encode("utf-8"))
        encode_params = str(encode_params, 'utf-8')
        url = f"{self.LINK}/{encode_params}"
        return url

    def create_cards(self, card_number, expire, amount, save=False) -> dict:
        '''
        documentation : https://help.paycom.uz/ru/metody-subscribe-api/cards.create
        '''
        data = dict(
            method=CARDS_CREATE,
            params=dict(
                card=dict(number=card_number, expire=expire),
                amount=amount,
                save=save
            )
        )

        response = requests.post(url=self.URL, json=data, headers=AUTHORIZATION)
        result = response.json()
        if 'error' in result:
            return result

        token = result['result']['card']['token']
        result = self.cards_get_verify_code(token=token)
        return result

    def cards_get_verify_code(self, token) -> dict:
        '''
        documentation : https://help.paycom.uz/ru/metody-subscribe-api/cards.get_verify_code
        '''
        data = dict(
            method=CARDS_GET_VERIFY_CODE,
            params=dict(token=token)
        )
        response = requests.post(url=self.URL, json=data, headers=AUTHORIZATION)
        result = response.json()
        result.update(token=token)

        return result

    def cards_verify(self, code, token):
        '''
        documentation : https://help.paycom.uz/ru/metody-subscribe-api/cards.verify
        '''
        data = dict(
            method=CARD_VERIFY,
            params=dict(
                token=token,
                code=code
            )
        )

        response = requests.post(url=self.URL, json=data, headers=AUTHORIZATION)
        return response.json()


class Paycom(Response):
    ORDER_FOUND = 200
    ORDER_NOT_FOND = -31050
    INVALID_AMOUNT = -31001

    def check_order(self, amount, account):
        """
        >>> self.check_order(amount=amount, account=account)
        """

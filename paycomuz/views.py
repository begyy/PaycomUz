# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication

# django
from django.conf import settings
from django.utils.timezone import datetime

# project
from .models import Transaction
from .serializers.payme_operation import PaycomOperationSerialzer
from .status import *


class MerchantAPIView(APIView):
    CHECK_PERFORM_TRANSACTION = 'CheckPerformTransaction'
    CREATE_TRANSACTION = 'CreateTransaction'
    PERFORM_TRANSACTION = 'PerformTransaction'
    ACCOUNTS = settings.PAYCOM_SETTINGS['ACCOUNTS']
    http_method_names = ['post']
    authentication_classes = [BasicAuthentication]
    VALIDATE_CLASS = None
    reply = None

    def __init__(self):
        self.METHODS = {
            self.CHECK_PERFORM_TRANSACTION: self.check_perform_transaction,
            self.CREATE_TRANSACTION: self.create_transaction,
            self.PERFORM_TRANSACTION: self.perform_transaction
        }
        self.REPLY_RESPONSE = {
            ORDER_FOUND: self.order_found,
            ORDER_NOT_FOND: self.order_not_found,
            INVALID_AMOUNT: self.invalid_amount
        }
        super(MerchantAPIView, self).__init__()

    def post(self, request):
        serializer = PaycomOperationSerialzer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        method = serializer.validated_data['method']
        self.METHODS[method](serializer.validated_data)

        assert self.reply != None
        return Response(self.reply)

    def check_perform_transaction(self, validated_data):
        """
        >>> self.check_perform_transaction(validated_data)
        """
        assert self.VALIDATE_CLASS != None
        result = self.VALIDATE_CLASS().check_order(**validated_data['params'])
        assert result != None
        self.REPLY_RESPONSE[result](validated_data)

    def create_transaction(self, validated_data):
        """
        >>> self.create_transaction(validated_data)
        """
        check_transaction = Transaction.objects.filter(_id=validated_data['params']['id']).exists()
        if check_transaction:
            check_transaction.update(state=CANCEL_TRANSACTION, status=Transaction.FAILED)

            self.reply = dict(error=dict(
                id=validated_data['id'],
                code=UNABLE_TO_PERFORM_OPERATION,
                message=UNABLE_TO_PERFORM_OPERATION_MESSAGE
            ))
        else:
            obj = Transaction.objects.create(
                request_id=validated_data['id'],
                _id=validated_data['params']['id'],
                amount=validated_data['params']['amount'] / 100,
                account=validated_data['params']['account'],
                state=CREATE_TRANSACTION
            )
            self.reply = dict(result=dict(
                create_time=datetime.now().timestamp(),
                transaction=obj.id,
                state=CREATE_TRANSACTION
            ))

    def perform_transaction(self, validated_data):
        """
        >>> self.perform_transaction(validated_data)
        """
        id = validated_data['params']['id']
        request_id = validated_data['id']
        try:
            obj = Transaction.objects.get(_id=id)
            if obj.state not in [CLOSE_TRANSACTION, CANCEL_TRANSACTION]:
                obj.state = CLOSE_TRANSACTION
                obj.status = Transaction.SUCCESS

                self.reply = dict(result=dict(
                    transaction=obj.id,
                    perform_time=datetime.now().timestamp(),
                    state=CLOSE_TRANSACTION
                ))
            else:
                obj.status = Transaction.FAILED

                self.reply = dict(error=dict(
                    id=request_id,
                    code=UNABLE_TO_PERFORM_OPERATION,
                    message=UNABLE_TO_PERFORM_OPERATION_MESSAGE
                ))
            obj.save()
        except Transaction.DoesNotExist:
            self.reply = dict(error=dict(
                id=request_id,
                code=TRANSACTION_NOT_FOND,
                message=TRANSACTION_NOT_FOND_MESSAGE
            ))

    def order_found(self, validated_data):
        self.reply = dict(result=dict(allow=True))

    def order_not_found(self, validated_data):
        self.reply = dict(error=dict(
            id=validated_data['id'],
            code=ORDER_NOT_FOND,
            message=ORDER_NOT_FOND_MESSAGE
        ))

    def invalid_amount(self, validated_data):
        self.reply = dict(error=dict(
            id=validated_data['id'],
            code=INVALID_AMOUNT,
            message=INVALID_AMOUNT_MESSAGE
        ))

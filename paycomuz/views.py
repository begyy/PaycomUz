# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
# django
from datetime import datetime
from django.conf import settings

# project
from .models import Transaction
from .serializers.payme_operation import PaycomOperationSerialzer
from paycomuz.authentication import authentication
from .status import *
from rest_framework.permissions import AllowAny
from . import Paycom


class MerchantAPIView(APIView):
    permission_classes = [AllowAny]
    CHECK_PERFORM_TRANSACTION = 'CheckPerformTransaction'
    CREATE_TRANSACTION = 'CreateTransaction'
    PERFORM_TRANSACTION = 'PerformTransaction'
    CHECK_TRANSACTION = 'CheckTransaction'
    CANCEL_TRANSACTION = 'CancelTransaction'
    GET_STATEMENT = 'GetStatement'

    http_method_names = ['post']
    authentication_classes = []
    VALIDATE_CLASS: Paycom = None
    reply = None
    ORDER_KEY = KEY = settings.PAYCOM_SETTINGS['ACCOUNTS']['KEY']

    def __init__(self):
        self.METHODS = {
            self.CHECK_PERFORM_TRANSACTION: self.check_perform_transaction,
            self.CREATE_TRANSACTION: self.create_transaction,
            self.PERFORM_TRANSACTION: self.perform_transaction,
            self.CHECK_TRANSACTION: self.check_transaction,
            self.CANCEL_TRANSACTION: self.cancel_transaction,
            self.GET_STATEMENT: self.get_statement
        }

        self.REPLY_RESPONSE = {
            ORDER_FOUND: self.order_found,
            ORDER_NOT_FOUND: self.order_not_found,
            INVALID_AMOUNT: self.invalid_amount
        }

        super(MerchantAPIView, self).__init__()

    def post(self, request):
        check = authentication(request)
        if check is False or not check:
            return Response(AUTH_ERROR)
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
        validate_class: Paycom = self.VALIDATE_CLASS()
        result: int = validate_class.check_order(**validated_data['params'])
        assert result != None
        self.REPLY_RESPONSE[result](validated_data)

    def create_transaction(self, validated_data):
        """
        >>> self.create_transaction(validated_data)
        """
        order_key = validated_data['params']['account'].get(self.ORDER_KEY)
        if not order_key:
            raise serializers.ValidationError(f"{self.ORDER_KEY} required field")

        validate_class: Paycom = self.VALIDATE_CLASS()
        result: int = validate_class.check_order(**validated_data['params'])
        assert result != None
        if result != ORDER_FOUND:
            self.REPLY_RESPONSE[result](validated_data)
            return

        _id = validated_data['params']['id']
        check_transaction = Transaction.objects.filter(order_key=order_key).order_by('-id')
        if check_transaction.exists():
            transaction = check_transaction.first()
            if transaction.status != Transaction.CANCELED and transaction._id == _id:
                self.reply = dict(result=dict(
                    create_time=int(transaction.created_datetime),
                    transaction=str(transaction.id),
                    state=CREATE_TRANSACTION
                ))

            elif transaction.status == Transaction.PROCESSING:
                self.reply = dict(
                    id=validated_data['id'],
                    error=dict(
                        code=ON_PROCESS,
                        message=dict(
                            uz="Buyurtma to'lo'vi hozirda amalga oshirilmoqda",
                            ru="Платеж на этот заказ на данный момент в процессе",
                            en="Payment for this order is currently on process"
                        )
                    )
                )

            else:
                self.reply = dict(error=dict(
                    id=validated_data['id'],
                    code=ORDER_NOT_FOUND,
                    message=ORDER_NOT_FOUND_MESSAGE
                ))
        else:
            current_time = datetime.now()
            current_time_to_string = int(round(current_time.timestamp()) * 1000)
            obj = Transaction.objects.create(
                request_id=validated_data['id'],
                _id=validated_data['params']['id'],
                amount=validated_data['params']['amount'] / 100,
                order_key=validated_data['params']['account'][self.ORDER_KEY],
                state=CREATE_TRANSACTION,
                created_datetime=current_time_to_string
            )
            self.reply = dict(result=dict(
                create_time=current_time_to_string,
                transaction=str(obj.id),
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
            if obj.state not in [CANCEL_TRANSACTION_CODE]:
                obj.state = CLOSE_TRANSACTION
                obj.status = Transaction.SUCCESS
                if not obj.perform_datetime:
                    current_time = datetime.now()
                    current_time_to_string = int(round(current_time.timestamp()) * 1000)
                    obj.perform_datetime = current_time_to_string
                    self.VALIDATE_CLASS().successfully_payment(validated_data['params'], obj)

                self.reply = dict(result=dict(
                    transaction=str(obj.id),
                    perform_time=int(obj.perform_datetime),
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
                code=TRANSACTION_NOT_FOUND,
                message=TRANSACTION_NOT_FOUND_MESSAGE
            ))

    def check_transaction(self, validated_data):
        """
        >>> self.check_transaction(validated_data)
        """
        id = validated_data['params']['id']
        request_id = validated_data['id']

        try:
            transaction = Transaction.objects.get(_id=id)
            self.response_check_transaction(transaction)
        except Transaction.DoesNotExist:
            self.reply = dict(error=dict(
                id=request_id,
                code=TRANSACTION_NOT_FOUND,
                message=TRANSACTION_NOT_FOUND_MESSAGE
            ))

    def cancel_transaction(self, validated_data):
        id = validated_data['params']['id']
        reason = validated_data['params']['reason']
        request_id = validated_data['id']

        try:
            transaction = Transaction.objects.get(_id=id)
            if transaction.state == 1:
                transaction.state = CANCEL_TRANSACTION_CODE
            elif transaction.state == 2:
                transaction.state = PERFORM_CANCELED_CODE
                self.VALIDATE_CLASS().cancel_payment(validated_data['params'], transaction)
            transaction.reason = reason
            transaction.status = Transaction.CANCELED

            current_time = datetime.now()
            current_time_to_string = int(round(current_time.timestamp()) * 1000)
            if not transaction.cancel_datetime:
                transaction.cancel_datetime = current_time_to_string
            transaction.save()

            self.response_check_transaction(transaction)
        except Transaction.DoesNotExist:
            self.reply = dict(error=dict(
                id=request_id,
                code=TRANSACTION_NOT_FOUND,
                message=TRANSACTION_NOT_FOUND_MESSAGE
            ))

    def get_statement(self, validated_data):
        from_d = validated_data.get('params').get('from')
        to_d = validated_data.get('params').get('to')

        filtered_transactions = Transaction.objects.filter(
            created_datetime__gte=from_d,
            created_datetime__lte=to_d
        )

        transactions_json = [
            dict(
                id = obj._id,
                time = int(obj.created_datetime),
                amount = obj.amount,
                account = dict(
                    order_id = obj.order_key
                ),
                create_time = int(obj.created_datetime) if obj.created_datetime else 0,
                perform_time = int(obj.perform_datetime) if obj.perform_datetime else 0,
                cancel_time = int(obj.cancel_datetime) if obj.cancel_datetime else 0,
                transaction = obj.request_id,
                state = obj.state,
                reason = obj.reason,
            ) 
            
            for obj in filtered_transactions]

        response = dict(
            result = dict(
                transactions = transactions_json
            )
        )

        self.reply = response

    def order_found(self, validated_data):
        self.reply = dict(result=dict(allow=True))

    def order_not_found(self, validated_data):
        self.reply = dict(error=dict(
            id=validated_data['id'],
            code=ORDER_NOT_FOUND,
            message=ORDER_NOT_FOUND_MESSAGE
        ))

    def invalid_amount(self, validated_data):
        self.reply = dict(error=dict(
            id=validated_data['id'],
            code=INVALID_AMOUNT,
            message=INVALID_AMOUNT_MESSAGE
        ))

    def response_check_transaction(self, transaction: Transaction):
        self.reply = dict(result=dict(
            create_time=int(transaction.created_datetime) if transaction.created_datetime else 0,
            perform_time=int(transaction.perform_datetime) if transaction.perform_datetime else 0,
            cancel_time=int(transaction.cancel_datetime) if transaction.cancel_datetime else 0,
            transaction=str(transaction.id),
            state=transaction.state,
            reason=transaction.reason
        ))

from rest_framework import serializers


class PaycomOperationSerialzer(serializers.Serializer):
    CHECK_PERFORM_TRANSACTION = 'CheckPerformTransaction'
    CREATE_TRANSACTION = 'CreateTransaction'
    PERFORM_TRANSACTION = 'PerformTransaction'
    METHODS = (
        (CHECK_PERFORM_TRANSACTION, CHECK_PERFORM_TRANSACTION),
        (CREATE_TRANSACTION, CREATE_TRANSACTION),
        (PERFORM_TRANSACTION, PERFORM_TRANSACTION)
    )
    id = serializers.IntegerField()
    method = serializers.ChoiceField(choices=METHODS)
    params = serializers.JSONField()

from django.db import models


class Transaction(models.Model):
    PROCESSING = 'processing'
    SUCCESS = 'success'
    FAILED = 'failed'
    STATUS = (
        (PROCESSING, 'processing'),
        (SUCCESS, 'success'),
        (FAILED, 'failed')
    )

    _id = models.CharField(max_length=255)
    request_id = models.IntegerField()
    account = models.TextField(max_length=255, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    state = models.IntegerField(blank=True, null=True)
    status = models.CharField(choices=STATUS, default='processing', max_length=55)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"

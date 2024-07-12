#!python3
# -*- codding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class Bond(models.Model):
    class PaymentFrequency(models.TextChoices):
        DAILY = "D", 'Daily'
        WEEKLY = "W", 'Weekly'
        MONTHLY = "M", 'Monthly'
        YEARLY = "Y", 'Yearly'

    isin: models.CharField = models.CharField(max_length=12, unique=True)
    emmision_name: models.CharField = models.CharField(max_length=180)
    value: models.FloatField = models.FloatField()
    interest: models.FloatField = models.FloatField()
    purchase_date: models.DateTimeField = models.DateTimeField()
    maturity_date: models.DateTimeField = models.DateTimeField()
    interest_payment_frequency: models.CharField = models.CharField(
        max_length=1, choices=PaymentFrequency.choices)
    user: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.emmision_name

    @staticmethod
    def get_attributes(cls) -> list[str]:
        field_list = []
        for field in cls._meta.fields:
            if field.name not in ("id", "isin", "user"):
                field_list.append(field.name)
        return field_list

#!python3
# -*- codding: utf-8 -*-

# todo/todo_api/serializers.py
from rest_framework import serializers
from bonds_api.models import Bond


class ChoiceField(serializers.ChoiceField):

    def to_representation(self, obj):
        if obj == "" and self.allow_blank:
            return obj
        result = self._choices.get(obj)
        if not result:
            return "Undefined"
        return result

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == "" and self.allow_blank:
            return ""

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)


class BondSerializer(serializers.ModelSerializer):
    interest_payment_frequency = ChoiceField(
        choices=Bond.PaymentFrequency.choices)

    class Meta:
        model = Bond
        fields = ["emmision_name", "isin", "value", "interest",
                  "purchase_date", "maturity_date", "user",
                  "interest_payment_frequency"]

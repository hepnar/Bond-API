#!python3
# -*- codding: utf-8 -*-

import requests

from settings import CDCP_URL
from datetime import datetime
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from bonds_api.models import Bond
from typing import Dict, Any

import logging

logger = logging.getLogger(__name__)


class PermissionDeniedException(Exception):
    """
        Custom exception for permission denied
    """
    def __init__(self, *args, **kwargs):
        self.message = "Permission denied"
        super().__init__(*args, **kwargs)


class InvalidAttributeException(Exception):
    """
        Custom exception for invalid attribute
    """
    def __init__(self, message, *args, **kwargs):
        self.message = message
        super().__init__(*args, **kwargs)


def custom_exception_handler(exc: Exception, context: dict) -> Response:
    """
        Custom exception handler
    """
    if isinstance(exc, PermissionDeniedException):
        logger.info(exc.message)
        return Response(exc.message, status=status.HTTP_403_FORBIDDEN)

    if isinstance(exc, InvalidAttributeException):
        logger.info(exc.message)
        return Response(exc.message, status=status.HTTP_400_BAD_REQUEST)

    response = exception_handler(exc, context)
    return response


def check_attributes(data: Dict[str, Any], bond: Bond = None,
                     update: bool = False) -> Dict[str, Any]:
    """
        Check if the attributes are valid
        parametr update determines if all attributes are required
    """
    res = {}

    # chenck if bond name
    emmision_name = data.get("emmision_name")
    if not update or emmision_name is not None:
        res["emmision_name"] = emmision_name

    # check if purchase date is valid
    purchase_dt = data.get("purchase_date")
    if not update or purchase_dt is not None:
        try:
            res["purchase_date"] = datetime.strptime(purchase_dt,
                                                     "%Y-%m-%dT%H:%M:%S%z")
        except ValueError as e:
            raise InvalidAttributeException(
                "Invalid purchase date: %s" % str(e))
    else:
        res["purchase_date"] = bond.purchase_date

    # check if maturity date is valid
    maturity_dt = data.get("maturity_date")
    if not update or maturity_dt is not None:
        try:
            res["maturity_date"] = datetime.strptime(maturity_dt,
                                                     "%Y-%m-%dT%H:%M:%S%z")
        except ValueError as e:
            raise InvalidAttributeException(
                "Invalid maturity date: %s" % str(e))
    else:
        res["maturity_date"] = bond.maturity_date

    # check if value is valid
    value = data.get("value")
    if not update or value is not None:
        try:
            res["value"] = float(value)
            if value < 0:
                raise InvalidAttributeException(
                    "Invalid value: value must be greater than 0")
        except ValueError as e:
            raise InvalidAttributeException(
                "Invalid value: %s is not a number" % str(e))

    # check if interest is valid number
    # interest can be negative
    interest = data.get("interest")
    if not update or interest is not None:
        try:
            res["interest"] = float(interest)
        except ValueError as e:
            raise InvalidAttributeException(
                "Invalid interest: %s is not a number" % str(e))

    # check if ISIN code is valid
    isin = data.get("isin")
    if not update or isin is not None:
        url = CDCP_URL + isin
        # validate aginst CDCP
        result = requests.request("GET", url)
        if result.status_code != 200:
            logger.warning("ISIN code %s is not valid: %s", isin, result.text)
            raise InvalidAttributeException("Invalid ISIN code")
        res["isin"] = isin

    # check if interest payment frequency is valid
    # valid values are D, W, M, Y, Daily, Weekly, Monthly, Yearly
    if_to_check = data.get("interest_payment_frequency")
    if not update or if_to_check is not None:
        if_to_check = if_to_check.upper()
        choices_dict = dict(Bond.PaymentFrequency.choices)
        if if_to_check in choices_dict:
            interest_frequency = choices_dict[if_to_check]
        elif if_to_check in Bond.PaymentFrequency.names:
            interest_frequency = data.get("interest_payment_frequency")
        else:
            raise InvalidAttributeException(
                "Invalid interest payment frequency")

        res["interest_frequency"] = interest_frequency

    # check if maturity date is greater than purchase date
    if res["purchase_date"] > res["maturity_date"]:
        raise InvalidAttributeException(
            "Maturity date must be greater than purchase date")

    return res


def get_number_of_payments(start_date: datetime, end_date: datetime,
                           frequency: str) -> int:
    """
    Calculate the number of payments between start and end date
    """
    if frequency == "D":
        return (end_date - start_date).days
    elif frequency == "W":
        return (end_date - start_date).days // 7
    elif frequency == "M":
        return (end_date.year - start_date.year) * 12 + \
            end_date.month - start_date.month
    elif frequency == "Y":
        return end_date.year - start_date.year
    else:
        return 0


def check_permisions(user: Any, user_id: int) -> None:
    """
    Check if the user has permissions to access the data
    """
    if user_id == user.id:
        return
    elif user.is_staff:
        return
    elif user.is_superuser:
        return

    raise PermissionDeniedException()

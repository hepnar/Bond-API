#!python3
# -*- codding: utf-8 -*-


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework import permissions
from bonds_api.models import Bond
from bonds_api.serializers import BondSerializer
from bonds_api.utils import check_attributes
from bonds_api.utils import check_permisions
from bonds_api.utils import get_number_of_payments

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(openapi.Info(
      title="Bond API",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),)

class BondListApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        """
        List all the bonds items for loged user
        ---
        Params:
            None
        Return:
            {
                list [
                    sturuct bond_data   - bond information viz post method
                ]
                status_code             - status code
                status                  - status message
            }
        """
        bond_list = Bond.objects.filter(user=request.user.id)
        serializer = BondSerializer(bond_list, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """
        Create the Bond with given json data
        ---
        Params:
            {
                str emmision_name               - Name of emision
                str isin                        - ISIN [12 characters]
                float value                     - value of bond
                float interest                  - interest of bond
                str purchase_date               - date of purchase
                                                  YYYY-MM-DDTHH:MM:SSZ
                str maturity_date               - date of maturity
                                                  YYYY-MM-DDTHH:MM:SSZ
                str interest_payment_frequency  - frequency of interest payment
                                                  Posible values: D, W, M, Y or
                                                  Daily, Weekly,...
            }
        Return:
            {
                sturuct bond_data       - data of new bond
                status_code             - status code
                                          201 - bond created
                                          400 - bad request mor info in status
                                                message
                status                  - status message
            }

        Exaple of request data:
            {"emmision_name": "Bond Valid ISIN",
             "isin": "CZ0003551251",
             "value": 10.0,
             "interest": 2.9,
             "purchase_date": "2024-06-16T12:00:00Z",
             "maturity_date": "2044-06-16T12:00:00Z",
             "user": 1,
             "interest_payment_frequency": "Yearly"}

        """

        data = check_attributes(request.data)

        data = {"emmision_name": data["emmision_name"],
                "isin": data["isin"],
                "value": data["value"],
                "interest": data["interest"],
                "purchase_date": data["purchase_date"],
                "maturity_date": data["maturity_date"],
                "interest_payment_frequency": data["interest_frequency"],
                "user": request.user.id
                }
        serializer = BondSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BondDetailApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, bond_id: str) -> Response:
        """
        Methods return just one bond with given isin
        ---
        Params:
                str isin                - ISIN
        Return:
            {
                sturuct bond_data       - data of new bond
                status_code             - status code
                                          200 - bond created
                                          403 - Forbidden
                                          404 - Not Found
                status                  - status message
            }

        """
        bond = Bond.objects.filter(user=request.user.id,
                                   isin=bond_id).first()

        if not bond:
            return Response("Bond not found", status=status.HTTP_404_NOT_FOUND)
        check_permisions(request.user, bond.user.id)

        serializer = BondSerializer(bond, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, bond_id: str) -> Response:
        """
        Methods updates some parameters of bond with given isin
        ---
        Params:
            {
                str emmision_name               - Name of emision
                float value                     - value of bond
                float interest                  - interest of bond
                str purchase_date               - date of purchase
                                                  YYYY-MM-DDTHH:MM:SSZ
                str maturity_date               - date of maturity
                                                  YYYY-MM-DDTHH:MM:SSZ
                str interest_payment_frequency  - frequency of interest payment
                                                  Posible values: D, W, M, Y or
                                                  Daily, Weekly,...
            }
        Return:
            {
                sturuct bond_data       - data of new bond
                status_code             - status code
                                          200 - bond created
                                          403 - Forbidden
                                          404 - Not Found
                status                  - status message
            }
        """
        bond = Bond.objects.filter(user=request.user.id,
                                   isin=bond_id).first()
        if not bond:
            return Response("Bond not found", status=status.HTTP_404_NOT_FOUND)

        check_permisions(request.user, bond.user.id)

        attribute_list = Bond.get_attributes(Bond)

        data = check_attributes(request.data, bond, True)

        for key, value in data.items():
            if key in attribute_list:
                setattr(bond, key, value)
            else:
                return Response("Invalid attribute",
                                status=status.HTTP_400_BAD_REQUEST)

        bond.save()
        serializer = BondSerializer(bond, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, bond_id: str) -> Response:
        """
        Methods delte bond with given isin
        ---
        Params:
                str isin                - ISIN
        Rerurn:
            {
                status_code             - status code
                                          200 - bond created
                                          403 - Forbidden
                                          404 - Not Found
                status                  - status message
            }
        """
        bond = Bond.objects.filter(user=request.user.id,
                                   isin=bond_id).first()
        if not bond:
            return Response("Bond not found", status=status.HTTP_404_NOT_FOUND)
        check_permisions(request.user, bond.user.id)
        bond.delete()
        return Response("Bond deleted", status=status.HTTP_200_OK)


class UserDetailApiView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, user_id: int) -> Response:
        """
        Methods some statistics about given user
        ---
        Params:
                int user_id             - user id
        Rerurn:
            {
                sturuct {
                    float avg_interest          - average interest of bonds
                    float future_value          - future value of all bonds
                    float total_value           - total value of all bonds
                    sturuct bond_data           - data of bond with nearest
                                                  maturity date
                }
                status_code             - status code
                                          200 - bond created
                                          403 - Forbidden
                                          404 - Not Found
                status                  - status message
            }
        """
        check_permisions(request.user, user_id)

        bond_list = Bond.objects.filter(user=user_id)
        if not bond_list:
            return Response("User not found", status=status.HTTP_404_NOT_FOUND)

        total_interest = 0
        total_value = 0
        future_value = 0
        next_maturity = None

        for bond in bond_list:
            total_interest += bond.interest
            total_value += bond.value
            if next_maturity is None or \
                    next_maturity.maturity_date > bond.maturity_date:
                next_maturity = bond

            number_of_payments = get_number_of_payments(
                bond.purchase_date, bond.maturity_date,
                bond.interest_payment_frequency)

            future_value += bond.value * (1.0 + bond.interest / 100) ** \
                number_of_payments

        serializer = BondSerializer(next_maturity, many=False)

        data = {"avg_interest": total_interest / len(bond_list),
                "future_value": future_value,
                "total_value": total_value,
                "next_maturity": serializer.data}

        return Response(data, status=status.HTTP_200_OK)

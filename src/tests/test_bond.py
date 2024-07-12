#!python3
# -*- codding: utf-8 -*-

from django.urls import reverse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase
from bonds_api.models import Bond

from unittest.mock import patch


class BondsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("test", "test")
        self.client.force_authenticate(self.user)

    def test_get_bond_list(self):
        """
        Ensure we can retrieve a list of bonds.
        """
        self.test_add_bond()
        response = self.client.get(reverse("bond-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bond.objects.count(), 1)
        self.assertEqual(Bond.objects.get().emmision_name, "Bond Valid ISIN")

    @patch('bonds_api.utils.requests.request')
    def test_add_bond(self, mock_request):
        """
        Ensure we can create a new account object.
        """
        mock_request.return_value.status_code = 200
        data = {"emmision_name": "Bond Valid ISIN",
                "isin": "CZ0003551251",
                "value": 11.5,
                "interest": 2.8,
                "purchase_date": "2024-06-16T12:00:00Z",
                "maturity_date": "2025-06-16T12:00:00Z",
                "interest_payment_frequency": "Yearly",
                }
        response = self.client.post(reverse("bond-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bond.objects.count(), 1)
        self.assertEqual(Bond.objects.get().emmision_name, "Bond Valid ISIN")

    @patch('bonds_api.utils.requests.request')
    def test_add_bond_invalid(self, mock_request):
        """
        Ensure we canot create a new account object with invalid ISIN.
        """
        mock_request.return_value.status_code = 403
        data = {"emmision_name": "Bond Invalid ISIN",
                "isin": "CZ0003551252",
                "value": 11.5,
                "interest": 2.8,
                "purchase_date": "2024-06-16T12:00:00Z",
                "maturity_date": "2025-06-16T12:00:00Z",
                "interest_payment_frequency": "Yearly",
                }

        response = self.client.post(reverse("bond-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Bond.objects.count(), 0)

    def test_get_bond_detail(self):
        """
        Ensure we can get detail of bond.
        """
        self.test_add_bond()
        url = reverse("bond-detail", args=["CZ0003551251"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bond.objects.count(), 1)
        self.assertEqual(Bond.objects.get().emmision_name, "Bond Valid ISIN")

    def test_patch_bond_detail(self):
        """
        Ensure we can update a bond object.
        """
        self.test_add_bond()
        url = reverse("bond-detail", args=["CZ0003551251"])
        data = {"emmision_name": "New name"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bond.objects.count(), 1)
        self.assertEqual(Bond.objects.get().emmision_name, "New name")

    def test_del_bond_detail(self):
        """
        Ensure we can delete a bond object.
        """
        self.test_add_bond()
        url = reverse("bond-detail", args=["CZ0003551251"])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bond.objects.count(), 0)

    def test_get_bond_user_detail(self):
        """
        Ensure we can show user detail.
        """
        self.test_add_bond()
        url = reverse("bond-user-detail", args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Bond.objects.count(), 1)
        self.assertEqual(Bond.objects.get().emmision_name, "Bond Valid ISIN")

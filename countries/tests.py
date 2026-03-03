from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from countries.models import Country

class CountryModelTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        # Initialize country data for tests
        self.country_data = {
            'country': 'Iran',
            'country_code': 'IR'
        }

    def test_create_country(self):
        # Test creating a new country (Happy Path)
        country = Country.objects.create(**self.country_data)
        self.assertEqual(country.country, 'Iran')
        self.assertEqual(country.country_code, 'IR')

    def test_country_str_representation(self):
        # Test string representation of a country
        country = Country.objects.create(**self.country_data)
        self.assertEqual(str(country), 'Iran')

    def test_country_code_max_length(self):
        # Test maximum length of country code (Error Case)
        with self.assertRaises(ValidationError):
            country = Country(country='Test', country_code='XXX')  # Length 3
            country.full_clean()

    def test_blank_fields(self):
        # Test required fields validation (Error Case)
        with self.assertRaises(ValidationError):
            country = Country()
            country.full_clean()
from django.urls import reverse
from django.urls import resolve
from django.test import TestCase
from django.test import Client
from index.views import index
import unittest

class IndexTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view_status_code(self):
        url = reverse('index')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_home_url_resolves_index_view(self):
        view = resolve('/')
        self.assertEquals(view.func, index)

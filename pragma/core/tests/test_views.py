"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: View tests for auth and role separation
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from pragma.core.models import Usuario


class ViewAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="contador", password="testpass123")
        Usuario.objects.create(user=self.user, rol="contador")

        self.admin_user = User.objects.create_user(
            username="adminpanel",
            password="testpass123",
            is_superuser=True,
            is_staff=True,
        )
        Usuario.objects.create(user=self.admin_user, rol="admin")

    def test_admin_panel_requires_login(self):
        response = self.client.get(reverse("admin_panel:admin_facturas"))
        self.assertEqual(response.status_code, 302)

    def test_non_admin_user_gets_forbidden(self):
        self.client.login(username="contador", password="testpass123")
        response = self.client.get(reverse("admin_panel:admin_facturas"))
        self.assertEqual(response.status_code, 403)

    def test_user_dashboard_access_for_authenticated_user(self):
        self.client.login(username="contador", password="testpass123")
        response = self.client.get(reverse("usuario:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_admin_user_can_access_admin_panel(self):
        self.client.login(username="adminpanel", password="testpass123")
        response = self.client.get(reverse("admin_panel:admin_facturas"))
        self.assertEqual(response.status_code, 200)

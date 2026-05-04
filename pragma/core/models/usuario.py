"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Usuario model - extended User profile with role information
"""

from django.db import models
from django.contrib.auth.models import User


class Usuario(models.Model):
    """
    Usuario model extending Django's User with additional role information.
    Used to distinguish between accountants (contador) and administrators.
    """

    ROL_CHOICES = [
        ("contador", "Contador"),
        ("admin", "Administrador"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="Usuario Django",
        help_text="Usuario de autenticación de Django"
    )
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        verbose_name="Rol",
        help_text="Rol del usuario en el sistema"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Actualización"
    )

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"

    def is_admin(self):
        """Check if user has admin role."""
        return self.rol == "admin"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["user__username"]

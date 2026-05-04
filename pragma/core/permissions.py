"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Permission helpers for role-based access control
"""

from django.core.exceptions import PermissionDenied


def require_admin_access(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    perfil = getattr(user, "perfil", None)
    return bool(perfil and perfil.is_admin())


def ensure_admin_or_raise(request):
    if not require_admin_access(request.user):
        raise PermissionDenied("No tienes permisos para acceder a esta sección.")

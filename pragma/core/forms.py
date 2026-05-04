"""
Pragma - Django OCR Invoice Processing System
Author: Pragma Team
Date: 2026-03-18
Description: Forms for user management and admin CRUD flows
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

from pragma.core.models import CertificadoBancario, Cliente, Factura, Usuario


class FacturaUploadForm(forms.Form):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.all(),
        required=False,
        help_text="Opcional: se usa para asociar la factura al cliente."
    )
    archivo = forms.FileField(
        help_text="Sube un archivo PDF, PNG o JPG para extraer datos por OCR.",
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "png", "jpg", "jpeg"])]
    )


class FacturaEditForm(forms.ModelForm):
    archivo = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "png", "jpg", "jpeg"])]
    )

    class Meta:
        model = Factura
        fields = ["numero_factura", "monto", "fecha", "cliente_nit", "cliente", "archivo"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }


class CertificadoBancarioForm(forms.ModelForm):
    archivo = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "png", "jpg", "jpeg"])]
    )

    class Meta:
        model = CertificadoBancario
        fields = [
            "numero_referencia",
            "monto",
            "fecha",
            "cliente_nit",
            "cliente",
            "archivo",
        ]


class UsuarioCreationWithRoleForm(UserCreationForm):
    email = forms.EmailField(required=False)
    rol = forms.ChoiceField(choices=Usuario.ROL_CHOICES)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Usuario.objects.update_or_create(
                user=user,
                defaults={"rol": self.cleaned_data["rol"]},
            )
        return user


class UsuarioRoleUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["rol"]

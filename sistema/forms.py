from django import forms
from django.forms import inlineformset_factory
from .models import Remision, Venta, DetalleVenta


class RemisionForm(forms.ModelForm):
    imagen = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Remision
        fields = ["folio", "cliente", "fecha", "imagen", "observaciones"]
        widgets = {
            "folio": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej. 12345"}),
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Opcional"}),
        }


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["fecha", "descuento", "iva"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "descuento": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "iva": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ["producto", "unidad", "cantidad", "precio_unitario"]
        widgets = {
            "producto": forms.Select(attrs={"class": "form-select"}),
            "unidad": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }


DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    extra=5,          # 5 renglones vacíos por default (puedes subirlo)
    can_delete=True,  # permite borrar líneas
)

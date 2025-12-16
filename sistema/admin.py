from django.contrib import admin
from .models import Cliente, Producto

# --------------------------
# ADMIN CLIENTE
# --------------------------
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "proveedor",
        "comercio",
        "contacto",
        "telefono",
    )
    search_fields = (
        "proveedor",
        "comercio",
        "contacto",
        "telefono",
    )


# --------------------------
# ADMIN PRODUCTO
# --------------------------
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "descripcion",
        "compra_cjs",
        "compra_pzs",
        "venta_cjs",
        "venta_pzs",
    )
    search_fields = (
        "codigo",
        "descripcion",
    )


from django.contrib import admin
from .models import Remision, Venta, DetalleVenta  # ajusto nombres al ver tu models.py


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    autocomplete_fields = ("producto",)  # si tienes muchos productos, esto es oro
    fields = ("producto", "unidad", "cantidad", "precio_unitario", "subtotal")
    readonly_fields = ("subtotal",)


@admin.register(Remision)
class RemisionAdmin(admin.ModelAdmin):
    list_display = ("folio", "cliente", "fecha", "tiene_imagen")
    search_fields = ("folio", "cliente__nombre", "cliente__clave")
    list_filter = ("fecha",)
    date_hierarchy = "fecha"

    def tiene_imagen(self, obj):
        return bool(obj.imagen)
    tiene_imagen.boolean = True
    tiene_imagen.short_description = "Imagen"


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    inlines = [DetalleVentaInline]
    list_display = ("id", "remision", "fecha", "subtotal", "descuento", "iva", "total")
    list_filter = ("fecha",)
    date_hierarchy = "fecha"
    search_fields = ("remision__folio", "remision__cliente__nombre", "remision__cliente__clave")
    readonly_fields = ("subtotal", "total")

    actions = ["recalcular_totales"]

    @admin.action(description="Recalcular totales de ventas seleccionadas")
    def recalcular_totales(self, request, queryset):
        for venta in queryset:
            venta.recalcular_totales(commit=True)


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ("venta", "producto", "unidad", "cantidad", "precio_unitario", "subtotal")
    search_fields = ("venta__remision__folio", "producto__nombre", "producto__clave")
    list_filter = ("unidad",)



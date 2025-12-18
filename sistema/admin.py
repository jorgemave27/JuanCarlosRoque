from django.contrib import admin
from .models import Cliente, Producto, Remision, Venta, DetalleVenta


# --------------------------
# ADMIN CLIENTE
# --------------------------
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("numero", "proveedor", "comercio", "contacto", "telefono")
    search_fields = ("proveedor", "comercio", "contacto", "telefono")


# --------------------------
# ADMIN PRODUCTO
# --------------------------
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descripcion", "compra_cjs", "compra_pzs", "venta_cjs", "venta_pzs")
    search_fields = ("codigo", "descripcion")


# --------------------------
# INLINE DETALLE VENTA
# --------------------------
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    autocomplete_fields = ("producto",)
    fields = ("producto", "unidad", "cantidad", "precio_unitario", "subtotal")
    readonly_fields = ("subtotal",)


# --------------------------
# ADMIN REMISION
# --------------------------
@admin.register(Remision)
class RemisionAdmin(admin.ModelAdmin):
    list_display = ("folio", "cliente", "fecha", "tiene_imagen")
    search_fields = ("folio", "cliente__comercio", "cliente__proveedor")
    list_filter = ("fecha", "cliente")
    date_hierarchy = "fecha"

    def tiene_imagen(self, obj):
        return bool(obj.imagen)
    tiene_imagen.boolean = True
    tiene_imagen.short_description = "Imagen"


# --------------------------
# ADMIN VENTA (con filtro por cliente y búsqueda por producto)
# --------------------------
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    inlines = [DetalleVentaInline]

    list_display = ("id", "fecha", "folio_remision", "cliente", "subtotal", "descuento", "iva", "total")
    list_filter = ("fecha", "remision__cliente")
    date_hierarchy = "fecha"

    search_fields = (
        "remision__folio",
        "remision__cliente__comercio",
        "remision__cliente__proveedor",
        "detalles__producto__codigo",
        "detalles__producto__descripcion",
    )

    autocomplete_fields = ("remision",)
    readonly_fields = ("subtotal", "total")

    actions = ["recalcular_totales"]

    def folio_remision(self, obj):
        return obj.remision.folio
    folio_remision.short_description = "Folio"

    def cliente(self, obj):
        return obj.remision.cliente
    cliente.short_description = "Cliente"

    @admin.action(description="Recalcular totales de ventas seleccionadas")
    def recalcular_totales(self, request, queryset):
        for venta in queryset:
            venta.recalcular_totales(commit=True)


# --------------------------
# ADMIN DETALLE VENTA
# --------------------------
@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ("venta", "producto", "unidad", "cantidad", "precio_unitario", "subtotal")
    list_filter = ("producto", "unidad")
    search_fields = ("venta__remision__folio", "producto__codigo", "producto__descripcion")

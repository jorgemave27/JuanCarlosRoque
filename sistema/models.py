from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal



class Cliente(models.Model):
    numero = models.IntegerField()
    proveedor = models.CharField(max_length=50)
    comercio = models.CharField(max_length=255)
    contacto = models.CharField(max_length=255, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=100, blank=True)
    referencia = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.comercio} ({self.proveedor})"


class Producto(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255)
    compra_cjs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    compra_pzs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    venta_cjs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    venta_pzs = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"


class Remision(models.Model):
    """
    Remisión en papel (evidencia). El 'dueño' de la remisión normalmente es el Cliente.
    Aquí vive la imagen escaneada/foto.
    """
    folio = models.CharField(max_length=50, db_index=True)
    cliente = models.ForeignKey(
        "sistema.Cliente",  # ajusta si tu modelo está en otra app o con otro nombre
        on_delete=models.PROTECT,
        related_name="remisiones",
    )
    fecha = models.DateField(db_index=True)

    # Imagen (o PDF si luego quieres). Por ahora imagen.
    imagen = models.ImageField(
        upload_to="remisiones/%Y/%m/",
        null=True,
        blank=True,
        help_text="Foto/escaneo de la remisión en papel."
    )

    observaciones = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # folio puede repetirse entre clientes, por eso lo atamos a cliente
        constraints = [
            models.UniqueConstraint(
                fields=["cliente", "folio"],
                name="uniq_remision_folio_por_cliente",
            )
        ]
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"Remisión {self.folio} - {self.cliente} ({self.fecha})"


class Venta(models.Model):
    """
    Venta asociada a una remisión.
    La venta tiene líneas (detalle) por producto.
    """
    remision = models.OneToOneField(
        Remision,
        on_delete=models.PROTECT,
        related_name="venta",
        help_text="Una remisión tiene a lo más una venta asociada."
    )

    # si quieres separar fecha de venta vs fecha de remisión:
    fecha = models.DateField(db_index=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    # si después agregas IVA/descuentos:
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    iva = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"Venta #{self.id} ({self.fecha}) - {self.remision.folio}"

    def recalcular_totales(self, commit=True):
        """
        Recalcula subtotal/total sumando sus detalles.
        Útil después de importar Excel o al editar líneas.
        """
        detalles = self.detalles.all()
        subtotal = sum((d.subtotal for d in detalles), Decimal("0.00"))
        self.subtotal = subtotal

        # total = subtotal - descuento + iva
        self.total = (subtotal - self.descuento) + self.iva

        if commit:
            self.save(update_fields=["subtotal", "total", "updated_at"])
        return self.total


class DetalleVenta(models.Model):
    """
    Línea de venta: producto + cantidad + unidad + precio.
    """
    UNIDAD_PAQUETES = "PAQ"
    UNIDAD_PIEZAS = "PZA"
    UNIDAD_CHOICES = [
        (UNIDAD_PAQUETES, "Paquetes"),
        (UNIDAD_PIEZAS, "Piezas"),
    ]

    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    producto = models.ForeignKey(
        "sistema.Producto",  # ajusta a tu modelo real
        on_delete=models.PROTECT,
        related_name="detalles_venta",
    )

    unidad = models.CharField(max_length=3, choices=UNIDAD_CHOICES, default=UNIDAD_PIEZAS)
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
    )

    precio_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        default=Decimal("0.00")
    )

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Evita duplicar el mismo producto 2 veces en la misma venta (si lo prefieres)
            models.UniqueConstraint(
                fields=["venta", "producto", "unidad"],
                name="uniq_producto_unidad_por_venta",
            )
        ]

    def __str__(self):
        return f"{self.producto} x {self.cantidad} ({self.get_unidad_display()})"

    def save(self, *args, **kwargs):
        # Calcula subtotal automáticamente
        self.subtotal = (self.cantidad * self.precio_unitario).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)


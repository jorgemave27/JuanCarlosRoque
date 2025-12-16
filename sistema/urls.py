from django.urls import path
from . import views

app_name = "sistema"

urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # Productos / Clientes
    path("productos/", views.lista_productos, name="lista_productos"),
    path("clientes/", views.lista_clientes, name="lista_clientes"),

    # Importadores
    path("importar/productos/", views.importar_productos, name="importar_productos"),
    path("importar/clientes/", views.importar_clientes, name="importar_clientes"),
    path("importar/remisiones/", views.importar_remisiones_excel, name="importar_remisiones_excel"),

    # Búsqueda
    path("buscar/", views.busqueda_global, name="busqueda"),

    # Remisiones
    path("remisiones/", views.remision_list, name="remision_list"),
    path("remisiones/nueva/", views.remision_create, name="remision_create"),
    path("remisiones/<int:pk>/", views.remision_detail, name="remision_detail"),

    # Ventas
    path("ventas/", views.venta_list, name="venta_list"),
    path("ventas/nueva/<int:remision_id>/", views.venta_create_from_remision, name="venta_create_from_remision"),
    path("ventas/<int:pk>/", views.venta_detail, name="venta_detail"),
    path("ventas/<int:pk>/editar/", views.venta_edit, name="venta_edit"),
]

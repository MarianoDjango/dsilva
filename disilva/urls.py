from django.contrib import admin
from django.contrib.auth import views
from django.urls import path, include
from myapp import views
from django.views.generic.base import RedirectView
from django.contrib.sitemaps.views import sitemap
from myapp.sitemaps import ArticuloSitemap, StaticViewSitemap
sitemaps = {
    'articulos': ArticuloSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='landingindex'),
    path('nosotros/', RedirectView.as_view(url='/#nosotros', permanent=True), name='landingnosotros'),
    path('myapp/', include('myapp.urls')),  # Ruta para la aplicación interna
    path('catalogo/', views.articulos_catalogo, name='catalogo_articulos'),
    path('catalogo/filtrar/', views.filtrar_articulos, name='filtrar_articulos'),
    path('articulo/<int:pk>/', views.articulo_detalle, name='articulo_detalle'),
    path('catalogo/pdf/', views.catalogo_pdf, name='catalogo_pdf'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
]

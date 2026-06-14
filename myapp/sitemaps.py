from django.contrib.sitemaps import Sitemap
from myapp.models import articulos


class ArticuloSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return articulos.objects.filter(idempresa=2, activo=True)

    def location(self, obj):
        return f"/articulo/{obj.pk}/"


class StaticViewSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ['home']

    def location(self, item):
        return '/'
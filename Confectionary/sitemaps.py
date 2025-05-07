from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return [
            'Confectionary:main_page',
            'Confectionary:showcase', 
            'Confectionary:photo_album',
            'Confectionary:custom_cakes',
            'Confectionary:delivery',
            'Confectionary:employees',
        ]

    def location(self, item):
        return reverse(item)
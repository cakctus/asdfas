import auto_info.views as views

from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.base),
    path('general/', views.general, name='general'),

    # apps
    path('cars/', include('cars.urls'), name='cars'),
    path('moto/', include('moto.urls'), name='moto'),


    path('s/', views.search, name='search'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

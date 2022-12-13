from django.urls import path, include
from moto import views

app_name = "moto"

urlpatterns = [
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/<int:brand_id>/models/', views.model_list, name='model_list'),
    path('brands/<int:brand_id>/models/<int:model_id>/modifications', views.modification_list, name='modification_list'),
    path('brands/<int:brand_id>/models/<int:model_id>/modifications/<int:modification_id>/detail', views.modification_detail, name='modification_detail'),
]

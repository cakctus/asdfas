from django.urls import path

from cars import views

app_name = 'cars'

urlpatterns = [
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/<int:brand_id>/models/', views.model_list, name='model_list'),
    path('brands/<int:brand_id>/models/<int:model_id>/generations', views.generation_list, name='generation_list'),
    path('brands/<int:brand_id>/models/<int:model_id>/generations/<int:generation_id>/modifications', views.modification_list, name='modification_list'),
    path('brands/<int:brand_id>/models/<int:model_id>/generations/<int:generation_id>/modifications/<int:modification_id>/detail', views.modification_detail, name='modification_detail'),
]

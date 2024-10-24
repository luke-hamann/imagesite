from django.urls import path

from . import views

urlpatterns = [
    path('', views.tags, name='tags'),
    path('image/<int:image_id>/', views.image, name='image'),
    path('detail/<int:image_id>/', views.detail, name='detail'),
    path('detail/<int:image_id>', views.delete, name='delete'),
    path('search/', views.search, name='search'),
    path('upload/', views.upload, name='upload'),
]

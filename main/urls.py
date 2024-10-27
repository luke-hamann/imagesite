from django.urls import path

from . import views

urlpatterns = [
    path('image/<int:image_id>/', views.image, name='image'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('autocomplete/<str:data>/', views.autocomplete, name='autocomplete'),
    path('', views.tags, name='tags'),
    path('detail/<int:image_id>/', views.detail, name='detail'),
    path('detail/<int:image_id>/<str:slug>/', views.detail, name='detail'),
    path('detail/<int:image_id>/<str:slug>/edit/', views.edit, name='edit'),
    path('detail/<int:image_id>/<str:slug>/delete/', views.delete, name='delete'),
    path('search/', views.search, name='search'),
    path('upload/', views.upload, name='upload'),
]

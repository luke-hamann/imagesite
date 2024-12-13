from django.urls import path
from . import views


# Define the URL routing for the app
urlpatterns = [
    path('', views.search, name='home'),
    path('tags/', views.tags, name='tags'),
    path('upload/', views.upload, name='upload'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('autotag/', views.autotag, name='autotag'),
    path('image/<int:image_id>/', views.image, name='image'),
    path('detail/<int:image_id>/', views.detail, name='detail'),
    path('detail/<int:image_id>/<str:slug>/', views.detail, name='detail'),
    path('detail/<int:image_id>/<str:slug>/edit/', views.edit, name='edit'),
    path('detail/<int:image_id>/<str:slug>/delete/', views.delete, name='delete')
]

from django.urls import path
from . import views

urlpatterns = [
    path('ocr/', views.ocr, name='ocr'),
    path('user_data/', views.user_data, name='user_data'),

]
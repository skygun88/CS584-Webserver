from django.urls import path
from . import views

urlpatterns = [
    path('kakao_ocr/', views.kakao_ocr, name='kakao_ocr'),
    # path('update/', views.update, name='update'),
    # path('cancel/', views.cancel, name='cancel'),
    # path('download/', views.download, name='download'),
    # path('test/', views.test, name='test'),
]
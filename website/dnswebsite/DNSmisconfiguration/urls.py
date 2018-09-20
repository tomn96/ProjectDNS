from django.urls import path

from . import views


app_name = 'DNSmisconfiguration'

urlpatterns = [
    path('', views.index, name='index'),
    path('csv', views.csv, name='csv'),
    path('address', views.address, name='address'),
    path('about', views.about, name='about'),
    path('upload_csv', views.upload_csv, name='upload_csv'),
    path('uploaded_csv/<csv_result>', views.uploaded_csv, name='uploaded_csv')
]

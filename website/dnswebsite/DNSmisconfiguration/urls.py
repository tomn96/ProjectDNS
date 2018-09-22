from django.urls import path

from . import views


app_name = 'DNSmisconfiguration'

urlpatterns = [
    path('', views.index, name='index'),
    path('csv_url', views.csv_url, name='csv_url'),
    path('address', views.address, name='address'),
    path('about', views.about, name='about'),
    path('upload_csv', views.upload_csv, name='upload_csv'),
    path('download_dict/<int:dict_id>/<int:option>', views.download_dict, name='download_dict')
]

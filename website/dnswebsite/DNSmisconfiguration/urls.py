from django.urls import path

from . import views


app_name = 'DNSmisconfiguration'

urlpatterns = [
    path('', views.index, name='index'),
    path('readme', views.readme, name='readme'),
    path('address', views.address, name='address'),
    path('csv_url', views.csv_url, name='csv_url'),
    path('upload_csv', views.upload_csv, name='upload_csv'),
    path('known_ns', views.known_ns, name='known_ns'),
    path('upload_known_ns', views.upload_known_ns, name='upload_known_ns'),
    path('download_dict/<int:dict_id>/<int:option>', views.download_dict, name='download_dict')
]

from django.urls import path

from . import views


app_name = 'DNSmisconfiguration'

urlpatterns = [
    path('', views.index, name='index'),
    path('readme', views.readme, name='readme'),
    path('address', views.address, name='address'),
    path('csv_url', views.csv_url, name='csv_url'),
    path('known_ns', views.known_ns, name='known_ns'),
    path('results/<int:dict_id>', views.results, name='results'),
    path('top500', views.top500, name='top500'),
    path('download_dict/<int:dict_id>/<int:option>', views.download_dict, name='download_dict'),
    path('download_results_servers', views.download_results_servers, name='download_results_servers'),
    path('download_results_records', views.download_results_records, name='download_results_records'),
    path('download_misconfigurations', views.download_misconfigurations, name='download_misconfigurations'),
    path('download_misconfigurations_count', views.download_misconfigurations_count, name='download_misconfigurations_count'),
    path('download_top500_results_servers', views.download_top500_results_servers, name='download_top500_results_servers'),
    path('download_top500_results_records', views.download_top500_results_records, name='download_top500_results_records'),
    path('download_top500_misconfigurations', views.download_top500_misconfigurations, name='download_top500_misconfigurations'),
    path('download_top500_misconfigurations_count', views.download_top500_misconfigurations_count, name='download_top500_misconfigurations_count')
]

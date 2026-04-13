from django.urls import path
from .views import (
    InstitucionListCreateView, InstitucionDetailView,
    SistemaListCreateView, SistemaDetailView, InstitucionPublicaListView, 
)

urlpatterns = [
    path('instituciones/',          InstitucionListCreateView.as_view(), name='institucion_list_create'),
    path('instituciones/<int:pk>/', InstitucionDetailView.as_view(),    name='institucion_detail'),

    path('sistemas/',          SistemaListCreateView.as_view(), name='sistema_list_create'),
    path('sistemas/<int:pk>/', SistemaDetailView.as_view(),    name='sistema_detail'), 
    path('instituciones/publicas/', InstitucionPublicaListView.as_view(), name='instituciones_publicas'),

]
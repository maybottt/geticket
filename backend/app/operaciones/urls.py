from django.urls import path
from .views import (
    AreaListCreateView, AreaDetailView,
    HorarioListCreateView, HorarioDetailView,
    CanalEntradaListCreateView, CanalEntradaDetailView,
    AgenteAreaListCreateView, AgenteAreaDetailView,
    AgenteHorarioListCreateView, AgenteHorarioDetailView,
)

urlpatterns = [
    # Áreas
    path('areas/',          AreaListCreateView.as_view(), name='area_list_create'),
    path('areas/<int:pk>/', AreaDetailView.as_view(),    name='area_detail'),

    # Horarios
    path('horarios/',          HorarioListCreateView.as_view(), name='horario_list_create'),
    path('horarios/<int:pk>/', HorarioDetailView.as_view(),    name='horario_detail'),

    # Canales de entrada
    path('canales/',          CanalEntradaListCreateView.as_view(), name='canal_list_create'),
    path('canales/<int:pk>/', CanalEntradaDetailView.as_view(),    name='canal_detail'),

    # Agente ↔ Área
    path('agente-areas/',          AgenteAreaListCreateView.as_view(), name='agente_area_list_create'),
    path('agente-areas/<int:pk>/', AgenteAreaDetailView.as_view(),    name='agente_area_detail'),

    # Agente ↔ Horario
    path('agente-horarios/',          AgenteHorarioListCreateView.as_view(), name='agente_horario_list_create'),
    path('agente-horarios/<int:pk>/', AgenteHorarioDetailView.as_view(),    name='agente_horario_detail'),
]
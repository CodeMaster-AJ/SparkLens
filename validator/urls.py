from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('report/<uuid:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('report/<uuid:pk>/pdf/', views.ReportPDFView.as_view(), name='report_pdf'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('health/', views.HealthView.as_view(), name='health'),
]

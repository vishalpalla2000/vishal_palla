from django.urls import path
from .views import CustomLoginView, welcome_view
from . import views


urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),  # Use CustomLoginView
    path('welcome/', welcome_view, name='welcome'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/update_manual_data/', views.update_manual_data, name='update_manual_data'),
    path('get_manual_data/', views.get_manual_data, name='get_manual_data'),
    path('get_snmp_ip_addresses/', views.get_snmp_ip_addresses, name='get_snmp_ip_addresses'),
    path('get_expirations/', views.get_expirations, name = 'get_expirations'),
    path('export_pdf/<int:selected_year>/', views.export_pdf, name='export_pdf'),
    path('report/', views.report, name='report'),
    path('logout/', views.logout_view, name='logout'),
    # Add a URL for the welcome page
    # Add other URLs for your app here if needed
]

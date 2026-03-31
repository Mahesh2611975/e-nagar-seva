from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # 🏠 HOME
    path('', views.home, name='home'),

    # 🔐 AUTH
    path('login/citizen/', views.citizen_login, name='citizen_login'),
    path('login/officer/', views.officer_login, name='officer_login'),

    path('signup/citizen/', views.citizen_signup, name='citizen_signup'),
    path('signup/officer/', views.officer_signup, name='officer_signup'),

    path('logout/', views.custom_logout, name='logout'),

    # 🔁 DASHBOARD REDIRECT
    path('dashboard/', views.dashboard_redirect, name='dashboard'),

    # 👤 CITIZEN DASHBOARD
    path('citizen/', views.citizen_dashboard, name='citizen_dashboard'),

    # 👮 STAFF DASHBOARD
    path('staff/', views.staff_dashboard, name='staff_dashboard'),

    # 📸 COMPLAINT
    path('complaint/', views.add_complaint, name='complaint'),

    # 🔄 UPDATE STATUS
    path('update/<int:id>/', views.update_status, name='update_status'),

    # 🔔 NOTIFICATIONS
    path('notifications/', views.notifications, name='notifications'),
]

# 🔥 MEDIA FILES
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
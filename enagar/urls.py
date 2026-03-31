from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('main.urls')),
    path('login/citizen/', views.citizen_login, name='citizen_login'),
    path('login/officer/', views.officer_login, name='officer_login'),

    path('signup/citizen/', views.citizen_signup, name='citizen_signup'),
    path('signup/officer/', views.officer_signup, name='officer_signup'),
    
    path('logout/', views.custom_logout, name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)